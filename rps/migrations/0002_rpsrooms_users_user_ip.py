# Generated by Django 4.1.3 on 2023-01-19 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rps', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rpsrooms_users',
            name='user_ip',
            field=models.CharField(default=1, max_length=40),
            preserve_default=False,
        ),
    ]
