from offices.models import Area
from typing import List, Dict, Any, Union
import logging

logger = logging.getLogger(__name__)


class Formatter():

    @classmethod
    def categorize_core_or_opt(cls, serv_items: Dict, sent_items: Dict, area_name: str) \
            -> Dict[str, Union[List, List, List, int, int]]:
        """
        :return:
        serv_id_dict = { 'core_item_ids': [], 'core_item_ids_not_in': [], 'opt_item_ids': [], 'area': int, 'ver': 1,}
        """
        serv_stock_core_items, sent_core_items = cls._get_serv_and_sent_items(serv_items, sent_items)
        serv_id_dict = {
            'core_item_ids': [],
            'core_item_ids_not_in': [],
            'opt_item_ids': [],
            'area': Area.objects.get(name__exact=area_name).code,
            'ver': 1,
        }
        serv_id_dict = cls._append_core(serv_id_dict, serv_stock_core_items, sent_core_items)
        serv_id_dict = cls._categorize_sent(serv_id_dict, serv_stock_core_items, sent_core_items)
        logger.debug('[serv_id_dict] {}'.format(serv_id_dict))
        return serv_id_dict

    @classmethod
    def _get_serv_and_sent_items(cls, serv_items, sent_items):
        serv_stock_core_items = serv_items['core_item_ids']
        sent_core_items = sent_items['core_item_ids']
        logger.debug('[serv_stock_core_items] {}'.format(serv_stock_core_items))
        logger.debug('[sent_core_items] {}'.format(sent_core_items))
        return serv_stock_core_items, sent_core_items

    @classmethod
    def _append_core(cls, serv_id_dict, serv_stock_core_items, sent_core_items):
        for serv_stock_core_item in serv_stock_core_items:
            if serv_stock_core_item in sent_core_items:
                word_family_id_serials = cls.__get_word_family_id_serials(serv_id_dict['core_item_ids'])
                if serv_stock_core_item.word_family_id_serial not in word_family_id_serials:
                    serv_id_dict['core_item_ids'].append(serv_stock_core_item)
            else:
                serv_id_dict['core_item_ids_not_in'].append(serv_stock_core_item)
        logger.debug('[serv_id_dict] {}'.format(serv_id_dict))
        logger.debug('[serv_stock_core_items] {}'.format(serv_stock_core_items))
        logger.debug('[sent_core_items] {}'.format(sent_core_items))
        return serv_id_dict

    @classmethod
    def _categorize_sent(cls, serv_id_dict, serv_stock_core_items, sent_core_items):
        for sent_core_item in sent_core_items:
            if sent_core_item in serv_stock_core_items:
                word_family_id_serials = cls.__get_word_family_id_serials(serv_id_dict['core_item_ids'])
                if sent_core_item.word_family_id_serial not in word_family_id_serials:
                    serv_id_dict['core_item_ids'].append(sent_core_item)
            else:
                serv_id_dict['opt_item_ids'].append(sent_core_item)
        logger.debug('[serv_id_dict] {}'.format(serv_id_dict))
        logger.debug('[serv_stock_core_items] {}'.format(serv_stock_core_items))
        logger.debug('[sent_core_items] {}'.format(sent_core_items))
        return serv_id_dict

    @classmethod
    def __get_word_family_id_serials(cls, instances):
        return [ins.word_family_id_serial for ins in instances]
