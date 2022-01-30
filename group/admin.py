from django.contrib import admin

from . import models

admin.site.register(models.Group)
admin.site.register(models.Permission)
admin.site.register(models.UserGroupPermission)
admin.site.register(models.GeneratedNumber)
admin.site.register(models.GroupMember)
