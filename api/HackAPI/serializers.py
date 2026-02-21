from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Workspace, Task


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assigned_to', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            'id', 'workspace', 'title', 'description', 'status', 'priority',
            'assigned_to', 'assigned_to_id', 'completed_by_commit',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'completed_by_commit', 'created_at', 'updated_at']


class WorkspaceSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    members = serializers.SerializerMethodField()

    def get_members(self, obj):
        users = User.objects.filter(pk__in=obj.members)
        return UserSerializer(users, many=True).data
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = [
            'id', 'name', 'github_repo_url', 'github_repo_owner', 'github_repo_name',
            'created_by', 'members', 'task_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'webhook_id', 'created_at', 'updated_at']

    def get_task_count(self, obj):
        return obj.tasks.count()
