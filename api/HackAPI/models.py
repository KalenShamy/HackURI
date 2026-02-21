from django.db import models
from django.contrib.auth.models import User
from django_mongodb_backend.fields import ArrayField, ObjectIdField


class Workspace(models.Model):
    name = models.CharField(max_length=255)
    github_repo_url = models.URLField()
    github_repo_owner = models.CharField(max_length=255)
    github_repo_name = models.CharField(max_length=255)
    webhook_id = models.CharField(max_length=255, blank=True, default='')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_workspaces')
    members = ArrayField(ObjectIdField(), default=list, blank=True)
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

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks'
    )
    completed_by_commit = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
