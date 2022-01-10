from django.db import models, IntegrityError
from typing import List, Dict, Any, Union
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


# ----------------------------------
class Item_Start(models.Model):
    word = models.CharField(unique=True, max_length=16)
    word_family = models.IntegerField()
    word_relative = models.CharField(max_length=64, default=None, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.word


class Item_End(models.Model):
    word = models.CharField(unique=True, max_length=16)
    word_family = models.IntegerField()
    word_relative = models.CharField(max_length=64, default=None, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.word


# ----------------------------------
class Name_Start(models.Model):
    word = models.CharField(unique=True, max_length=16)
    word_family = models.IntegerField()
    word_relative = models.CharField(max_length=64, default=None, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.word


class Name_End(models.Model):
    word = models.CharField(unique=True, max_length=16)
    word_family = models.IntegerField()
    word_relative = models.CharField(max_length=64, default=None, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.word


class Joint(models.Model):
    word = models.CharField(unique=True, max_length=16)
    word_family = models.IntegerField()
    word_relative = models.CharField(max_length=64, default=None, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.word

    @staticmethod
    def join_words_without_blank(start, joint, end) -> str:
        join_items = []
        for word in [start, joint, end]:
            if word.word != "''":
                join_items.append(word.word)
        serv_el = ''.join(join_items)
        logger.debug('[serv_el] {}'.format(serv_el))
        return serv_el

    @staticmethod
    def get_word_id_serial(start, joint, end) -> str:
        return '|'.join([str(word.id) for word in [start, joint, end]])

    @staticmethod
    def get_word_family_id_serial(start, joint, end) -> str:
        word_family_id_serial = '__'.join([str(word.word_family) for word in [start, joint, end]])
        logger.debug('[word_family_id_] {}'.format(word_family_id_serial))
        return word_family_id_serial

