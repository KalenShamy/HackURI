from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include

from HackAPI.views import desktop_auth_callback

BUILD_VERSION = 'v2-debug-2026-02-22'


def health_check(request):
    return JsonResponse({'status': 'ok', 'build': BUILD_VERSION})


urlpatterns = [
    path('health', health_check),
    path('admin/', admin.site.urls),
    path('api/', include('HackAPI.urls')),
    path('auth', desktop_auth_callback, name='desktop-auth-callback'),
]
