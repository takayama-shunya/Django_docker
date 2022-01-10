from django import forms
from ..models import Service_Item, Service_Name, Service_Stock
from typing import List, Dict, Any, Union
import logging

logger = logging.getLogger(__name__)


class ServiceStockForm(forms.Form):
    serv_name = forms.CharField()

    def __init__(self, *args, **kwd):
        super(ServiceStockForm, self).__init__(*args, **kwd)

    class Meta:
        model = Service_Stock
        fields = ('serv_name')
        labels = {
            'serv_name': 'サービス名'
        }

    @classmethod
    def clean_fields(cls, request_post):
        inputs, serv_name = cls._get_inputs(request_post)
        serv_name = cls._clean_serv_name(serv_name)
        serv_items = cls._clean_serv_items(inputs)
        return serv_name, serv_items

    @classmethod
    def _get_inputs(cls, request_post):
        inputs = dict(request_post)
        _ = inputs.pop('csrfmiddlewaretoken')
        serv_name = inputs.pop('serv_name')[0]
        logger.debug('[serv_name] {}'.format(serv_name))
        return inputs, serv_name

    @classmethod
    def _clean_serv_name(cls, name):
        logger.debug('[name] {}'.format(name))
        serv_name = Service_Name.objects.select_related('name_start').filter(
            is_std=True, name_start__word__contains=name[0]).get()
        logger.debug('[serv_name] {}'.format(serv_name))

        if serv_name is None:
            raise Exception('serv_name is None. name={}'.format(name))
        cls.__is_in_serv_phrase(serv_name, _type='serv_name')
        try:
            return serv_name.phrase
        except Exception as e:
            cls.__raise_exception(serv_name, e)

    @classmethod
    def _clean_serv_items(cls, inputs):
        _serv_items = [item[0] for item in inputs.values()]
        logger.debug('[serv_items] {}'.format(_serv_items))
        std_items = []
        for _serv_item in _serv_items:
            serv_item = Service_Item.objects.filter(phrase=_serv_item).get()
            try:
                std_items.append(serv_item.phrase)
            except Exception as e:
                cls.__raise_exception(serv_item, e)
        logger.debug('[std_items] {}'.format(std_items))
        return std_items

    @classmethod
    def __is_in_serv_phrase(cls, el, **_type):
        logger.debug('[_type] {}'.format(_type))
        if el is None:
            raise forms.ValidationError('このphraseはテーブルにありません。 {}'.format(el))
        if _type == 'serv_name':
            logger.debug(
                '[word_family_id_serial word_id_serial] {}'.format([el.word_family_id_serial, el.word_id_serial]))

    @classmethod
    def __raise_exception(cls, phrase, e):
        logger.debug('[e] {}'.format(e))
        if e.__str__() == 'Service_Item matching query does not exist.':
            txt = 'このphraseのword_familyにはis_core_std=Trueがありません。[{}]'
            raise forms.ValidationError(txt.format(phrase))
        else:
            raise forms.ValidationError('[e] {}'.format(e))

