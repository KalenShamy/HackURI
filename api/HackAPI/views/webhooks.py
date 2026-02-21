import hashlib
import hmac
import json

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..services.gemini import analyze_commits
from ..models import Task, Workspace


def verify_github_signature(request):
    """Verify the X-Hub-Signature-256 header from GitHub."""
    signature = request.META.get('HTTP_X_HUB_SIGNATURE_256', '')
    if not signature or not settings.GITHUB_WEBHOOK_SECRET:
        return False
    expected = 'sha256=' + hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode(),
        request.body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(signature, expected)


@api_view(['POST'])
@permission_classes([AllowAny])
def github_webhook(request):
    """Handle GitHub push webhook events — analyze commits with Gemini."""
    if not verify_github_signature(request):
        return Response({'error': 'Invalid signature'}, status=403)

    event = request.META.get('HTTP_X_GITHUB_EVENT', '')
    if event != 'push':
        return Response({'status': 'ignored'})

    payload = request.data
    repo_full_name = payload.get('repository', {}).get('full_name', '')
    commits = payload.get('commits', [])
    commit_messages = [c.get('message', '') for c in commits]

    if not commit_messages:
        return Response({'status': 'no commits'})

    # Find the workspace for this repo
    try:
        owner, name = repo_full_name.split('/')
        workspace = Workspace.objects.get(github_repo_owner=owner, github_repo_name=name)
    except (ValueError, Workspace.DoesNotExist):
        return Response({'status': 'no matching workspace'})

    # Get open tasks for context
    open_tasks = list(workspace.tasks.exclude(status=Task.Status.DONE).values_list('title', flat=True))

    if not open_tasks:
        return Response({'status': 'no open tasks'})

    # Ask Gemini which tasks were completed
    completed_titles = analyze_commits(commit_messages, open_tasks)

    # Mark matched tasks as done
    marked = []
    for title in completed_titles:
        updated = workspace.tasks.filter(title=title, status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS]).update(
            status=Task.Status.DONE,
            completed_by_commit=commits[0].get('id', '')[:12],
        )
        if updated:
            marked.append(title)

    return Response({'status': 'processed', 'completed_tasks': marked})
