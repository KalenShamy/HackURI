import requests
from django.conf import settings
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
        json={
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
        return Response({'error': 'Failed to get access token'}, status=400)

    # Fetch GitHub user profile
    user_response = requests.get(
        'https://api.github.com/user',
        headers={'Authorization': f'Bearer {access_token}'},
        timeout=10,
    )
    github_user = user_response.json()

    # Create or get Django user
    user, _ = User.objects.get_or_create(
        username=github_user['login'],
        defaults={'email': github_user.get('email', '')},
    )

    # Generate DRF token
    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'github_avatar': github_user.get('avatar_url', ''),
        },
        'github_token': access_token,
    })
