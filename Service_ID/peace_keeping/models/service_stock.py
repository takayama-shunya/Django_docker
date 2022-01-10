from django.db import models
from django.utils import timezone
from django.conf import settings
from words.models import Service_Item, Service_Name
from offices.models import Area
from typing import List, Dict, Union
from utils.views import Encode, Decode
import logging

logger = logging.getLogger(__name__)


class Service_Stock(models.Model):
    id = models.AutoField(primary_key=True)
    serv_name = models.ForeignKey(Service_Name, to_field='phrase', on_delete=models.DO_NOTHING)
    serv_id = models.CharField(unique=True, max_length=255, default='---')
    core_serv_id = models.CharField(max_length=255, unique=False)
    core_items_serial = models.CharField(max_length=255)
    opt_serv_id = models.CharField(max_length=255, blank=True, null=True)
    opt_items_serial = models.CharField(max_length=255, blank=True, null=True)
    area = models.ForeignKey(Area, to_field='code', on_delete=models.DO_NOTHING)
    ver = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.serv_name.phrase

    @classmethod
    def fuzzy_search(cls, serv_name_or_needs: str, area_name: str) -> List:
        serv_names = Service_Name.fuzzy_search(serv_name_or_needs)
        serv_stocks = cls.get_serv_stocks(serv_names, area_name)
        logger.debug('[fuzzy_search() serv_stocks] {}'.format(serv_stocks))
        return serv_stocks

    @classmethod
    def get_serv_stocks(cls, serv_names: List, area_name) -> List:
        logger.debug('[get_serv_stocks() serv_names,area_name] {} {}'.format(serv_names, area_name))
        serv_stocks = []
        for serv_name in serv_names:
            query = Service_Stock.objects.filter(serv_name=serv_name, area__name=area_name)
            if query.exists():
                serv_stocks.append(query.get())
        if len(serv_stocks) > 0:
            return serv_stocks
        else:
            txt = 'Service_Stockに{}の自治体ごとのカスタムフォームが作成されていない可能性があります。'
            raise ValueError(txt.format(serv_names))

    @classmethod
    def get_base_url(cls,request):
        _base_url = 'http://' + request.META.get('REMOTE_ADDR')
        base_url = _base_url if not settings.DEBUG else _base_url + ':' + request.META['SERVER_PORT']
        logging.debug('[base_url] {}'.format(base_url))
        return base_url

    @classmethod
    def _query(self, serv_name, area_name):
        return Service_Stock.objects.filter(serv_name=serv_name, area__name=area_name)

    @classmethod
    def save_serv_stock(cls, serv_name: str, serv_items: List, route_from: str) -> str:
        logger.debug('[save_serv_stock() serv_name,serv_items] {} {}'.format(serv_name, serv_items))
        core_serv_id = Encode.core_serv_id(serv_items)
        custom_serv_id = None if route_from is 'ValidateServiceStock' else Encode.opt_serv_id(serv_items)
        area_instance = Area.objects.get(name='内閣中央省庁')
        ver = 1
        _serv_id = Encode.from_4_els([core_serv_id, custom_serv_id, area_instance.code, ver])
        if not Service_Stock.objects.filter(serv_id__exact=_serv_id).exists():
            serv_stock = Service_Stock()
            serv_stock.serv_name = Service_Name.objects.filter(phrase__exact=serv_name).get()
            serv_stock.core_serv_id = core_serv_id
            serv_stock.core_items_serial = '|'.join(serv_items)
            serv_stock.opt_serv_id = custom_serv_id
            serv_stock.opt_item_serial = Encode.from_serv_id_to_phrase_serial(custom_serv_id, 'o')
            serv_stock.area = area_instance
            serv_stock.ver = ver
            serv_stock.serv_id = Encode.from_4_els([core_serv_id, custom_serv_id, area_instance.code, ver])
            serv_stock.save()
            return serv_stock.serv_id
        else:
            raise Exception('このサービスIDはすでに登録されています。[{}]'.format(_serv_id))

    @classmethod
    def _get_phrase_serial(cls, serv_id, core_or_opt):
        phrases = []
        if core_or_opt == 'core':
            core_serv_ids = list(map(int, serv_id.split('c')[1::]))
            logger.debug('[core_serv_ids] {}'.format(core_serv_ids))
            for core_item_id in core_serv_ids:
                serv_item = Service_Item.objects.filter(core_item_id=core_item_id, is_core_std=True)
                if serv_item.exists():
                    phrases.append(serv_item.get().phrase)
        elif core_or_opt == 'opt':
            opt_serv_ids = list(map(int, serv_id.split('o')[1::]))
            for opt_item_id in opt_serv_ids:
                serv_item = Service_Item.objects.filter(opt_item_id=opt_item_id, is_opt_std=True)
                if serv_item.exists():
                    phrases.append(serv_item.get().phrase)
        else:
            raise Exception('core_or_optにcoreかopt以外の値が代入されています。')
        return '|'.join(phrases)

    @classmethod
    def save_item_from_raw_item(cls, raw_item):
        logger.debug('[raw_item] {}'.format(raw_item))
        serv_id = raw_item.serv_id
        _core_item_ids, _opt_item_ids, _, _ = Decode.to_4_els_list(serv_id)
        area = Area.objects.filter(name=raw_item.area).get()
        serv_name = raw_item.serv_name
        if not Service_Stock.objects.filter(serv_id=serv_id).exists():
            serv_stock = Service_Stock()
            serv_stock.serv_name = Service_Name.objects.get(phrase=serv_name)
            serv_stock.core_serv_id = ''.join(_core_item_ids)
            serv_stock.core_items_serial = raw_item.core_items_serial
            serv_stock.opt_serv_id = ''.join(_opt_item_ids)
            serv_stock.opt_items_serial = raw_item.opt_items_serial
            serv_stock.area = area
            serv_stock.ver = cls._get_latest_ver_num(serv_id)
            serv_stock.serv_id = serv_id
            serv_stock.save()
            logger.info('[SAVED Service_Stock] {}'.format(serv_stock))
            return serv_stock.id
        else:
            txt = '[WARNING] {}には、既に{}が登録されています。[{}]'
            # raise Exception(txt.format(area, serv_name))
            logger.warning(txt.format(area, serv_name, serv_id))

    @classmethod
    def _get_latest_ver_num(cls, serv_id):
        _3_els = '-'.join(serv_id.split('-')[0:3])
        logger.debug('[serv_id] {}'.format(serv_id))
        logger.debug('[_3_els] {}'.format(_3_els))
        serv_stock = Service_Stock.objects.filter(serv_id__regex=_3_els)
        if Service_Stock.objects.filter(serv_id__regex=_3_els).exists():
            latest_serv_stock = Service_Stock.objects.filter(serv_id__regex=_3_els).order_by('-id').first()
            return latest_serv_stock.ver
        else:
            return 1
