from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email), **kwargs
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):

        user = self.create_user(
            email,
            password=password,
        )
        user.admin = True
        user.is_active = True
        user.is_superuser = True
        user.staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='email address',
                              max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    user_phone = models.CharField(max_length=15)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def __str__(self):
        return f"{self.first_name or self.email}"

    def is_group_member(self, fund_group=None):
        "Is the user a member of fund group?"

        return fund_group.id in list(self.user_fund_groups.values_list('group__id', flat=True))

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        "Is the user an admin member?"
        return self.admin

    def has_group_permission(self, permission, group_instance):
        if self.is_staff or group_instance.created_by == self:
            return True

        permissions = [_permission.lower() for
                       _permission in list(self.user_group_permissions.filter(
                           group=group_instance).values_list(
                               'permission__name',
                           flat=True))]

        return permission.lower() in permissions or 'all' in permissions
