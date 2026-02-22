import hashlib
import hmac
from datetime import datetime, timezone

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..services.gemini import analyze_commits
from ..services.github import parse_checkboxes_from_body, sync_tasks_from_checkboxes
from ..models import (
    Feature, Task, Workspace,
    Commit, GitHubLabel, GitHubMilestone,
    PullRequest, PRReview, PRComment,
)


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


def _get_workspace(payload):
    """Return the Workspace for this payload's repo, or None."""
    repo = payload.get('repository', {})
    owner = repo.get('owner', {}).get('login', '')
    name = repo.get('name', '')
    try:
        return Workspace.objects.get(github_repo_owner=owner, github_repo_name=name)
    except Workspace.DoesNotExist:
        return None


def _parse_dt(value):
    """Parse an ISO 8601 datetime string to a timezone-aware datetime, or return None."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None


# ── sub-handlers ──────────────────────────────────────────────────────────────

def handle_push(payload, workspace):
    commits = payload.get('commits', [])
    commit_messages = [c.get('message', '') for c in commits]
    branch = payload.get('ref', '').replace('refs/heads/', '')

    commits_stored = 0
    for c in commits:
        sha = c.get('id', '')
        if not sha:
            continue
        author = c.get('author', {})
        _, created = Commit.objects.get_or_create(
            sha=sha,
            defaults={
                'workspace': workspace,
                'message': c.get('message', ''),
                'author_login': author.get('username', ''),
                'author_name': author.get('name', ''),
                'author_email': author.get('email', ''),
                'url': c.get('url', ''),
                'branch': branch,
                'added_files': c.get('added', []),
                'modified_files': c.get('modified', []),
                'removed_files': c.get('removed', []),
                'github_timestamp': _parse_dt(c.get('timestamp')),
            },
        )
        if created:
            commits_stored += 1

    if not commit_messages:
        return {'commits_stored': commits_stored, 'completed_tasks': []}

    open_tasks = list(
        Task.objects.filter(feature__workspace=workspace)
        .exclude(status=Task.Status.DONE)
        .values_list('title', flat=True)
    )

    if not open_tasks:
        return {'commits_stored': commits_stored, 'completed_tasks': []}

    completed_titles = analyze_commits(commit_messages, open_tasks)

    marked = []
    first_sha = commits[0].get('id', '')[:12] if commits else ''
    for title in completed_titles:
        updated = (
            Task.objects.filter(
                feature__workspace=workspace,
                title=title,
                status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS],
            ).update(status=Task.Status.DONE, completed_by_commit=first_sha)
        )
        if updated:
            marked.append(title)

    return {'commits_stored': commits_stored, 'completed_tasks': marked}


def handle_pull_request(payload, workspace):
    action = payload.get('action', '')
    pr_data = payload.get('pull_request', {})
    github_id = pr_data.get('id')
    pr_number = pr_data.get('number', 0)

    state = PullRequest.State.MERGED if pr_data.get('merged') else pr_data.get('state', 'open')

    # Sync labels
    label_ids = []
    for label in pr_data.get('labels', []):
        GitHubLabel.objects.update_or_create(
            workspace=workspace,
            github_id=label['id'],
            defaults={
                'name': label.get('name', ''),
                'color': label.get('color', ''),
                'description': label.get('description', ''),
            },
        )
        label_ids.append(label['id'])

    # Resolve milestone FK
    milestone = None
    ms_data = pr_data.get('milestone')
    if ms_data:
        milestone, _ = GitHubMilestone.objects.get_or_create(
            workspace=workspace,
            github_id=ms_data['id'],
            defaults={
                'number': ms_data.get('number', 0),
                'title': ms_data.get('title', ''),
                'description': ms_data.get('description', ''),
                'state': ms_data.get('state', 'open'),
                'due_on': _parse_dt(ms_data.get('due_on')),
                'html_url': ms_data.get('html_url', ''),
            },
        )

    requested_reviewers = [r['login'] for r in pr_data.get('requested_reviewers', []) if r.get('login')]

    pr, _ = PullRequest.objects.update_or_create(
        workspace=workspace,
        github_id=github_id,
        defaults={
            'number': pr_number,
            'title': pr_data.get('title', ''),
            'body': pr_data.get('body', '') or '',
            'state': state,
            'html_url': pr_data.get('html_url', ''),
            'diff_url': pr_data.get('diff_url', ''),
            'author_login': pr_data.get('user', {}).get('login', ''),
            'author_avatar_url': pr_data.get('user', {}).get('avatar_url', ''),
            'head_ref': pr_data.get('head', {}).get('ref', ''),
            'head_sha': pr_data.get('head', {}).get('sha', ''),
            'base_ref': pr_data.get('base', {}).get('ref', ''),
            'base_sha': pr_data.get('base', {}).get('sha', ''),
            'requested_reviewers': requested_reviewers,
            'label_ids': label_ids,
            'merged_at': _parse_dt(pr_data.get('merged_at')),
            'merge_commit_sha': pr_data.get('merge_commit_sha', '') or '',
            'commits_count': pr_data.get('commits', 0) or 0,
            'additions': pr_data.get('additions', 0) or 0,
            'deletions': pr_data.get('deletions', 0) or 0,
            'changed_files': pr_data.get('changed_files', 0) or 0,
            'github_created_at': _parse_dt(pr_data.get('created_at')),
            'github_updated_at': _parse_dt(pr_data.get('updated_at')),
            'github_closed_at': _parse_dt(pr_data.get('closed_at')),
            'milestone': milestone,
        },
    )

    # Create/sync Feature for this PR
    pr_body = pr_data.get('body', '') or ''
    feature_state = Feature.State.CLOSED if state in ('closed', 'merged') else Feature.State.OPEN

    if action == 'opened':
        feature, _ = Feature.objects.get_or_create(
            workspace=workspace,
            github_id=github_id,
            defaults={
                'name': pr_data.get('title', ''),
                'description': pr_body,
                'type': Feature.Type.PULL_REQUEST,
                'github_number': pr_number,
                'html_url': pr_data.get('html_url', ''),
                'state': feature_state,
            },
        )
        checkboxes = parse_checkboxes_from_body(pr_body)
        if checkboxes:
            sync_tasks_from_checkboxes(feature, checkboxes)

    elif action == 'edited':
        try:
            feature = Feature.objects.get(workspace=workspace, github_id=github_id)
            feature.name = pr_data.get('title', feature.name)
            feature.description = pr_body
            feature.save(update_fields=['name', 'description'])
            checkboxes = parse_checkboxes_from_body(pr_body)
            sync_tasks_from_checkboxes(feature, checkboxes)
        except Feature.DoesNotExist:
            pass

    elif action == 'closed':
        Feature.objects.filter(workspace=workspace, github_id=github_id).update(state=Feature.State.CLOSED)

        # On merge, auto-complete linked tasks via Gemini
        if pr_data.get('merged'):
            pr_context = [f"{pr.title}\n{pr.body}"]
            open_tasks = list(
                Task.objects.filter(feature__workspace=workspace)
                .exclude(status=Task.Status.DONE)
                .values_list('title', flat=True)
            )
            if open_tasks:
                completed_titles = analyze_commits(pr_context, open_tasks)
                for title in completed_titles:
                    Task.objects.filter(
                        feature__workspace=workspace,
                        title=title,
                        status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS],
                    ).update(status=Task.Status.DONE, completed_by_commit=pr.head_sha[:12])

    elif action == 'reopened':
        Feature.objects.filter(workspace=workspace, github_id=github_id).update(state=Feature.State.OPEN)

    return {'pr_number': pr.number, 'action': action, 'state': state}


def handle_pull_request_review(payload, workspace):
    review_data = payload.get('review', {})
    pr_github_id = payload.get('pull_request', {}).get('id')

    try:
        pr = PullRequest.objects.get(workspace=workspace, github_id=pr_github_id)
    except PullRequest.DoesNotExist:
        return {'status': 'pr_not_found'}

    state_map = {
        'approved': PRReview.State.APPROVED,
        'changes_requested': PRReview.State.CHANGES_REQUESTED,
        'commented': PRReview.State.COMMENTED,
        'dismissed': PRReview.State.DISMISSED,
    }
    state = state_map.get(review_data.get('state', '').lower(), PRReview.State.PENDING)

    PRReview.objects.update_or_create(
        pull_request=pr,
        github_id=review_data['id'],
        defaults={
            'reviewer_login': review_data.get('user', {}).get('login', ''),
            'reviewer_avatar_url': review_data.get('user', {}).get('avatar_url', ''),
            'state': state,
            'body': review_data.get('body', '') or '',
            'html_url': review_data.get('html_url', ''),
            'commit_sha': review_data.get('commit_id', ''),
            'github_submitted_at': _parse_dt(review_data.get('submitted_at')),
        },
    )

    return {'review_id': review_data['id'], 'state': state}


def handle_pull_request_review_comment(payload, workspace):
    action = payload.get('action', '')
    comment_data = payload.get('comment', {})
    pr_github_id = payload.get('pull_request', {}).get('id')

    try:
        pr = PullRequest.objects.get(workspace=workspace, github_id=pr_github_id)
    except PullRequest.DoesNotExist:
        return {'status': 'pr_not_found'}

    if action == 'deleted':
        PRComment.objects.filter(
            pull_request=pr,
            github_id=comment_data['id'],
            comment_type=PRComment.CommentType.REVIEW,
        ).delete()
        return {'comment_id': comment_data['id'], 'action': 'deleted'}

    # Resolve review FK if present
    review = None
    review_id = comment_data.get('pull_request_review_id')
    if review_id:
        review = PRReview.objects.filter(pull_request=pr, github_id=review_id).first()

    PRComment.objects.update_or_create(
        pull_request=pr,
        github_id=comment_data['id'],
        comment_type=PRComment.CommentType.REVIEW,
        defaults={
            'review': review,
            'author_login': comment_data.get('user', {}).get('login', ''),
            'author_avatar_url': comment_data.get('user', {}).get('avatar_url', ''),
            'body': comment_data.get('body', ''),
            'html_url': comment_data.get('html_url', ''),
            'diff_hunk': comment_data.get('diff_hunk', ''),
            'path': comment_data.get('path', ''),
            'position': comment_data.get('position'),
            'commit_sha': comment_data.get('commit_id', ''),
            'github_created_at': _parse_dt(comment_data.get('created_at')),
            'github_updated_at': _parse_dt(comment_data.get('updated_at')),
        },
    )

    return {'comment_id': comment_data['id'], 'action': action}


def handle_issue_comment(payload, workspace):
    action = payload.get('action', '')
    issue = payload.get('issue', {})
    comment_data = payload.get('comment', {})

    # Only process comments on pull requests
    if not issue.get('pull_request'):
        return {'status': 'ignored_issue_comment'}

    try:
        pr = PullRequest.objects.get(workspace=workspace, number=issue['number'])
    except PullRequest.DoesNotExist:
        return {'status': 'pr_not_found'}

    if action == 'deleted':
        PRComment.objects.filter(
            pull_request=pr,
            github_id=comment_data['id'],
            comment_type=PRComment.CommentType.ISSUE,
        ).delete()
        return {'comment_id': comment_data['id'], 'action': 'deleted'}

    PRComment.objects.update_or_create(
        pull_request=pr,
        github_id=comment_data['id'],
        comment_type=PRComment.CommentType.ISSUE,
        defaults={
            'author_login': comment_data.get('user', {}).get('login', ''),
            'author_avatar_url': comment_data.get('user', {}).get('avatar_url', ''),
            'body': comment_data.get('body', ''),
            'html_url': comment_data.get('html_url', ''),
            'github_created_at': _parse_dt(comment_data.get('created_at')),
            'github_updated_at': _parse_dt(comment_data.get('updated_at')),
        },
    )

    return {'comment_id': comment_data['id'], 'action': action}


def handle_issues(payload, workspace):
    action = payload.get('action', '')
    issue = payload.get('issue', {})
    issue_number = issue.get('number')
    github_id = issue.get('id')

    if action == 'opened':
        # Create a Feature for this issue if one doesn't exist
        feature, created = Feature.objects.get_or_create(
            workspace=workspace,
            github_id=github_id,
            defaults={
                'name': issue.get('title', ''),
                'description': issue.get('body', '') or '',
                'type': Feature.Type.ISSUE,
                'github_number': issue_number,
                'html_url': issue.get('html_url', ''),
                'state': Feature.State.OPEN,
            },
        )
        if created:
            checkboxes = parse_checkboxes_from_body(issue.get('body', ''))
            if checkboxes:
                sync_tasks_from_checkboxes(feature, checkboxes)

    elif action == 'edited':
        try:
            feature = Feature.objects.get(workspace=workspace, github_number=issue_number, type=Feature.Type.ISSUE)
        except Feature.DoesNotExist:
            return {'issue_number': issue_number, 'action': action, 'status': 'feature_not_found'}
        feature.name = issue.get('title', feature.name)
        feature.description = issue.get('body', '') or ''
        feature.save(update_fields=['name', 'description'])
        checkboxes = parse_checkboxes_from_body(issue.get('body', ''))
        sync_tasks_from_checkboxes(feature, checkboxes)

    elif action == 'closed':
        Feature.objects.filter(
            workspace=workspace, github_number=issue_number, type=Feature.Type.ISSUE,
        ).update(state=Feature.State.CLOSED)
        # Also mark all tasks as done
        Task.objects.filter(
            feature__workspace=workspace,
            feature__github_number=issue_number,
            feature__type=Feature.Type.ISSUE,
        ).exclude(status=Task.Status.DONE).update(status=Task.Status.DONE)

    elif action == 'reopened':
        Feature.objects.filter(
            workspace=workspace, github_number=issue_number, type=Feature.Type.ISSUE,
        ).update(state=Feature.State.OPEN)

    return {'issue_number': issue_number, 'action': action}


def handle_create(payload, workspace):
    return {'ref_type': payload.get('ref_type', ''), 'ref': payload.get('ref', '')}


def handle_delete(payload, workspace):
    return {'ref_type': payload.get('ref_type', ''), 'ref': payload.get('ref', '')}


def handle_label(payload, workspace):
    action = payload.get('action', '')
    label_data = payload.get('label', {})

    if action == 'deleted':
        GitHubLabel.objects.filter(workspace=workspace, github_id=label_data['id']).delete()
    else:
        GitHubLabel.objects.update_or_create(
            workspace=workspace,
            github_id=label_data['id'],
            defaults={
                'name': label_data.get('name', ''),
                'color': label_data.get('color', ''),
                'description': label_data.get('description', ''),
            },
        )

    return {'label_id': label_data.get('id'), 'action': action}


def handle_milestone(payload, workspace):
    action = payload.get('action', '')
    ms_data = payload.get('milestone', {})

    if action == 'deleted':
        GitHubMilestone.objects.filter(workspace=workspace, github_id=ms_data['id']).delete()
    else:
        GitHubMilestone.objects.update_or_create(
            workspace=workspace,
            github_id=ms_data['id'],
            defaults={
                'number': ms_data.get('number', 0),
                'title': ms_data.get('title', ''),
                'description': ms_data.get('description', '') or '',
                'state': ms_data.get('state', 'open'),
                'due_on': _parse_dt(ms_data.get('due_on')),
                'html_url': ms_data.get('html_url', ''),
            },
        )

    return {'milestone_id': ms_data.get('id'), 'action': action}


# ── main endpoint ─────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def github_webhook(request):
    """Handle GitHub webhook events — dispatch to per-event handlers."""
    if not verify_github_signature(request):
        return Response({'error': 'Invalid signature'}, status=403)

    event = request.META.get('HTTP_X_GITHUB_EVENT', '')
    payload = request.data

    workspace = _get_workspace(payload)
    if workspace is None:
        return Response({'status': 'no matching workspace'})

    handlers = {
        'push': handle_push,
        'pull_request': handle_pull_request,
        'pull_request_review': handle_pull_request_review,
        'pull_request_review_comment': handle_pull_request_review_comment,
        'issue_comment': handle_issue_comment,
        'issues': handle_issues,
        'create': handle_create,
        'delete': handle_delete,
        'label': handle_label,
        'milestone': handle_milestone,
    }

    handler = handlers.get(event)
    if handler is None:
        return Response({'status': 'ignored'})

    result = handler(payload, workspace)
    return Response({'status': 'processed', **result})
