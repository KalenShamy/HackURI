from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HackAPI', '0002_remove_task_workspace_feature_task_feature'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='github_issue_number',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='github_pr_number',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
