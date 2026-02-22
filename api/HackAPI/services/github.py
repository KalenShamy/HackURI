import re
import logging
import requests

logger = logging.getLogger(__name__)

GITHUB_API = 'https://api.github.com'


def _github_headers(token):
    return {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
    }


def render_tasks_as_checkboxes(tasks):
    """Render a queryset of Tasks as GitHub-flavored markdown checkboxes."""
    lines = []
    for task in tasks.order_by('checkbox_index', 'created_at'):
        checked = 'x' if task.status == 'done' else ' '
        lines.append(f'- [{checked}] {task.title}')
    return '\n'.join(lines)


def parse_checkboxes_from_body(body):
    """Parse markdown checkboxes from a GitHub issue/PR body.

    Returns list of (title, is_checked) tuples.
    """
    if not body:
        return []
    pattern = r'^- \[([ xX])\] (.+)$'
    results = []
    for line in body.splitlines():
        match = re.match(pattern, line.strip())
        if match:
            is_checked = match.group(1).lower() == 'x'
            title = match.group(2).strip()
            results.append((title, is_checked))
    return results


def create_github_issue(workspace, feature):
    """Create a GitHub issue for a Feature. Updates feature with github fields."""
    if not workspace.github_token:
        logger.warning('No GitHub token on workspace %s, skipping issue creation', workspace.id)
        return None

    tasks = feature.tasks.all()
    body = ''
    if feature.description:
        body = feature.description + '\n\n'
    if tasks.exists():
        body += render_tasks_as_checkboxes(tasks)

    url = f'{GITHUB_API}/repos/{workspace.github_repo_owner}/{workspace.github_repo_name}/issues'
    resp = requests.post(
        url,
        json={'title': feature.name, 'body': body.strip()},
        headers=_github_headers(workspace.github_token),
        timeout=10,
    )

    if resp.status_code != 201:
        logger.error('Failed to create GitHub issue: %s %s', resp.status_code, resp.text)
        return None

    data = resp.json()
    feature.type = 'issue'
    feature.github_number = data['number']
    feature.github_id = data['id']
    feature.html_url = data.get('html_url', '')
    feature.state = 'open'
    feature.save(update_fields=['type', 'github_number', 'github_id', 'html_url', 'state'])

    # Assign checkbox indices to tasks
    for i, task in enumerate(tasks.order_by('created_at')):
        task.checkbox_index = i
        task.save(update_fields=['checkbox_index'])

    return data


def update_issue_body(workspace, feature):
    """Update the GitHub issue/PR body with current task checkboxes."""
    if not workspace.github_token or not feature.github_number:
        return None

    tasks = feature.tasks.all()
    body = ''
    if feature.description:
        body = feature.description + '\n\n'
    if tasks.exists():
        body += render_tasks_as_checkboxes(tasks)

    # Use issues endpoint for both issues and PRs (GitHub supports it for both)
    url = (
        f'{GITHUB_API}/repos/{workspace.github_repo_owner}/{workspace.github_repo_name}'
        f'/issues/{feature.github_number}'
    )
    resp = requests.patch(
        url,
        json={'body': body.strip()},
        headers=_github_headers(workspace.github_token),
        timeout=10,
    )

    if resp.status_code != 200:
        logger.error('Failed to update issue body: %s %s', resp.status_code, resp.text)
        return None

    return resp.json()


def sync_tasks_from_checkboxes(feature, checkboxes):
    """Sync tasks from parsed checkboxes. Returns (created, updated) counts.

    checkboxes: list of (title, is_checked) tuples from parse_checkboxes_from_body.
    """
    from ..models import Task

    existing_tasks = {t.title: t for t in feature.tasks.all()}
    created = 0
    updated = 0

    seen_titles = set()
    for i, (title, is_checked) in enumerate(checkboxes):
        seen_titles.add(title)
        new_status = Task.Status.DONE if is_checked else Task.Status.TODO

        if title in existing_tasks:
            task = existing_tasks[title]
            changed = False
            if task.checkbox_index != i:
                task.checkbox_index = i
                changed = True
            if is_checked and task.status != Task.Status.DONE:
                task.status = Task.Status.DONE
                changed = True
            elif not is_checked and task.status == Task.Status.DONE:
                task.status = Task.Status.TODO
                changed = True
            if changed:
                task.save(update_fields=['checkbox_index', 'status'])
                updated += 1
        else:
            Task.objects.create(
                feature=feature,
                title=title,
                status=new_status,
                checkbox_index=i,
            )
            created += 1

    return created, updated
