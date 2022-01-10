from django.contrib import admin
from .models import Service_Name, Service_Stock, Used_Service
import logging

logger = logging.getLogger(__name__)


class ServiceStockAdmin(admin.ModelAdmin):
    list_display = ['serv_name_id', 'area', 'serv_id', 'modified_at']
    search_fields = ['serv_name_id', 'area', 'serv_id', 'modified_at']

    def get_form(self, request, obj=None, **kwargs):
        form = super(ServiceStockAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['serv_name'].queryset = Service_Name.objects.filter(is_std=True)
        return form


#
# class UsedServiceAdmin(admin.ModelAdmin):
#     list_display = ['serv_id', 'my_num_id', 'residence_num']
#     search_fields = ['serv_id', 'my_num_id__my_num_id', 'residence_num']


admin.site.register(Service_Stock, ServiceStockAdmin)
# admin.site.register(Used_Service, UsedServiceAdmin)
admin.site.register(Used_Service)
