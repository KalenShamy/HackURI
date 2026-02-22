import traceback

from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Feature, Task, Workspace
from ..serializers import FeatureSerializer, TaskSerializer, WorkspaceSerializer
from ..services.gemini import generate_features_and_tasks, generate_features_from_repo
from ..services.github import create_github_issue, fetch_repo_summary, register_webhook, unregister_webhook


class WorkspaceViewSet(viewsets.ModelViewSet):
    serializer_class = WorkspaceSerializer

    def get_queryset(self):
        return Workspace.objects.filter(members=self.request.user.id)

    def _register_webhook(self, workspace):
        try:
            register_webhook(
                workspace,
                webhook_url=settings.GITHUB_WEBHOOK_URL,
                secret=settings.GITHUB_WEBHOOK_SECRET,
            )
        except Exception:
            print(f'[WARNING] Failed to register webhook for workspace {workspace.id}')
            traceback.print_exc()

    def _generate_from_repo(self, workspace):
        try:
            summary = fetch_repo_summary(workspace)
            if not summary:
                print(f'[INFO] Empty repo summary for workspace {workspace.id}, skipping AI generation')
                return

            raw = generate_features_from_repo(summary)
            if not raw:
                print(f'[INFO] Gemini returned no features for workspace {workspace.id}')
                return

            for feature_data in raw:
                feature = Feature.objects.create(
                    workspace=workspace,
                    name=feature_data.get('name', 'Untitled Feature'),
                    description=feature_data.get('description', ''),
                )
                for i, task_data in enumerate(feature_data.get('tasks', [])):
                    priority = task_data.get('priority', 'medium')
                    if priority not in ('low', 'medium', 'high'):
                        priority = 'medium'
                    Task.objects.create(
                        feature=feature,
                        title=task_data.get('title', 'Untitled Task'),
                        description=task_data.get('description', ''),
                        priority=priority,
                        checkbox_index=i,
                    )
                try:
                    create_github_issue(workspace, feature)
                except Exception:
                    print(f'[WARNING] Failed to create GitHub issue for auto-generated feature {feature.id}')
                    traceback.print_exc()
        except Exception:
            print(f'[WARNING] Auto-generation from repo failed for workspace {workspace.id} — workspace creation continues')
            traceback.print_exc()

    def perform_create(self, serializer):
        workspace = serializer.save(created_by=self.request.user)
        if self.request.user.id not in workspace.members:
            workspace.members.append(self.request.user.id)
        workspace.save()
        if workspace.github_repo_owner and workspace.github_repo_name:
            self._register_webhook(workspace)
            self._generate_from_repo(workspace)

    def perform_update(self, serializer):
        old = self.get_object()
        old_repo = (old.github_repo_owner, old.github_repo_name)
        workspace = serializer.save()
        new_repo = (workspace.github_repo_owner, workspace.github_repo_name)
        if new_repo != old_repo and workspace.github_repo_owner and workspace.github_repo_name:
            self._register_webhook(workspace)

    def perform_destroy(self, instance):
        try:
            unregister_webhook(instance)
        except Exception:
            print(f'[WARNING] Failed to unregister webhook for workspace {instance.id}')
            traceback.print_exc()
        instance.delete()

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

    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Generate features and tasks from a text description using Gemini.

        Request body: {"description": "..."}
        Returns the created features with their tasks.
        """
        description = request.data.get('description', '').strip()
        if not description:
            return Response({'error': 'description is required'}, status=status.HTTP_400_BAD_REQUEST)

        workspace = self.get_object()

        raw = generate_features_and_tasks(description)
        if not raw:
            return Response(
                {'error': 'Failed to generate features — check GEMINI_API_KEY or try again'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        created_features = []
        for feature_data in raw:
            feature = Feature.objects.create(
                workspace=workspace,
                name=feature_data.get('name', 'Untitled Feature'),
                description=feature_data.get('description', ''),
            )

            tasks = []
            for i, task_data in enumerate(feature_data.get('tasks', [])):
                priority = task_data.get('priority', 'medium')
                if priority not in ('low', 'medium', 'high'):
                    priority = 'medium'
                task = Task.objects.create(
                    feature=feature,
                    title=task_data.get('title', 'Untitled Task'),
                    description=task_data.get('description', ''),
                    priority=priority,
                    checkbox_index=i,
                )
                tasks.append(task)

            try:
                create_github_issue(workspace, feature)
            except Exception:
                print(f'[ERROR] Failed to create GitHub issue for generated feature {feature.id}')
                traceback.print_exc()

            feature_out = FeatureSerializer(feature).data
            feature_out['tasks'] = TaskSerializer(tasks, many=True).data
            created_features.append(feature_out)

        return Response(created_features, status=status.HTTP_201_CREATED)
