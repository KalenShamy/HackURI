from django.contrib import admin

from .models import Workspace, Task

admin.site.register(Workspace)
admin.site.register(Task)
