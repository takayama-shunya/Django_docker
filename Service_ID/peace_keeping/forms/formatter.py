from django.db import models
from peace_keeping.models import Service_Item
from offices.models import Area
from typing import List, Dict, Any, Union
import logging

logger = logging.getLogger(__name__)


class Formatter():
    """
    methods :
    get_phrase_val_list()
    old_phrase_val_list()
    categorize_core_or_opt()
    """

    @classmethod
    def get_phrase_val_list(cls,
                            core_item_ids: List,
                            opt_item_ids: List,
                            area_code: models,
                            ver: int
                            ) -> List[Dict[str, Union[str, str, str]]]:

        core_items = [cls._get_core_serv_items(id) for id in core_item_ids]
        opt_items = [cls._get_opt_serv_items(id) for id in opt_item_ids]
        logger.debug('[get_phrase_val_list core_items] {}'.format(core_items))
        logger.debug('[get_phrase_val_list opt_items] {}'.format(opt_items))
        phrase_val_list = cls._create_phrase_val_list(core_items, opt_items)
        return phrase_val_list

    @classmethod
    def _get_core_serv_items(self, id: str) -> models:
        query = Service_Item.objects.filter(core_item_id=id)
        if query.exists():
            return query.get()
        else:
            return None

    @classmethod
    def _get_opt_serv_items(self, id: str) -> models:
        query = Service_Item.objects.filter(opt_item_id=id)
        if query.exists():
            return query.get()
        else:
            return None

    @classmethod
    def _create_phrase_val_list(cls, core_items: List, opt_items: List) -> List[Dict[str, Union[str, str, str]]]:
        """
        :return: [{
                    'serv_item': str,
                    'serv_item_id': str,
                    'value': '',
                }]
        """
        phrase_val_list = []
        merged_items = core_items + opt_items if None not in opt_items else core_items
        for el in merged_items:
            phrase_val_list.append({
                'serv_item': el.phrase,
                'serv_item_id': cls.__get_serv_item_id(el),
                'value': '',
            })
        logging.debug('[_create_phrase_val_list() phrase_val_list] {}'.format(phrase_val_list))
        return phrase_val_list

    @classmethod
    def __get_serv_item_id(cls, el: models) -> str:
        try:
            return el.core_item_id
        except Exception:
            try:
                return el.opt_item_id
            except Exception:
                raise Exception('core_item_id、option_item_idがありません')

    @classmethod
    def old_phrase_val_list(cls, inputs: Dict) -> List[Dict[str, Union[str, str, str]]]:
        """
        :return: phrase_val_list = [{
                'serv_item': str,
                'serv_item_id': str,
                'value': str
            }]
        """
        logging.debug('[inputs] {}'.format(inputs))
        serv_item_ids = inputs.keys()
        values = [val[0] for val in inputs.values()]
        phrase_val_list = []
        for serv_item_id, value in zip(serv_item_ids, values):
            phrase_val_list.append({
                'serv_item': cls._get_serv_item(serv_item_id),
                'serv_item_id': serv_item_id,
                'value': value
            })
        logging.debug('[phrase_val_list] {}'.format(phrase_val_list))
        return phrase_val_list

    @classmethod
    def _get_serv_item(cls, serv_item_id: str) -> str:
        serv_item_id = serv_item_id.split('/')[0]
        logger.debug('[_get_serv_item() serv_item_id] {}'.format(serv_item_id))
        if 'c' == serv_item_id[0]:
            serv_item = Service_Item.objects.filter(core_item_id=serv_item_id).get()
        elif 'o' == serv_item_id[0]:
            serv_item = Service_Item.objects.filter(opt_item_id=serv_item_id).get().phrase
        else:
            raise Exception('サービス項目IDの値が不正です。{}'.format(serv_item_id))
        logging.debug('[Service_Item] {}'.format(serv_item))
        return serv_item.phrase
