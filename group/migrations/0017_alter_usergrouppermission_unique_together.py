# Generated by Django 3.2 on 2022-01-10 14:16

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('group', '0016_alter_groupmember_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='usergrouppermission',
            unique_together={('user', 'permission', 'group')},
        ),
    ]
