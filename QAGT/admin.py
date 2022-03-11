from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import *

# ADDITIONAL_FIELDS = (('附加数据', {'fields': ('grade', 'sex', 'introduction', 'tags')}),)

# @admin.register(User)
# class UserAdmin(BaseUserAdmin):
#     list_display = ('__str__', 'first_name', 'grade', 'sex', 'tags', 'is_active', 'is_staff')
#     fieldsets = BaseUserAdmin.fieldsets + ADDITIONAL_FIELDS
#     add_fieldsets = BaseUserAdmin.fieldsets + ADDITIONAL_FIELDS

admin.site.register(Users)
admin.site.register(Articles)
admin.site.register(Comments)
admin.site.register(Topics)
admin.site.register(Reports)
admin.site.register(Notices)
admin.site.register(Likes)
