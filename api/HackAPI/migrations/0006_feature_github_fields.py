from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HackAPI', '0005_pullrequest_commit_prreview_prcomment'),
    ]

    operations = [
        # Add github_token to Workspace
        migrations.AddField(
            model_name='workspace',
            name='github_token',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        # Add new fields to Feature
        migrations.AddField(
            model_name='feature',
            name='type',
            field=models.CharField(
                choices=[('issue', 'Issue'), ('pull_request', 'Pull Request'), ('local', 'Local')],
                default='local',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='feature',
            name='github_number',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='feature',
            name='github_id',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='feature',
            name='html_url',
            field=models.URLField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='feature',
            name='state',
            field=models.CharField(
                choices=[('open', 'Open'), ('closed', 'Closed')],
                default='open',
                max_length=10,
            ),
        ),
        # Remove old github fields from Task
        migrations.RemoveField(
            model_name='task',
            name='github_issue_number',
        ),
        migrations.RemoveField(
            model_name='task',
            name='github_pr_number',
        ),
        # Add checkbox_index to Task
        migrations.AddField(
            model_name='task',
            name='checkbox_index',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
