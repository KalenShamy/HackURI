from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TaskViewSet,
    WorkspaceViewSet,
    github_oauth_url,
    github_oauth_callback,
    github_webhook,
    slack_events,
)

router = DefaultRouter()
router.register('workspaces', WorkspaceViewSet, basename='workspace')
router.register('tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/github/', github_oauth_url, name='github-oauth-url'),
    path('auth/github/callback/', github_oauth_callback, name='github-oauth-callback'),
    path('webhooks/github/', github_webhook, name='github-webhook'),
    path('webhooks/slack/', slack_events, name='slack-events'),
]
