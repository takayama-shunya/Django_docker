from django.db import models
from django.db import IntegrityError
from django.utils import timezone
from offices.models import Area
from words.models import Service_Item
from utils.views import Encode, Decode
from typing import List, Dict, Any, Union
import logging

logger = logging.getLogger(__name__)


class Raw_Item(models.Model):
    id = models.AutoField(primary_key=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, to_field='code', default=1)
    name_in_paper = models.CharField(max_length=32)
    serv_id = models.CharField(max_length=255, unique=True)
    serv_name = models.CharField(max_length=32)
    items_in_paper_serial = models.CharField(max_length=255)
    items_order_by_serv_item_serial = models.CharField(max_length=255)
    items_order_by_serv_item_id_serial = models.CharField(max_length=255)
    core_serv_id = models.CharField(max_length=255, unique=True)
    core_items_serial = models.CharField(max_length=255)
    core_items_not_in_paper_serial = models.CharField(max_length=255, null=True, blank=True)
    opt_serv_id = models.CharField(max_length=255, blank=True, null=True)
    opt_items_serial = models.CharField(max_length=255, null=True, blank=True)
    original_file_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '-'.join([self.area.name, self.serv_name])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["area", "serv_id"],
                name="unique_serv_id_in_small_area"
            ),
        ]

    @classmethod
    def save_raw_item(cls, context: Dict) -> str:
        serv_id_dict = context['serv_id_dict']
        serv_id, core_serv_id, opt_serv_id = Encode.raw_data(serv_id_dict)
        logger.debug('[save_raw_item() some_serv_ids] {}'.format([serv_id, core_serv_id, opt_serv_id]))
        area_name = Area.objects.filter(name__exact=context['area_name']).get()
        serv_name = context['cans'][0]
        if not Raw_Item.objects.filter(serv_id=serv_id).exists():
            raw_item = Raw_Item()
            raw_item.area = area_name
            raw_item.name_in_paper = context['phrases'][0]
            raw_item.serv_name = serv_name
            raw_item.items_in_paper_serial = '|'.join(context['phrases'][1::])
            raw_item.items_order_by_serv_item_serial = '|'.join(context['cans'][1::])
            raw_item.items_order_by_serv_item_id_serial = \
                Encode.to_ordered_ids(context['cans'][1::], serv_id_dict['opt_item_ids'])
            raw_item.core_serv_id = core_serv_id
            raw_item.core_items_serial = Encode.from_instance_to_phrase_serial(serv_id_dict['core_item_ids'])
            raw_item.core_items_not_in_paper_serial = Encode.from_instance_to_phrase_serial(
                serv_id_dict['core_item_ids_not_in'])
            raw_item.opt_serv_id = opt_serv_id
            raw_item.opt_items_serial = Encode.from_instance_to_phrase_serial(serv_id_dict['opt_item_ids'])
            raw_item.original_file_path = context['file_path']
            raw_item.serv_id = serv_id
            raw_item.save()
            logger.info('[SAVED Raw_Item] {}'.format([raw_item, raw_item.serv_id]))
            return raw_item.serv_id
        else:
            txt = '[WARNING] {}には、既に{}が登録されています。[{}]'
            # raise Exception(txt.format(area, serv_name))
            logger.warning(txt.format(area_name, serv_name, serv_id))
            return Raw_Item.objects.get(serv_id=serv_id).serv_id

    @classmethod
    def get_service_id(cls, can_items):
        _serv_items = []
        for can_item in can_items:
            _serv_items.append(Service_Item.objects.get(phrase__exact=can_item).core_item_id)
        logger.debug('[_serv_items] {}'.format(_serv_items))
        return ''.join(_serv_items)

    @classmethod
    def get_split_items(cls, city):
        raw_items = Raw_Item.objects.filter(small_area=city).all()
        split_items = []
        # for raw_item in raw_items:
        #     import sys
        #     sys.exit()
        #     raw_item.small_area

    @classmethod
    def set_is_opt_std_to_serv_item(cls, raw_item_id):
        is_std_items = []
        raw_item = Raw_Item.objects.get(serv_id=raw_item_id)
        # core_serv_items = raw_item.core_items_serial.split('|') +  raw_item.core_items_not_in_paper_serial.split('|')
        opt_serv_items = raw_item.opt_items_serial.split('|')
        logger.debug('[set_is_opt_std_to_serv_item() opt_serv_items] {}'.format(opt_serv_items))
        for opt_serv_item in opt_serv_items:
            _, phrase = Service_Item.set_is_opt_std(opt_serv_item)
        return is_std_items

    @property
    def core_item_serial_(self):
        return None
