# Generated by Django 5.1.6 on 2025-03-19 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neuroa_app', '0018_alter_experience_city_alter_experience_country_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='attributes',
            field=models.ManyToManyField(related_name='candidates', to='neuroa_app.attribute'),
        ),
        migrations.DeleteModel(
            name='CandidateAttribute',
        ),
    ]
