# Generated by Django 5.1.6 on 2025-02-18 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neuroa_app', '0003_user_last_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('candidate', 'Candidate'), ('recruiter', 'Recruiter'), ('admin', 'Admin')], default='candidate', max_length=20),
        ),
    ]
