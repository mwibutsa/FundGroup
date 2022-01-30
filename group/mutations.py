import random
from datetime import timedelta

import graphene
from django.contrib.auth import get_user_model
from graphql.error.base import GraphQLError
from graphql_jwt.decorators import login_required

from .models import GeneratedNumber, Group, Permission, UserGroupPermission
from .types import GeneratedNumberType, GroupType, UserGroupPermissionType


class GenerateNumber(graphene.Mutation):
    generated_number = graphene.Field(GeneratedNumberType)

    class Arguments:
        group_id = graphene.Int(required=True)

    @login_required
    def mutate(self, info, group_id):
        user = info.context.user
        group = Group.objects.get(pk=group_id)

        if not user.is_group_member(group):
            raise GraphQLError(
                "You're not part of this fund group. Kindly contact the admin for a spot")

        # Generate random number
        generated_numbers = GeneratedNumber.objects.filter(group=group)

        if len(generated_numbers) == group.total_members:
            raise GraphQLError('This fund group is full. Please contact your admin for a spot.')

        else:
            random_number = random.randint(1, group.total_members)
            generate = True
            number_exists = False

            while generate:
                number_exists = GeneratedNumber.objects.filter(
                    group=group, number=random_number, owner=user).first()

                if number_exists is not None:
                    random_number = random.randint(1, group.total_members)
                else:
                    generate = False

            generated_number = GeneratedNumber.objects.create(
                group=group, owner=user, number=random_number)

            return GenerateNumber(generated_number=generated_number)


class CreateGroup(graphene.Mutation):
    fund_group = graphene.Field(GroupType)

    class Arguments:
        name = graphene.String(required=True)
        total_members = graphene.Int(required=True)
        starting_date = graphene.Date(required=True)
        end_date = graphene.Date()

    @login_required
    def mutate(self, info, **kwargs):
        end_date = kwargs.get('end_date')
        name = kwargs.get('name')
        total_members = kwargs.get('total_members')
        starting_date = kwargs.get('starting_date')
        user = info.context.user

        if not end_date:
            end_date = starting_date + timedelta(total_members * 30)

        group = Group.objects.create(end_date=end_date, name=name,
                                     total_members=total_members,
                                     starting_date=starting_date,
                                     created_by=user)

        return CreateGroup(fund_group=group)


class EditGroup(graphene.Mutation):
    fund_group = graphene.Field(GroupType)

    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        total_members = graphene.Int()
        starting_date = graphene.Date()
        end_date = graphene.Date()

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        id = kwargs.get('id')
        group = Group.objects.get(pk=id)

        if not user.has_group_permission('edit', group):
            raise GraphQLError("You don't have permission to edit this fund group")

        end_date = kwargs.get('end_date')
        total_members = kwargs.get('total_members', group.total_members)
        starting_date = kwargs.get('starting_date', group.starting_date)

        if total_members and not(end_date):
            end_date = starting_date + timedelta(total_members * 30)

        group.name = kwargs.get('name', group.name)
        group.total_members = total_members
        group.starting_date = starting_date
        group.end_date = end_date

        group.save()

        return EditGroup(fund_group=group)


class DeleteGroup(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        user = info.context.user
        group = Group.objects.get(pk=id)

        if not user.has_group_permission('delete', group):
            raise GraphQLError("You don't have permission to delete this group")

        group_name = group.name
        group.delete()

        return DeleteGroup(message=f"Group {group_name} has been deleted successfully")


class GrantGroupPermission(graphene.Mutation):
    granted_permission = graphene.Field(UserGroupPermissionType)

    class Arguments:
        group_id = graphene.ID(required=True)
        permission_id = graphene.ID(required=True)
        user_id = graphene.ID(required=True)

    @login_required
    def mutate(self, info, group_id, permission_id, user_id):

        current_user = info.context.user

        group = Group.objects.get(pk=group_id)

        if not current_user.has_group_permission('grant permission', group):
            raise GraphQLError("You are not allowed to grant permission to other users.")

        permission = Permission.objects.get(pk=permission_id)
        user = get_user_model().objects.get(pk=user_id)

        permission_exists = UserGroupPermission.objects.filter(
            group=group, permission=permission, user=user).first()

        if permission_exists is not None:
            raise GraphQLError(
                f"User {user.first_name or user.email} already has {permission.name} " +
                f"permission on group {group.name}"
            )

        user_permission = UserGroupPermission.objects.create(
            group=group, user=user, permission=permission)

        return GrantGroupPermission(granted_permission=user_permission)


class RevokeGroupPermission(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        group_id = graphene.ID(required=True)
        permission_id = graphene.ID(required=True)
        user_id = graphene.ID(required=True)

    @login_required
    def mutate(self, info, group_id, permission_id, user_id):
        current_user = info.context.user
        group = Group.objects.get(pk=group_id)

        if not current_user.has_group_permission('grant permission', group):
            raise GraphQLError("You are not allowed to revoke permissions from other users.")

        permission = Permission.objects.get(pk=permission_id)
        user = get_user_model().objects.get(pk=user_id)

        existing_permission = UserGroupPermission.objects.filter(
            permission=permission, user=user).first()

        if existing_permission is None:
            raise GraphQLError(
                f"User {user.first_name or user.email} doesn't have " +
                f"{permission.name} permission on {group.name}")

        existing_permission.delete()

        return RevokeGroupPermission(message=f"Permission {permission.name} " +
                                     f"has been successfully revoked from {user.first_name}")


class EditUserGroupPermission(graphene.Mutation):
    edited_permission = graphene.Field(UserGroupPermissionType)

    class Arguments:
        user_permission_id = graphene.ID(required=True)
        new_permission_id = graphene.ID(required=True)
        group_id = graphene.ID(required=True)
        user_id = graphene.ID(required=True)

    def mutate(self, info, user_permission_id, new_permission_id, group_id, user_id):

        current_user = info.context.user
        group = Group.objects.get(pk=group_id)

        if not current_user.has_group_permission('grant permission', group):
            raise GraphQLError(
                f"You are not allowed to change permissions for fund group {group.name}.")

        user = get_user_model().objects.get(pk=user_id)
        # User's previous permission
        existing_permission = UserGroupPermission.objects.get(pk=user_permission_id)
        # import pdb
        # pdb.set_trace()
        if existing_permission.user != user:
            raise GraphQLError(
                f"This permission does not belong to the user {user.first_name or user.email}")

        if existing_permission.group != group:
            raise GraphQLError(
                f"User {user.first_name or user.email} doesn't have" +
                f"{existing_permission.permission.name}" +
                f"permission on fund group {group.name}")

        new_permission = Permission.objects.get(pk=new_permission_id)
        existing_permission.permission = new_permission
        existing_permission.save()

        return EditUserGroupPermission(edited_permission=existing_permission)


class Mutation(graphene.ObjectType):
    create_fund_group = CreateGroup.Field()
    edit_fund_group = EditGroup.Field()
    generate_number = GenerateNumber.Field()
    delete_fund_group = DeleteGroup.Field()
    grant_permission = GrantGroupPermission.Field()
    revoke_group_permission = RevokeGroupPermission.Field()
    edit_user_group_permission = EditUserGroupPermission.Field()
