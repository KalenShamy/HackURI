import django.db.models.deletion
import django_mongodb_backend.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HackAPI', '0003_task_github_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='GitHubLabel',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('github_id', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
                ('color', models.CharField(max_length=10)),
                ('description', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='labels', to='HackAPI.workspace')),
            ],
            options={
                'unique_together': {('workspace', 'github_id')},
            },
        ),
        migrations.CreateModel(
            name='GitHubMilestone',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('github_id', models.IntegerField()),
                ('number', models.IntegerField()),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, default='')),
                ('state', models.CharField(choices=[('open', 'Open'), ('closed', 'Closed')], default='open', max_length=10)),
                ('due_on', models.DateTimeField(blank=True, null=True)),
                ('html_url', models.URLField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='milestones', to='HackAPI.workspace')),
            ],
            options={
                'unique_together': {('workspace', 'github_id')},
            },
        ),
    ]
