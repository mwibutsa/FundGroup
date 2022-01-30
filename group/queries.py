
import graphene
from graphql import GraphQLError

from .models import GeneratedNumber, Group, Permission, UserGroupPermission
from .types import (GeneratedNumberType, GroupType, PermissionType,
                    UserGroupPermissionType)


class Query(graphene.ObjectType):
    fund_groups = graphene.List(GroupType, limit=graphene.Int(), search=graphene.String())
    fund_group = graphene.Field(GroupType, id=graphene.Int(required=True))
    generated_numbers = graphene.List(
        GeneratedNumberType, group_id=graphene.Int(), user_id=graphene.Int())
    user_permission = graphene.List(UserGroupPermissionType, group_id=graphene.Int(
        required=True), user_id=graphene.Int(required=True))
    permissions = graphene.List(PermissionType)

    def resolve_fund_groups(self, _, limit=None, search=None):
        if search is not None and limit is not None:
            return Group.objects.filter(name__icontains=search, limit=limit)

        elif limit is not None:
            return Group.objects.all(limit=limit)
        elif search is not None:
            return Group.objects.filter(name__icontains=search)
        else:
            return Group.objects.all()

    def resolve_fund_group(self, _, id):

        group = Group.objects.get(pk=id)

        if not group:
            raise GraphQLError('Group with provided id was not found')

        return group

    def resolve_generated_numbers(self, info, user_id=None, group_id=None):
        filters = {}

        if user_id:
            filters['owner_id'] = user_id
        if group_id:
            filters['group_id'] = group_id

        return GeneratedNumber.objects.filter(**filters)

    def resolve_user_permission(self, info, user_id, group_id):
        return UserGroupPermission.objects.filter(group_id=group_id, user_id=user_id)

    def resolve_permissions(self, info):
        return Permission.objects.all()
