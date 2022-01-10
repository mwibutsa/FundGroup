import graphene
from django.contrib.auth import get_user_model
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from group.models import Group, GroupMember

from .types import GroupMemberType, UserType


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        email = graphene.String(required=True)
        user_phone = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, first_name, last_name, email, user_phone, password):
        user = get_user_model().objects.create_user(first_name=first_name,
                                                    last_name=last_name,
                                                    email=email,
                                                    user_phone=user_phone,
                                                    password=password)
        return CreateUser(user=user)


class AddGroupMember(graphene.Mutation):
    group_member = graphene.Field(GroupMemberType)

    class Arguments:
        member_id = graphene.ID(required=True)
        group_id = graphene.ID(required=True)

    @login_required
    def mutate(self, info, member_id, group_id):
        user = info.context.user
        group = Group.objects.get(pk=group_id)

        if not user.has_group_permission('add member', group):
            raise GraphQLError(f"You are not allowed to add a group member to {group.name}")

        member = get_user_model().objects.get(pk=member_id)

        group_member = GroupMember.objects.create(member=member, group=group)

        return AddGroupMember(group_member=group_member)


class RemoveGroupMember(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        member_id = graphene.ID(required=True)
        group_id = graphene.ID(required=True)

    @login_required
    def mutate(self, info, member_id, group_id):
        user = info.context.user
        group = Group.objects.get(pk=group_id)

        if not user.has_group_permission('remove member', group):
            raise GraphQLError("You are not allowed to remove a group member.")

        member = get_user_model().objects.get(pk=member_id)

        GroupMember.objects.get(member=member, group=group).delete()

        return RemoveGroupMember(
            message=f"{member.first_name} has been removed from fund group {group.name}")


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    add_group_member = AddGroupMember.Field()
    remove_group_member = RemoveGroupMember.Field()
