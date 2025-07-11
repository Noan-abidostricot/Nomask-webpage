# Generated by Django 5.1.6 on 2025-02-26 16:37

import django.db.models.deletion
import multiselectfield.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neuroa_app', '0012_rename_remote_candidate_candidate_remote_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('diversity_and_inclusion_policy', models.TextField()),
                ('url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='JobOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('publication_date', models.DateField(auto_now=True)),
                ('city', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('skills', models.TextField()),
                ('is_part_time', models.BooleanField(default=False)),
                ('benefits', models.TextField()),
                ('recruitment_process', models.TextField()),
                ('contract_types', multiselectfield.db.fields.MultiSelectField(choices=[('cdi', 'CDI'), ('cdd', 'CDD'), ('freelance', 'Freelance'), ('self_employed', 'Self_Employed'), ('internship', 'Internship'), ('work_study', 'Work_Study'), ('civic_service', 'Civic_Service'), ('other', 'Other')], max_length=73)),
                ('remote', multiselectfield.db.fields.MultiSelectField(choices=[('full_remote', 'Full_Remote'), ('no_remote', 'No_Remote'), ('hybrid', 'Hybrid')], max_length=28)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='neuroa_app.company')),
            ],
        ),
    ]
