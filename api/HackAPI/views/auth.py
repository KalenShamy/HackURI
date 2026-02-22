import json
import traceback
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


@api_view(['GET'])
@permission_classes([AllowAny])
def github_oauth_url(request):
    """Return the GitHub OAuth authorization URL for the desktop client."""
    url = (
        f'https://github.com/login/oauth/authorize'
        f'?client_id={settings.GITHUB_CLIENT_ID}'
        f'&scope=repo,read:user,user:email'
    )
    return Response({'url': url})


@api_view(['POST'])
@permission_classes([AllowAny])
def github_oauth_callback(request):
    """Exchange a GitHub OAuth code for an access token and create/login the user."""
    code = request.data.get('code')
    if not code:
        return Response({'error': 'Missing code'}, status=400)

    # Exchange code for GitHub access token
    token_response = requests.post(
        'https://github.com/login/oauth/access_token',
        data={
            'client_id': settings.GITHUB_CLIENT_ID,
            'client_secret': settings.GITHUB_CLIENT_SECRET,
            'code': code,
        },
        headers={'Accept': 'application/json'},
        timeout=10,
    )
    token_data = token_response.json()
    access_token = token_data.get('access_token')

    if not access_token:
        error = token_data.get('error', 'Unknown error')
        error_desc = token_data.get('error_description', '')
        print(f'[ERROR] GitHub OAuth failed: {error} - {error_desc}')
        return Response(
            {'error': 'Failed to get access token', 'details': f'{error}: {error_desc}'},
            status=400,
        )

    # Fetch GitHub user profile
    user_response = requests.get(
        'https://api.github.com/user',
        headers={'Authorization': f'Bearer {access_token}'},
        timeout=10,
    )
    github_user = user_response.json()

    if 'login' not in github_user:
        print(f'[ERROR] GitHub user API failed: {github_user}')
        return Response(
            {'error': 'Failed to fetch GitHub profile', 'details': github_user.get('message', 'unknown')},
            status=400,
        )

    # Create or get Django user
    try:
        user, _ = User.objects.get_or_create(
            username=github_user['login'],
            defaults={'email': github_user.get('email') or ''},
        )

        # Generate DRF token
        token, _ = Token.objects.get_or_create(user=user)
    except Exception:
        print('[ERROR] Failed to create/get user or token')
        traceback.print_exc()
        return Response({'error': 'Server error during user creation'}, status=500)

    return Response({
        'token': token.key,
        'user': {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'github_avatar': github_user.get('avatar_url', ''),
        },
        'github_token': access_token,
    })


@require_GET
def desktop_auth_callback(request):
    """GitHub OAuth callback for the desktop app.

    Receives the code from GitHub, exchanges it for tokens,
    then redirects to hivemind:// so the Electron app can handle it.
    """
    print(f'[AUTH] desktop_auth_callback hit, query params: {dict(request.GET)}', flush=True)

    code = request.GET.get('code')
    if not code:
        params = dict(request.GET)
        print(f'[AUTH] No code param. Params: {params}', flush=True)
        return HttpResponseBadRequest(
            f'Missing code parameter. Received query params: {params}'
        )

    print(f'[AUTH] Got code, exchanging with GitHub...', flush=True)

    # Exchange code for GitHub access token
    token_response = requests.post(
        'https://github.com/login/oauth/access_token',
        data={
            'client_id': settings.GITHUB_CLIENT_ID,
            'client_secret': settings.GITHUB_CLIENT_SECRET,
            'code': code,
        },
        headers={'Accept': 'application/json'},
        timeout=10,
    )
    token_data = token_response.json()
    print(f'[AUTH] Token exchange response: {token_data}', flush=True)
    access_token = token_data.get('access_token')

    if not access_token:
        error = token_data.get('error', 'Unknown error')
        error_desc = token_data.get('error_description', '')
        print(f'[AUTH] FAILED: {error} - {error_desc}', flush=True)
        print(f'[AUTH] Client ID used: {settings.GITHUB_CLIENT_ID[:8]}...', flush=True)
        msg = f'Failed to get access token: {error}'
        if error_desc:
            msg += f' ({error_desc})'
        return HttpResponseBadRequest(msg)

    print(f'[AUTH] Got access token, fetching GitHub user...', flush=True)

    # Fetch GitHub user profile
    try:
        user_response = requests.get(
            'https://api.github.com/user',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10,
        )
        github_user = user_response.json()
        print(f'[AUTH] GitHub user: {github_user.get("login", "MISSING")}', flush=True)

        if 'login' not in github_user:
            print(f'[AUTH] GitHub user API failed: {github_user}', flush=True)
            return HttpResponseBadRequest(f'GitHub API error: {github_user.get("message", "unknown")}')

        # Create or get Django user
        user, _ = User.objects.get_or_create(
            username=github_user['login'],
            defaults={'email': github_user.get('email') or ''},
        )

        # Generate DRF token
        token, _ = Token.objects.get_or_create(user=user)
        print(f'[AUTH] User + token created, redirecting...', flush=True)
    except Exception as e:
        print(f'[AUTH] EXCEPTION: {e}', flush=True)
        return HttpResponseBadRequest(f'Server error: {e}')

    # Redirect to the desktop app via custom protocol
    params = urlencode({
        'token': token.key,
        'github_token': access_token,
        'user': json.dumps({
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
        }),
    })
    redirect_url = f'hivemind://callback?{params}'

    # Return an HTML page that attempts the redirect client-side.
    # This is more reliable than a 302 for custom protocols.
    html = f"""<!DOCTYPE html>
<html>
<head><title>Redirecting to HiveMind...</title></head>
<body>
<p>Redirecting to HiveMind desktop app...</p>
<p>If nothing happens, <a href="{redirect_url}">click here</a>.</p>
<script>window.location.href = "{redirect_url}";</script>
</body>
</html>"""
    return HttpResponse(html, content_type='text/html')
