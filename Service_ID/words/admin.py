from django.contrib import admin
from .models import Item_Start, Joint, Item_End, Service_Item, Name_Start, Name_End, Service_Name
import logging

logger = logging.getLogger(__name__)


class WordAdmin(admin.ModelAdmin):
    list_display = ['word', 'word_family', 'word_relative']
    search_fields = ['word', 'word_family', 'word_relative']


class ServiceItemAdmin(admin.ModelAdmin):
    list_display = ['phrase', 'core_item_id', 'opt_item_id', 'word_id_serial', 'word_family_id_serial', 'is_core_std',
                    'is_opt_std','is_app_con']
    search_fields = ['phrase', 'core_item_id', 'opt_item_id', 'word_id_serial', 'word_family_id_serial']


class ServiceNameAdmin(admin.ModelAdmin):
    list_display = ['phrase', 'word_id_serial', 'word_family_id_serial', 'is_std']
    # list_filter = ['is_std']
    search_fields = ['phrase', 'word_id_serial', 'word_family_id_serial']


admin.site.register(Item_Start, WordAdmin)
admin.site.register(Joint, WordAdmin)
admin.site.register(Item_End, WordAdmin)
admin.site.register(Name_Start, WordAdmin)
admin.site.register(Name_End, WordAdmin)
# -----
admin.site.register(Service_Item, ServiceItemAdmin)
admin.site.register(Service_Name, ServiceNameAdmin)
