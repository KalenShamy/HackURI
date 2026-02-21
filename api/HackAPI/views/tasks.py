from rest_framework import viewsets

from ..models import Task
from ..serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer

    def get_queryset(self):
        qs = Task.objects.filter(workspace__members=self.request.user)
        workspace_id = self.request.query_params.get('workspace')
        if workspace_id:
            qs = qs.filter(workspace_id=workspace_id)
        return qs.select_related('assigned_to', 'workspace')
