import logging

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Feature, Task
from ..serializers import FeatureSerializer, TaskSerializer
from ..services.github import create_github_issue, update_issue_body

logger = logging.getLogger(__name__)


class FeatureViewSet(viewsets.ModelViewSet):
    serializer_class = FeatureSerializer

    def get_queryset(self):
        qs = Feature.objects.filter(workspace__members=self.request.user.id)
        workspace_id = self.request.query_params.get('workspace')
        if workspace_id:
            qs = qs.filter(workspace_id=workspace_id)
        return qs.select_related('workspace')

    def perform_create(self, serializer):
        feature = serializer.save()
        # Auto-create a GitHub issue for this feature
        try:
            create_github_issue(feature.workspace, feature)
        except Exception:
            logger.exception('Failed to create GitHub issue for feature %s', feature.id)

    @action(detail=True, methods=['post'])
    def sync_to_github(self, request, pk=None):
        """Force-push current tasks as checkboxes to GitHub."""
        feature = self.get_object()
        result = update_issue_body(feature.workspace, feature)
        if result is None:
            return Response({'status': 'failed'}, status=400)
        return Response({'status': 'synced'})


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer

    def get_queryset(self):
        qs = Task.objects.filter(feature__workspace__members=self.request.user.id)
        feature_id = self.request.query_params.get('feature')
        if feature_id:
            qs = qs.filter(feature_id=feature_id)
        workspace_id = self.request.query_params.get('workspace')
        if workspace_id:
            qs = qs.filter(feature__workspace_id=workspace_id)
        return qs.select_related('assigned_to', 'feature__workspace')

    def _sync_feature_to_github(self, task):
        """Sync the parent feature's checkboxes to GitHub after task changes."""
        if task.feature and task.feature.github_number:
            try:
                update_issue_body(task.feature.workspace, task.feature)
            except Exception:
                logger.exception('Failed to sync feature %s to GitHub', task.feature.id)

    def perform_create(self, serializer):
        task = serializer.save()
        # Assign checkbox index
        if task.feature:
            max_idx = task.feature.tasks.exclude(pk=task.pk).filter(
                checkbox_index__isnull=False
            ).order_by('-checkbox_index').values_list('checkbox_index', flat=True).first()
            task.checkbox_index = (max_idx or 0) + 1 if max_idx is not None else 0
            task.save(update_fields=['checkbox_index'])
        self._sync_feature_to_github(task)

    def perform_update(self, serializer):
        task = serializer.save()
        self._sync_feature_to_github(task)

    def perform_destroy(self, instance):
        feature = instance.feature
        instance.delete()
        if feature and feature.github_number:
            try:
                update_issue_body(feature.workspace, feature)
            except Exception:
                logger.exception('Failed to sync feature %s to GitHub', feature.id)
