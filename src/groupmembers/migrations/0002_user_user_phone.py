# Generated by Django 3.2 on 2021-12-29 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groupmembers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_phone',
            field=models.CharField(default=123456789, max_length=15),
            preserve_default=False,
        ),
    ]
