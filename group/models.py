from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=255)
    starting_date = models.DateField(auto_now=False, auto_now_add=False)
    total_members = models.IntegerField()
    end_date = models.DateField(auto_now=False, auto_now_add=False)
    created_by = models.ForeignKey(
        get_user_model(), related_name='fund_groups', on_delete=models.CASCADE, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name} has  ({self.total_members})"

    @property
    def is_past_due(self):
        return self.end_date > date.today()

    class Meta:
        ordering = ('name',)


class Permission(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


class UserGroupPermission(models.Model):
    group = models.ForeignKey(
        'Group', related_name='group_permissions', on_delete=models.CASCADE)
    permission = models.ForeignKey(
        'Permission', related_name='group_permissions', on_delete=models.CASCADE)
    user = models.ForeignKey(
        get_user_model(), related_name='user_group_permissions', on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.first_name or self.user.email} \
                can {self.permission.name} --> {self.group.name}"

    def __repr__(self) -> str:
        return f"{self.user.first_name or self.user.email} \
                can {self.permission.name} --> {self.group.name}"

    class Meta:
        unique_together = (('user', 'permission', 'group'),)


class GeneratedNumber(models.Model):
    owner = models.ForeignKey(
        get_user_model(), related_name='generated_numbers', on_delete=models.CASCADE)
    group = models.ForeignKey('Group', related_name='generated_numbers', on_delete=models.CASCADE)
    number = models.IntegerField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    @property
    def receive_date(self):
        "Date on which the user will get money"
        return date.today() + timedelta(self.number * 30)

    def __str__(self) -> str:
        return f"{self.owner.first_name or self.owner.email} will get money on {self.receive_date}."

    class Meta:
        unique_together = (('number', 'group'), ('owner', 'group'))
        ordering = ('number',)


class GroupMember(models.Model):
    """Model to keep track of users who belongs to a particular fund group"""

    member = models.ForeignKey(
        get_user_model(), related_name='user_fund_groups', on_delete=models.CASCADE)
    group = models.ForeignKey('Group', related_name='members', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.member.first_name or self.member.email} is part of {self.group.name}"

    class Meta:
        unique_together = (('member', 'group'),)
