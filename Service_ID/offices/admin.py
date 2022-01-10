from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export import resources
from import_export.admin import ImportExportMixin
from .models import  Area, Officer, Resident
import logging

logger = logging.getLogger(__name__)


class UserResource(resources.ModelResource):
    class Meta:
        model = User


@admin.register(User)
class UserAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = UserResource


class AreaAdmin(admin.ModelAdmin):
    list_display = ['large_area', 'small_area', 'code']
    search_fields = ['large_area', 'small_area', 'code']


class ResidentAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'my_num_id', 'address', 'resident_num']
    search_fields = ['last_name', 'my_num_id', 'address', 'resident_num']


# admin.site.register(User)
admin.site.register(Area, AreaAdmin)
admin.site.register(Officer, UserAdmin)
admin.site.register(Resident, ResidentAdmin)
