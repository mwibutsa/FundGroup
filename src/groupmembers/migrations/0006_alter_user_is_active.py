# Generated by Django 3.2 on 2022-01-09 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groupmembers', '0005_auto_20220101_1132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]