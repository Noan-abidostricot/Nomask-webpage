# Generated by Django 5.1.6 on 2025-04-11 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neuroa_app', '0025_alter_experience_name_alter_experience_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='job',
            field=models.CharField(max_length=100, verbose_name='Poste recherché'),
        ),
    ]
