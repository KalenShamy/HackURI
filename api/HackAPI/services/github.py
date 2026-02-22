import base64
import re
import traceback
import requests

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
        print(f'[WARNING] No GitHub token on workspace {workspace.id}, skipping issue creation')
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
        print(f'[ERROR] Failed to create GitHub issue: {resp.status_code} {resp.text}')
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
        print(f'[ERROR] Failed to update issue body: {resp.status_code} {resp.text}')
        return None

    return resp.json()


def register_webhook(workspace, webhook_url, secret, token=None):
    """Register a GitHub webhook for the workspace repo. Stores webhook_id on the workspace.

    webhook_url: full public URL GitHub will POST to (e.g. 'https://yourserver.com/api/webhooks/github/')
    secret: GITHUB_WEBHOOK_SECRET value
    token: GitHub token to use; falls back to workspace.github_token
    """
    github_token = token or workspace.github_token
    if not github_token:
        print(f'[WARNING] No GitHub token for workspace {workspace.id}, skipping webhook registration')
        return None

    # Remove any existing webhook first to avoid duplicates
    if workspace.webhook_id:
        unregister_webhook(workspace, github_token)

    url = f'{GITHUB_API}/repos/{workspace.github_repo_owner}/{workspace.github_repo_name}/hooks'
    payload = {
        'name': 'web',
        'active': True,
        'events': [
            'push',
            'pull_request',
            'pull_request_review',
            'pull_request_review_comment',
            'issue_comment',
            'issues',
            'create',
            'delete',
            'label',
            'milestone',
        ],
        'config': {
            'url': webhook_url,
            'content_type': 'json',
            'secret': secret,
            'insecure_ssl': '0',
        },
    }
    resp = requests.post(url, json=payload, headers=_github_headers(github_token), timeout=10)

    if resp.status_code == 201:
        hook_id = str(resp.json().get('id', ''))
        workspace.webhook_id = hook_id
        workspace.save(update_fields=['webhook_id'])
        print(f'[INFO] Registered webhook {hook_id} for workspace {workspace.id}')
        return hook_id

    print(f'[ERROR] Failed to register webhook: {resp.status_code} {resp.text}')
    return None


def unregister_webhook(workspace, token=None):
    """Delete the GitHub webhook stored on the workspace."""
    if not workspace.webhook_id:
        return

    github_token = token or workspace.github_token
    if not github_token:
        return

    url = (
        f'{GITHUB_API}/repos/{workspace.github_repo_owner}/{workspace.github_repo_name}'
        f'/hooks/{workspace.webhook_id}'
    )
    resp = requests.delete(url, headers=_github_headers(github_token), timeout=10)

    if resp.status_code in (204, 404):
        workspace.webhook_id = ''
        workspace.save(update_fields=['webhook_id'])
        print(f'[INFO] Unregistered webhook for workspace {workspace.id}')
    else:
        print(f'[ERROR] Failed to delete webhook: {resp.status_code} {resp.text}')


_REPO_SUMMARY_README_LIMIT = 2000
_REPO_SUMMARY_LANG_LIMIT = 300
_REPO_SUMMARY_DEP_LIMIT = 500
_REPO_SUMMARY_DEP_FILES = ['package.json', 'requirements.txt', 'Cargo.toml', 'go.mod', 'pyproject.toml']


def fetch_repo_summary(workspace) -> str:
    """Fetch a condensed summary of the repo for use as Gemini context.

    Returns a concatenated string containing README, language stats, and the first
    matching dependency file. Returns an empty string if no content could be fetched.
    """
    if not workspace.github_token:
        print(f'[WARNING] No GitHub token on workspace {workspace.id}, skipping repo summary')
        return ''

    owner = workspace.github_repo_owner
    name = workspace.github_repo_name
    headers = _github_headers(workspace.github_token)
    parts = []

    try:
        resp = requests.get(
            f'{GITHUB_API}/repos/{owner}/{name}/readme',
            headers=headers,
            timeout=10,
        )
        if resp.status_code == 200:
            content = base64.b64decode(resp.json().get('content', '')).decode('utf-8', errors='replace')
            parts.append(f'## README\n{content[:_REPO_SUMMARY_README_LIMIT]}')
    except Exception:
        print(f'[WARNING] Failed to fetch README for {owner}/{name}')
        traceback.print_exc()

    try:
        resp = requests.get(
            f'{GITHUB_API}/repos/{owner}/{name}/languages',
            headers=headers,
            timeout=10,
        )
        if resp.status_code == 200:
            lang_str = ', '.join(f'{k}: {v}' for k, v in resp.json().items())
            parts.append(f'## Languages\n{lang_str[:_REPO_SUMMARY_LANG_LIMIT]}')
    except Exception:
        print(f'[WARNING] Failed to fetch languages for {owner}/{name}')
        traceback.print_exc()

    for dep_file in _REPO_SUMMARY_DEP_FILES:
        try:
            resp = requests.get(
                f'{GITHUB_API}/repos/{owner}/{name}/contents/{dep_file}',
                headers=headers,
                timeout=10,
            )
            if resp.status_code == 200:
                content = base64.b64decode(resp.json().get('content', '')).decode('utf-8', errors='replace')
                parts.append(f'## {dep_file}\n{content[:_REPO_SUMMARY_DEP_LIMIT]}')
                break
        except Exception:
            print(f'[WARNING] Failed to fetch {dep_file} for {owner}/{name}')
            traceback.print_exc()

    return '\n\n'.join(parts)


def sync_tasks_from_checkboxes(feature, checkboxes):
    """Sync tasks from parsed checkboxes. Returns (created, updated) counts.

    checkboxes: list of (title, is_checked) tuples from parse_checkboxes_from_body.
    """
    from ..models import Task

    all_tasks = list(feature.tasks.all())
    # Match by checkbox_index first (avoids duplicate-title ambiguity), fall back to title
    existing_by_index = {t.checkbox_index: t for t in all_tasks if t.checkbox_index is not None}
    existing_by_title = {t.title: t for t in all_tasks if t.checkbox_index is None}
    created = 0
    updated = 0

    seen_titles = set()
    for i, (title, is_checked) in enumerate(checkboxes):
        seen_titles.add(title)
        new_status = Task.Status.DONE if is_checked else Task.Status.TODO

        task = existing_by_index.get(i) or existing_by_title.get(title)
        if task is not None:
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
