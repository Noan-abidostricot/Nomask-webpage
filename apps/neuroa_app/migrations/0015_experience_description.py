# Generated by Django 5.1.6 on 2025-02-28 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neuroa_app', '0014_rename_remote_joboffer_remotes'),
    ]

    operations = [
        migrations.AddField(
            model_name='experience',
            name='description',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
