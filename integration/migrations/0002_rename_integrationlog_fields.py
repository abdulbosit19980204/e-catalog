# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('integration', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='integrationlog',
            old_name='total',
            new_name='total_items',
        ),
        migrations.RenameField(
            model_name='integrationlog',
            old_name='processed',
            new_name='processed_items',
        ),
        migrations.RenameField(
            model_name='integrationlog',
            old_name='created',
            new_name='created_items',
        ),
        migrations.RenameField(
            model_name='integrationlog',
            old_name='updated',
            new_name='updated_items',
        ),
        migrations.RenameField(
            model_name='integrationlog',
            old_name='errors',
            new_name='error_items',
        ),
        migrations.RenameField(
            model_name='integrationlog',
            old_name='error_message',
            new_name='error_details',
        ),
        migrations.RenameField(
            model_name='integrationlog',
            old_name='started_at',
            new_name='start_time',
        ),
        migrations.RenameField(
            model_name='integrationlog',
            old_name='completed_at',
            new_name='end_time',
        ),
        migrations.RemoveField(
            model_name='integrationlog',
            name='progress_percent',
        ),
    ]

