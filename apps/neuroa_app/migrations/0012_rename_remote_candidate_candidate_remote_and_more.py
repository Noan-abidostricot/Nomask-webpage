# Generated by Django 5.1.6 on 2025-02-26 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neuroa_app', '0011_merge_20250221_1052'),
    ]

    operations = [
        migrations.RenameField(
            model_name='candidate',
            old_name='remote',
            new_name='candidate_remote',
        ),
        migrations.AlterField(
            model_name='experience',
            name='experience_contract_type',
            field=models.CharField(choices=[('contract', 'Contract'), ('training', 'Training'), ('other', 'Other')], default='other', max_length=50),
        ),
    ]
