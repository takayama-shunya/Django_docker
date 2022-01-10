from django.db import models
from offices.models import Area
from typing import List, Dict, Any, Union
from words.models import Service_Item
import logging

logger = logging.getLogger(__name__)


class Encode():

    @classmethod
    def core_serv_id(cls, serv_items: List) -> str:
        logger.debug('[core_serv_id() serv_items] {}'.format(serv_items))
        serv_item_ids = []
        for _serv_item in serv_items:
            serv_item = Service_Item.objects.filter(phrase=_serv_item).get()
            serv_item_ids.append(serv_item.core_item_id)
        logger.debug('[core_serv_id() core_item_ids] {}'.format(serv_item_ids))
        return ''.join(serv_item_ids)

    @classmethod
    def opt_serv_id(cls, serv_items: List) -> Union[str, None]:
        logger.debug('[opt_serv_id() serv_items] {}'.format(serv_items))
        serv_item_ids = []
        for _serv_item in serv_items:
            query = Service_Item.objects.filter(phrase=_serv_item)
            if query.filter(is_opt_std=True).exists():
                serv_item_ids.append(query.get().opt_item_id)
        logger.debug('[opt_serv_id() opt_serv_ids] {}'.format(serv_item_ids))
        return ''.join(serv_item_ids) if len(serv_items) > 0 else None

    @classmethod
    def from_4_els(cls, els: List) -> str:
        """
        :param [core_serv_id, custom_serv_id, area_code, ver]
        :return: serv_id
        """
        logger.debug('[from_4_els() els] {}'.format(els))
        _els = []
        for el in els:
            if el != None:
                _els.append(el)
        return '-'.join(list(map(str, _els)))

    @classmethod
    def raw_data(cls, serv_id_dict: Dict):
        """
        serv_id_dict = { 'core_item_ids': [], 'core_item_ids_not_in': [], 'opt_item_ids': [], 'area': int, 'ver': int,}
        :return: serv_id
        """
        logger.debug('[raw_data() serv_id_dict] {}'.format(serv_id_dict))
        core_item_ids_serial = cls._encode_to_core_serv_id(serv_id_dict['core_item_ids'])
        core_item_ids_not_in_serial = cls._encode_to_core_serv_id(serv_id_dict['core_item_ids_not_in'])
        core_serv_id = ''.join([core_item_ids_serial, core_item_ids_not_in_serial])
        opt_serv_id = cls._encode_to_opt_serv_id(serv_id_dict['opt_item_ids'])
        serv_id = cls.from_4_els([core_serv_id, opt_serv_id, serv_id_dict['area'], serv_id_dict['ver']])
        some_serv_ids = [serv_id, core_serv_id, opt_serv_id]
        logger.debug('[raw_data() some_serv_ids] {}'.format(some_serv_ids))
        return some_serv_ids

    @classmethod
    def _encode_to_core_serv_id(cls, dict) -> str:
        logger.debug('[_encode_to_core_serv_id() dict] {}'.format(dict))
        core_serv_id = ''.join([el.core_item_id for el in dict])
        logger.debug('[_encode_to_core_serv_id() core_serv_id] {}'.format(core_serv_id))
        return core_serv_id

    @classmethod
    def _encode_to_opt_serv_id(cls, dict) -> str:
        logger.debug('[_encode_to_opt_serv_id() dict] {}'.format(dict))
        opt_serv_id = ''.join([el.temp_opt_item_id for el in dict]) if len(dict) > 0 else None
        logger.debug('[_encode_to_opt_serv_id() opt_serv_id] {}'.format(opt_serv_id))
        return opt_serv_id

    @classmethod
    def from_instance_to_phrase_serial(cls, serv_item_instances) -> str:
        return '|'.join(serv_item.phrase for serv_item in serv_item_instances)

    @classmethod
    def from_serv_id_to_phrase_serial(cls, serv_id, c_or_o) -> Union[str, None]:
        if serv_id is not None:
            _serv_ids = serv_id.split(c_or_o)[1::]
            logger.debug('[from_serv_id_to_phrase_serial() _serv_ids] {}'.format(_serv_ids))
            return ''.join(c_or_o + id for id in _serv_ids)
        else:
            return None

    @classmethod
    def to_ordered_ids(cls, cans, opt_item_ids) -> str:
        logger.debug('[cans] {}'.format(cans))
        logger.debug('[opt_item_ids] {}'.format(opt_item_ids))
        ordered_ids = []
        for can in cans:
            serv_item = Service_Item.objects.get(phrase__exact=can)
            if serv_item in opt_item_ids:
                ordered_ids.append(serv_item.temp_opt_item_id)
            else:
                ordered_ids.append(serv_item.core_item_id)
        return '|'.join(ordered_ids)
