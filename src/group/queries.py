
import graphene
from graphql import GraphQLError

from .models import GeneratedNumber, Group
from .types import GeneratedNumberType, GroupType


class Query(graphene.ObjectType):
    fund_groups = graphene.List(GroupType, limit=graphene.Int(), search=graphene.String())
    fund_group = graphene.Field(GroupType, id=graphene.Int(required=True))
    generated_numbers = graphene.List(
        GeneratedNumberType, group_id=graphene.Int(), user_id=graphene.Int())

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
