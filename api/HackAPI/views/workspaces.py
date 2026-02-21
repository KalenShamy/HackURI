from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Workspace
from ..serializers import WorkspaceSerializer


class WorkspaceViewSet(viewsets.ModelViewSet):
    serializer_class = WorkspaceSerializer

    def get_queryset(self):
        return Workspace.objects.filter(members=self.request.user.id)

    def perform_create(self, serializer):
        workspace = serializer.save(created_by=self.request.user)
        workspace.members.append(self.request.user.id)
        workspace.save()

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        workspace = self.get_object()
        if request.user.id not in workspace.members:
            workspace.members.append(request.user.id)
            workspace.save()
        return Response({'status': 'joined'})

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        workspace = self.get_object()
        if request.user.id in workspace.members:
            workspace.members.remove(request.user.id)
            workspace.save()
        return Response({'status': 'left'})
