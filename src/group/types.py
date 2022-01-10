import graphene
from graphene_django import DjangoObjectType

from .models import GeneratedNumber, Group, UserGroupPermission


class UserGroupPermissionType(DjangoObjectType):
    class Meta:
        model = UserGroupPermission


class GroupType(DjangoObjectType):
    is_past_due = graphene.String(source="is_past_due")

    class Meta:
        model = Group


class GeneratedNumberType(DjangoObjectType):
    receive_date = graphene.String(source="receive_date")

    class Meta:
        model = GeneratedNumber
