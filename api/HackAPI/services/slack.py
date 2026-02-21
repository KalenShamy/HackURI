from slack_sdk import WebClient
from django.conf import settings


def get_slack_client() -> WebClient | None:
    """Return a configured Slack WebClient, or None if not configured."""
    if not settings.SLACK_BOT_TOKEN:
        return None
    return WebClient(token=settings.SLACK_BOT_TOKEN)


def notify_task_completed(channel: str, task_title: str, commit_sha: str, repo: str):
    """Send a Slack message notifying that a task was auto-completed by a commit."""
    client = get_slack_client()
    if not client:
        return

    client.chat_postMessage(
        channel=channel,
        text=f"Task *{task_title}* was automatically marked complete by commit `{commit_sha}` in `{repo}`.",
    )


def notify_task_created(channel: str, task_title: str, workspace_name: str):
    """Send a Slack message when a new task is created."""
    client = get_slack_client()
    if not client:
        return

    client.chat_postMessage(
        channel=channel,
        text=f"New task created in *{workspace_name}*: {task_title}",
    )
