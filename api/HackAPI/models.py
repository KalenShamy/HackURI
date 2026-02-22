from django.db import models
from django.contrib.auth.models import User
from django_mongodb_backend.fields import ArrayField, ObjectIdField


class Workspace(models.Model):
    name = models.CharField(max_length=255)
    github_repo_url = models.URLField()
    github_repo_owner = models.CharField(max_length=255)
    github_repo_name = models.CharField(max_length=255)
    webhook_id = models.CharField(max_length=255, blank=True, default='')
    github_token = models.CharField(max_length=255, blank=True, default='')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_workspaces')
    members = ArrayField(ObjectIdField(), default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Feature(models.Model):
    class Type(models.TextChoices):
        ISSUE = 'issue', 'Issue'
        PULL_REQUEST = 'pull_request', 'Pull Request'
        LOCAL = 'local', 'Local'

    class State(models.TextChoices):
        OPEN = 'open', 'Open'
        CLOSED = 'closed', 'Closed'

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='features')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.LOCAL)
    github_number = models.IntegerField(null=True, blank=True)
    github_id = models.BigIntegerField(null=True, blank=True)
    html_url = models.URLField(blank=True, default='')
    state = models.CharField(max_length=10, choices=State.choices, default=State.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = 'todo', 'To Do'
        IN_PROGRESS = 'in_progress', 'In Progress'
        DONE = 'done', 'Done'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'

    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks'
    )
    completed_by_commit = models.CharField(max_length=255, blank=True, default='')
    checkbox_index = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class GitHubLabel(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='labels')
    github_id = models.IntegerField()
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=10)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('workspace', 'github_id')]

    def __str__(self):
        return self.name


class GitHubMilestone(models.Model):
    class State(models.TextChoices):
        OPEN = 'open', 'Open'
        CLOSED = 'closed', 'Closed'

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='milestones')
    github_id = models.IntegerField()
    number = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    state = models.CharField(max_length=10, choices=State.choices, default=State.OPEN)
    due_on = models.DateTimeField(null=True, blank=True)
    html_url = models.URLField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('workspace', 'github_id')]

    def __str__(self):
        return self.title


class PullRequest(models.Model):
    class State(models.TextChoices):
        OPEN = 'open', 'Open'
        CLOSED = 'closed', 'Closed'
        MERGED = 'merged', 'Merged'

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='pull_requests')
    task = models.ForeignKey(
        Task, on_delete=models.SET_NULL, null=True, blank=True, related_name='pull_requests'
    )
    milestone = models.ForeignKey(
        GitHubMilestone, on_delete=models.SET_NULL, null=True, blank=True, related_name='pull_requests'
    )

    github_id = models.IntegerField()
    number = models.IntegerField()
    title = models.CharField(max_length=500)
    body = models.TextField(blank=True, default='')
    state = models.CharField(max_length=10, choices=State.choices, default=State.OPEN)
    html_url = models.URLField(blank=True, default='')
    diff_url = models.URLField(blank=True, default='')

    author_login = models.CharField(max_length=255)
    author_avatar_url = models.URLField(blank=True, default='')

    head_ref = models.CharField(max_length=255)
    head_sha = models.CharField(max_length=40)
    base_ref = models.CharField(max_length=255)
    base_sha = models.CharField(max_length=40)

    requested_reviewers = ArrayField(models.CharField(max_length=255), default=list, blank=True)
    label_ids = ArrayField(models.IntegerField(), default=list, blank=True)

    merged_at = models.DateTimeField(null=True, blank=True)
    merge_commit_sha = models.CharField(max_length=40, blank=True, default='')

    commits_count = models.IntegerField(default=0)
    additions = models.IntegerField(default=0)
    deletions = models.IntegerField(default=0)
    changed_files = models.IntegerField(default=0)

    github_created_at = models.DateTimeField(null=True, blank=True)
    github_updated_at = models.DateTimeField(null=True, blank=True)
    github_closed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('workspace', 'github_id')]

    def __str__(self):
        return f'PR #{self.number}: {self.title}'


class Commit(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='commits')
    pull_request = models.ForeignKey(
        PullRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='commits'
    )

    sha = models.CharField(max_length=40, unique=True)
    message = models.TextField()
    author_login = models.CharField(max_length=255, blank=True, default='')
    author_name = models.CharField(max_length=255, blank=True, default='')
    author_email = models.CharField(max_length=255, blank=True, default='')
    url = models.URLField(blank=True, default='')
    branch = models.CharField(max_length=255, blank=True, default='')

    added_files = ArrayField(models.CharField(max_length=500), default=list, blank=True)
    modified_files = ArrayField(models.CharField(max_length=500), default=list, blank=True)
    removed_files = ArrayField(models.CharField(max_length=500), default=list, blank=True)

    github_timestamp = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sha[:12]


class PRReview(models.Model):
    class State(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        CHANGES_REQUESTED = 'changes_requested', 'Changes Requested'
        COMMENTED = 'commented', 'Commented'
        DISMISSED = 'dismissed', 'Dismissed'

    pull_request = models.ForeignKey(PullRequest, on_delete=models.CASCADE, related_name='reviews')

    github_id = models.IntegerField()
    reviewer_login = models.CharField(max_length=255)
    reviewer_avatar_url = models.URLField(blank=True, default='')
    state = models.CharField(max_length=20, choices=State.choices, default=State.PENDING)
    body = models.TextField(blank=True, default='')
    html_url = models.URLField(blank=True, default='')
    commit_sha = models.CharField(max_length=40, blank=True, default='')

    github_submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('pull_request', 'github_id')]

    def __str__(self):
        return f'Review {self.github_id} on PR {self.pull_request_id}'


class PRComment(models.Model):
    class CommentType(models.TextChoices):
        ISSUE = 'issue', 'Issue Comment'
        REVIEW = 'review', 'Review Comment'

    pull_request = models.ForeignKey(PullRequest, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(
        PRReview, on_delete=models.SET_NULL, null=True, blank=True, related_name='comments'
    )

    github_id = models.IntegerField()
    comment_type = models.CharField(max_length=10, choices=CommentType.choices, default=CommentType.ISSUE)
    author_login = models.CharField(max_length=255)
    author_avatar_url = models.URLField(blank=True, default='')
    body = models.TextField()
    html_url = models.URLField(blank=True, default='')

    diff_hunk = models.TextField(blank=True, default='')
    path = models.CharField(max_length=500, blank=True, default='')
    position = models.IntegerField(null=True, blank=True)
    commit_sha = models.CharField(max_length=40, blank=True, default='')

    github_created_at = models.DateTimeField(null=True, blank=True)
    github_updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('pull_request', 'github_id', 'comment_type')]

    def __str__(self):
        return f'{self.comment_type} comment {self.github_id}'
