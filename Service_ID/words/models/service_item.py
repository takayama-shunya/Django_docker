from django.db import models, IntegrityError
from django.db.models import Q
from typing import List, Dict, Any, Union
from django.utils import timezone
from . import Item_Start, Item_End, Joint
import logging

logger = logging.getLogger(__name__)


class Service_Item(models.Model):
    id = models.AutoField(primary_key=True)
    phrase = models.CharField(unique=True, max_length=32)
    is_app_con = models.BooleanField(default=False)
    word_id_serial = models.CharField(unique=True, max_length=255)  # ex. '12|83|46'
    word_family_id_serial = models.CharField(max_length=255)  # not unique
    core_item_id = models.CharField(max_length=16, blank=True, null=True)  # id is unique but nullable
    opt_item_id = models.CharField(max_length=16, blank=True, null=True)  # id is unique but nullable
    item_start = models.ForeignKey(Item_Start, on_delete=models.DO_NOTHING)
    joint = models.ForeignKey(Joint, on_delete=models.DO_NOTHING)
    item_end = models.ForeignKey(Item_End, on_delete=models.DO_NOTHING)
    is_core_std = models.BooleanField(default=False)
    is_opt_std = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.phrase

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["item_start", "joint", "item_end"],
                name="unique_word"
            ),
        ]

    @classmethod
    def save_serv(cls, item_start, joint, item_end):
        serv_item = Service_Item()
        word_id_serial = Joint.get_word_id_serial(item_start, joint, item_end)
        if not Service_Item.objects.filter(word_id_serial__exact=word_id_serial).exists():
            serv_item.phrase = Joint.join_words_without_blank(item_start, joint, item_end)
            serv_item.word_id_serial = word_id_serial
            serv_item.word_family_id_serial = Joint.get_word_family_id_serial(item_start, joint, item_end)
            serv_item.core_item_id = None
            serv_item.opt_item_id = None
            serv_item.item_start = item_start
            serv_item.joint = joint
            serv_item.item_end = item_end
            serv_item.is_core_std = False
            serv_item.save()
            return True
        else:
            return False

    @classmethod
    def update_serv(cls, item_start, joint, item_end):
        serv_item = Service_Item.objects.filter(item_start=item_start, joint=joint, item_end=item_end).get()
        word_family_id_serial = Joint.get_word_family_id_serial(item_start, joint, item_end)
        if cls._is_unique(word_family_id_serial):
            serv_item.word_id_serial = Joint.get_word_id_serial(item_start, joint, item_end)
            serv_item.word_family_id_serial = word_family_id_serial
            serv_item.save()
            return True
        else:
            txt = 'word_family_id_serial[{}]には標準項目が複数あります。[{}]'
            raise Exception(txt.format(word_family_id_serial, serv_item.phrase))

    @classmethod
    def _is_unique(cls, word_family_id_serial):
        serv_items = Service_Item.objects.filter(word_family_id_serial=word_family_id_serial, is_core_std=True).all()
        return True if len(serv_items) == 1 else False

    @classmethod
    def set_is_core_std(cls, phrase, is_app_con):
        serv_item = Service_Item.objects.filter(phrase=phrase).get()
        serv_item.is_core_std = True
        serv_item.core_item_id = cls._create_or_get_id(serv_item.phrase, 'c')
        serv_item.is_app_con = is_app_con
        serv_item.save()
        logger.debug('[set is_core_std] {}'.format(serv_item.phrase))
        return cls.__name__, serv_item.phrase

    @classmethod
    def set_is_opt_std(cls, phrase):
        serv_item = Service_Item.objects.filter(phrase=phrase).get()
        logger.debug('[phrase, serv_item] {} {}'.format(phrase, serv_item))
        if serv_item.is_opt_std is False:
            serv_item.is_opt_std = True
            serv_item.opt_item_id = serv_item.temp_opt_item_id
            serv_item.save()
            logger.debug('[set_is_opt_std() is_opt_std] {}'.format(serv_item.phrase))
        else:
            logger.warning('[WARNING] 既にオプション項目として登録されています。{}'.format(serv_item))
        return cls.__name__, serv_item.phrase

    @classmethod
    def _create_or_get_id(cls, phrase, c_or_o):
        new_core_item_id_int = cls.__get_new_core_item_id()
        c_or_o_id = c_or_o + str(new_core_item_id_int)
        logger.debug('[_create_or_get_id() c_or_o_id] {}'.format(c_or_o_id))
        return c_or_o_id

    @property
    def core_item_id_int(cls):
        return int(cls.core_item_id[1::])

    @property
    def opt_item_id_int(cls):
        return int(cls.opt_item_id[1::])

    @classmethod
    def __get_new_core_item_id(cls):
        serv_items = Service_Item.objects.filter(is_core_std=True).all()
        if len(serv_items) > 0:
            latest_core_item_id = max([serv_item.core_item_id_int for serv_item in serv_items])
            new_core_item_id_int = latest_core_item_id + 1
        else:
            new_core_item_id_int = 1
        logger.debug('[__get_or_set_id() latest_id] {}'.format(new_core_item_id_int))
        return new_core_item_id_int

    @classmethod
    def fuzzy_search(cls, phrase: str) -> List:
        item_starts = cls.get_item_starts(phrase)
        item_ends = cls.get_item_ends(phrase)
        word_family_id_serial = cls.get_word_family_id_serial(phrase)
        serv_items = Service_Item.objects.filter(
            Q(item_start__in=item_starts) |
            Q(item_end__in=item_ends) |
            Q(word_family_id_serial__in=word_family_id_serial),
            Q(is_core_std=True) |
            Q(is_opt_std=True)) \
            .order_by('-id').all()
        logger.debug('[fuzzy_search() serv_items] {}'.format(serv_items))
        return serv_items

    @classmethod
    def get_item_starts(cls, phrase) -> List:
        Model = Item_Start
        word_part = Model.objects.filter(word__regex=phrase).order_by('-id').first()
        logger.debug('[get_item_starts() word_part] {}'.format(word_part))
        return cls._get_word_parts(Model, word_part)

    @classmethod
    def get_item_ends(cls, phrase) -> List:
        Model = Item_End
        word_part = Model.objects.filter(word__regex=phrase).order_by('-id').first()
        logger.debug('[get_item_ends() word_part] {}'.format(word_part))
        return cls._get_word_parts(Model, word_part)

    @classmethod
    def get_word_family_id_serial(cls, phrase):
        serv_items = Service_Item.objects.filter(phrase=phrase).all()
        return [serv_item.word_family_id_serial for serv_item in serv_items]

    @classmethod
    def _get_word_parts(cls, Model, word_part) -> List:
        if word_part is not None:
            word_parts = Model.objects.filter(word_family=word_part.word_family).order_by('-id').all()
        else:
            word_parts = []
        logger.debug('[_get_word_parts() word_parts] {}'.format(word_parts))
        return word_parts

    @property
    def temp_opt_item_id(self):
        logger.debug('[self.core_item_id[1::]] {}'.format(self.core_item_id))
        return 'o' + self.core_item_id[1::]
