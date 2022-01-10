from django.db import models
from django.utils import timezone
from . import Raw_Item
from offices.models import Area
import logging

logger = logging.getLogger(__name__)


class Archived_Data(models.Model):
    id = models.AutoField(primary_key=True)
    area_id = models.ForeignKey(Area, on_delete=models.CASCADE, to_field='code', default=901000)
    serv_id = models.ForeignKey(Raw_Item, on_delete=models.CASCADE, to_field='serv_id', related_name='_serv_id')
    serv_name = models.CharField(max_length=255)
    core_serv_id = models.CharField(max_length=255)
    core_items_serial = models.CharField(max_length=255)
    opt_serv_id = models.CharField(max_length=255, blank=True, null=True)
    opt_items_serial = models.CharField(max_length=255, null=True, blank=True)
    inputs_in_paper_serial = models.CharField(max_length=255)
    original_file_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return ''.join([self.serv_id.area.name, self.serv_id.serv_name])

    @classmethod
    def save_archive(self, serv_id, inputs, path):
        archived_data = Archived_Data()
        inputs_in_paper_serial = '|'.join(inputs)
        raw_item = Raw_Item.objects.get(serv_id=serv_id)
        if not Archived_Data.objects.filter(serv_id=serv_id, inputs_in_paper_serial=inputs_in_paper_serial).exists():
            archived_data.area_id = Area.objects.get(code=serv_id.split('-')[2])
            archived_data.serv_id = raw_item
            archived_data.serv_name = raw_item.serv_name
            archived_data.core_serv_id = raw_item.core_serv_id
            archived_data.core_items_serial = raw_item.core_items_serial
            archived_data.opt_serv_id = raw_item.opt_serv_id
            archived_data.opt_items_serial = raw_item.opt_items_serial
            archived_data.inputs_in_paper_serial = inputs_in_paper_serial
            archived_data.original_file_path = path
            archived_data.save()
            return archived_data.serv_id
        else:
            return None
