from django.apps import AppConfig


class HackapiConfig(AppConfig):
    default_auto_field = 'django_mongodb_backend.fields.ObjectIdAutoField'
    name = 'HackAPI'
