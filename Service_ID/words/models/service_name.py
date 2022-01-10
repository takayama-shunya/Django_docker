from django.db import models, IntegrityError
from django.db.models import Q
from typing import List, Dict, Any, Union
from django.utils import timezone
from . import Name_Start, Name_End, Joint
import logging

logger = logging.getLogger(__name__)


class Service_Name(models.Model):
    id = models.AutoField(primary_key=True)
    phrase = models.CharField(unique=True, max_length=32)
    word_id_serial = models.CharField(unique=True, max_length=255)  # ex. '12|83|46'
    word_family_id_serial = models.CharField(max_length=255)  # not unique
    name_start = models.ForeignKey(Name_Start, on_delete=models.DO_NOTHING)
    joint = models.ForeignKey(Joint, on_delete=models.DO_NOTHING)
    name_end = models.ForeignKey(Name_End, on_delete=models.DO_NOTHING)
    is_std = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.phrase

    @classmethod
    def save_serv(cls, name_start, joint, name_end):
        serv_name = Service_Name()
        word_id_serial = Joint.get_word_id_serial(name_start, joint, name_end)
        if not Service_Name.objects.filter(word_id_serial__exact=word_id_serial).exists():
            serv_name.phrase = Joint.join_words_without_blank(name_start, joint, name_end)
            serv_name.word_id_serial = word_id_serial
            serv_name.word_family_id_serial = Joint.get_word_family_id_serial(name_start, joint, name_end)
            serv_name.name_start = name_start
            serv_name.joint = joint
            serv_name.name_end = name_end
            serv_name.is_std = False
            serv_name.save()
            return True
        else:
            return False

    @classmethod
    def set_is_std(cls, phrase):
        serv_name = Service_Name.objects.filter(phrase=phrase).get()
        serv_name.is_std = True
        serv_name.save()
        return cls.__name__, serv_name.phrase

    @property
    def is_core_std(self):
        return self.is_std

    @classmethod
    def set_is_core_std(self, phrase):
        return self.set_is_std(phrase)

    @classmethod
    def fuzzy_search(cls, phrase: str) -> List:
        name_starts = cls.get_name_starts(phrase)
        name_ends = cls.get_name_ends(phrase)
        word_family_id_serial = cls.get_word_family_id_serial(phrase)
        serv_names = Service_Name.objects.filter(
            Q(name_start__in=name_starts) |
            Q(name_end__in=name_ends) |
            Q(word_family_id_serial__in=word_family_id_serial),
            is_std=True) \
            .order_by('-id').all()
        logger.debug('[fuzzy_search() serv_names] {}'.format(serv_names))
        return serv_names

    @classmethod
    def get_name_starts(cls, phrase) -> List:
        Model = Name_Start
        word_part = Model.objects.filter(word__contains=phrase).order_by('-id').first()
        logger.debug('[get_name_starts() word_part] {}'.format(word_part))
        return cls._get_word_parts(Model, word_part)

    @classmethod
    def get_name_ends(cls, phrase) -> List:
        Model = Name_End
        word_part = Model.objects.filter(word__contains=phrase).order_by('-id').first()
        logger.debug('[get_name_ends() word_part] {}'.format(word_part))
        return cls._get_word_parts(Model, word_part)

    @classmethod
    def get_word_family_id_serial(cls, phrase):
        serv_name = Service_Name.objects.filter(phrase=phrase).all()
        return [serv_name.word_family_id_serial for serv_name in serv_name]

    @classmethod
    def _get_word_parts(cls, Model, word_part) -> List:
        if word_part is not None:
            word_parts = Model.objects.filter(word_family=word_part.word_family).order_by('-id').all()
        else:
            word_parts = []
        logger.debug('[_get_word_parts() word_parts] {}'.format(word_parts))
        return word_parts
