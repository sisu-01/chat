# Generated by Django 4.1.3 on 2022-12-19 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatroom',
            name='state',
            field=models.IntegerField(null=True),
        ),
    ]
