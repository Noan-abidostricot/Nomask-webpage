# Generated by Django 5.1.6 on 2025-02-20 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neuroa_app', '0009_alter_candidateattribute_candidate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attribute',
            name='description',
        ),
        migrations.AddField(
            model_name='candidateattribute',
            name='description',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
