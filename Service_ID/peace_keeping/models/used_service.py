from django.db import models
from django.utils import timezone
from offices.models import Resident
from . import Service_Stock
from typing import List, Dict, Union
import logging

logger = logging.getLogger(__name__)


class Used_Service(models.Model):
    serv_id = models.ForeignKey(Service_Stock, to_field='serv_id', related_name='stock_serv_id',
                                on_delete=models.DO_NOTHING)
    issue_num = models.IntegerField()
    my_num_id = models.ForeignKey(Resident, to_field='my_num_id', related_name='res_my_num_id',
                                  on_delete=models.DO_NOTHING, blank=True, null=True)
    resident_num = models.CharField(max_length=12, blank=True, null=True)
    used_serv_item_ids = models.CharField(max_length=255)
    send_vals = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.serv_id.serv_name.phrase

    @classmethod
    def save_used_serv(cls, context: Dict) -> models:
        query = Resident.objects.filter(my_num_id=cls._get_my_num(context['phrase_val_list']))
        resident = query.get() if query.exists() else None
        serv_stock = Service_Stock.objects.filter(serv_id=context['serv_id']).get()
        used_serv = Used_Service()
        used_serv.serv_id = serv_stock
        used_serv.issue_num = cls._get_issue_num(serv_stock.serv_id)
        used_serv.my_num_id = resident
        used_serv.resident_num = resident.resident_num if resident is not None else None
        used_serv.used_serv_item_ids = cls._merge_serv_ids(context['phrase_val_list'])
        used_serv.send_vals = cls._merge_values(context['phrase_val_list'])
        used_serv.save()
        return used_serv.serv_id

    @classmethod
    def _get_issue_num(cls, serv_id: str) -> str:
        used_serv = Used_Service.objects.filter(serv_id__exact=serv_id).order_by('-id').first()
        if used_serv is not None:
            issue_number = int(used_serv.serv_id.serv_id.split('-')[-1]) + 1
        else:
            issue_number = 1
        return str(issue_number)

    @classmethod
    def _get_my_num(cls, phrase_val_list: List) -> str:
        for el in phrase_val_list:
            logging.debug('[el, type] {}'.format([el, type(el)]))
            if 'マイナンバー' in el['serv_item']:
                return el['value']

    @classmethod
    def _merge_serv_ids(cls, phrase_val_list: List) -> str:
        return ''.join([el['serv_item_id'] for el in phrase_val_list])

    @classmethod
    def _merge_values(cls, phrase_val_list: List) -> str:
        return '|'.join([el['value'] for el in phrase_val_list])
