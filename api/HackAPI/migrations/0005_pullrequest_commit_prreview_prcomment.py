import django.db.models.deletion
import django_mongodb_backend.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HackAPI', '0004_githubbabel_githubmilestone'),
    ]

    operations = [
        migrations.CreateModel(
            name='PullRequest',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('github_id', models.IntegerField()),
                ('number', models.IntegerField()),
                ('title', models.CharField(max_length=500)),
                ('body', models.TextField(blank=True, default='')),
                ('state', models.CharField(choices=[('open', 'Open'), ('closed', 'Closed'), ('merged', 'Merged')], default='open', max_length=10)),
                ('html_url', models.URLField(blank=True, default='')),
                ('diff_url', models.URLField(blank=True, default='')),
                ('author_login', models.CharField(max_length=255)),
                ('author_avatar_url', models.URLField(blank=True, default='')),
                ('head_ref', models.CharField(max_length=255)),
                ('head_sha', models.CharField(max_length=40)),
                ('base_ref', models.CharField(max_length=255)),
                ('base_sha', models.CharField(max_length=40)),
                ('requested_reviewers', django_mongodb_backend.fields.ArrayField(base_field=models.CharField(max_length=255), blank=True, default=list)),
                ('label_ids', django_mongodb_backend.fields.ArrayField(base_field=models.IntegerField(), blank=True, default=list)),
                ('merged_at', models.DateTimeField(blank=True, null=True)),
                ('merge_commit_sha', models.CharField(blank=True, default='', max_length=40)),
                ('commits_count', models.IntegerField(default=0)),
                ('additions', models.IntegerField(default=0)),
                ('deletions', models.IntegerField(default=0)),
                ('changed_files', models.IntegerField(default=0)),
                ('github_created_at', models.DateTimeField(blank=True, null=True)),
                ('github_updated_at', models.DateTimeField(blank=True, null=True)),
                ('github_closed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pull_requests', to='HackAPI.workspace')),
                ('task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pull_requests', to='HackAPI.task')),
                ('milestone', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pull_requests', to='HackAPI.githubmilestone')),
            ],
            options={
                'unique_together': {('workspace', 'github_id')},
            },
        ),
        migrations.CreateModel(
            name='Commit',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sha', models.CharField(max_length=40, unique=True)),
                ('message', models.TextField()),
                ('author_login', models.CharField(blank=True, default='', max_length=255)),
                ('author_name', models.CharField(blank=True, default='', max_length=255)),
                ('author_email', models.CharField(blank=True, default='', max_length=255)),
                ('url', models.URLField(blank=True, default='')),
                ('branch', models.CharField(blank=True, default='', max_length=255)),
                ('added_files', django_mongodb_backend.fields.ArrayField(base_field=models.CharField(max_length=500), blank=True, default=list)),
                ('modified_files', django_mongodb_backend.fields.ArrayField(base_field=models.CharField(max_length=500), blank=True, default=list)),
                ('removed_files', django_mongodb_backend.fields.ArrayField(base_field=models.CharField(max_length=500), blank=True, default=list)),
                ('github_timestamp', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commits', to='HackAPI.workspace')),
                ('pull_request', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='commits', to='HackAPI.pullrequest')),
            ],
        ),
        migrations.CreateModel(
            name='PRReview',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('github_id', models.IntegerField()),
                ('reviewer_login', models.CharField(max_length=255)),
                ('reviewer_avatar_url', models.URLField(blank=True, default='')),
                ('state', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('changes_requested', 'Changes Requested'), ('commented', 'Commented'), ('dismissed', 'Dismissed')], default='pending', max_length=20)),
                ('body', models.TextField(blank=True, default='')),
                ('html_url', models.URLField(blank=True, default='')),
                ('commit_sha', models.CharField(blank=True, default='', max_length=40)),
                ('github_submitted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('pull_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='HackAPI.pullrequest')),
            ],
            options={
                'unique_together': {('pull_request', 'github_id')},
            },
        ),
        migrations.CreateModel(
            name='PRComment',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('github_id', models.IntegerField()),
                ('comment_type', models.CharField(choices=[('issue', 'Issue Comment'), ('review', 'Review Comment')], default='issue', max_length=10)),
                ('author_login', models.CharField(max_length=255)),
                ('author_avatar_url', models.URLField(blank=True, default='')),
                ('body', models.TextField()),
                ('html_url', models.URLField(blank=True, default='')),
                ('diff_hunk', models.TextField(blank=True, default='')),
                ('path', models.CharField(blank=True, default='', max_length=500)),
                ('position', models.IntegerField(blank=True, null=True)),
                ('commit_sha', models.CharField(blank=True, default='', max_length=40)),
                ('github_created_at', models.DateTimeField(blank=True, null=True)),
                ('github_updated_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('pull_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='HackAPI.pullrequest')),
                ('review', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comments', to='HackAPI.prreview')),
            ],
            options={
                'unique_together': {('pull_request', 'github_id', 'comment_type')},
            },
        ),
    ]
