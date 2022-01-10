from django.contrib import admin
from .models import Raw_Item, Archived_Data
import logging

logger = logging.getLogger(__name__)


class Raw_ItemAdmin(admin.ModelAdmin):
    # readonly_fields = ('standard_name_id', 'core_service_id')
    list_display = ['area', 'serv_name', 'serv_id']
    search_fields = ['area', 'serv_name', 'serv_id']

class ArchivedDataAdmin(admin.ModelAdmin):
    list_display = [ 'serv_id',]
    search_fields = ['area', 'serv_name', 'serv_id']

admin.site.register(Raw_Item, Raw_ItemAdmin)
admin.site.register(Archived_Data, ArchivedDataAdmin)
