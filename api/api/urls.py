import os

from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include

from HackAPI.views import desktop_auth_callback

APP_VERSION = os.getenv('APP_VERSION', '0.0.0-dev')
APP_COMMIT = os.getenv('APP_COMMIT', os.getenv('GITHUB_SHA', 'local'))[:12]


def health_check(request):
    return JsonResponse(
        {
            'status': 'ok',
            'build': f'{APP_VERSION}+{APP_COMMIT}',
            'version': APP_VERSION,
            'commit': APP_COMMIT,
        }
    )


urlpatterns = [
    path('health', health_check),
    path('admin/', admin.site.urls),
    path('api/', include('HackAPI.urls')),
    path('auth', desktop_auth_callback, name='desktop-auth-callback'),
]
