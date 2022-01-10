import graphene
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType
from group.models import GroupMember


class GroupMemberType(DjangoObjectType):
    class Meta:
        model = GroupMember


class UserType(DjangoObjectType):
    is_admin = graphene.String(source='is_admin')
    is_staff = graphene.String(source='is_staff')

    class Meta:
        model = get_user_model()
        exclude_fields = ['password']
