# Generated by Django 3.2 on 2022-01-01 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groupmembers', '0002_user_user_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
