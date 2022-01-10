from django.db import models
from offices.models import Area
from typing import List, Dict, Any, Union
import logging

logger = logging.getLogger(__name__)


class Decode():

    @classmethod
    def to_4_els_dict(cls, serv_id: str, _Service_Item) -> Dict[str, Union[List, List, int, int]]:
        """
        :return: {'core_item_ids': List,
                  'opt_item_ids': List,
                  'area': models,
                  'ver': int, }
        """
        core_item_ids, opt_item_ids, area_code, ver = cls.to_4_els_list(serv_id)
        serv_items_dict = {
            'core_item_ids': cls._get_core_instantiated(core_item_ids, _Service_Item),
            'opt_item_ids': cls._get_opt_instantiated(opt_item_ids, _Service_Item),
            'area': area_code,
            'ver': ver,
        }
        logger.debug('[serv_items_dict] {}'.format(serv_items_dict))
        return serv_items_dict

    @classmethod
    def to_4_els_list(cls, serv_id: str) -> List[Union[List[Union[str]], List, int, int]]:
        """
        :return: [
        core_item_ids = [str, str,,,],
        opt_item_ids = [str, str,,,],
        area_code = int
        ver = int
        ]
        """
        logger.debug('[***serv_id] {}'.format(serv_id))
        core_opt_area_ver = serv_id.split('-')
        logger.debug('[core_opt_area_ver] {}'.format(core_opt_area_ver))
        core_item_ids = ['c' + core_item for core_item in core_opt_area_ver[0].split('c')[1::]]
        # if len(core_opt_area_ver) == 4:
        #     opt_item_ids = [opt_item for opt_item in core_opt_area_ver[1].split('o')[1::]]
        # elif len(core_opt_area_ver) == 3:
        #     opt_item_ids = []
        # else:
        #     raise Exception('サービスIDの構造に不具合があります。core_opt_area_ver {}'.format(core_opt_area_ver))
        opt_item_ids = cls._get_opt_serv_id(core_opt_area_ver)
        area_code, ver = cls._get_area_code__ver(core_opt_area_ver)
        decoded_serv_id = [core_item_ids, opt_item_ids, area_code, ver]
        logger.debug('[decoded_serv_id] {}'.format(decoded_serv_id))
        return decoded_serv_id

    @classmethod
    def _get_core_instantiated(cls, item_ids: List, _Service_Item) -> List:
        instances = []
        for item_id in item_ids:
            query = _Service_Item.objects.filter(core_item_id=item_id, is_core_std=True)
            if query.exists():
                instances.append(query.get())
        logger.debug('[instances] {}'.format(instances))
        return instances

    @classmethod
    def _get_opt_instantiated(cls, item_ids: List, _Service_Item) -> List:
        instances = []
        for item_id in item_ids:
            query = _Service_Item.objects.filter(opt_item_id=item_id, is_opt_std=True)
            if query.exists():
                instances.append(query.get())
        logger.debug('[instances] {}'.format(instances))
        return instances

    @classmethod
    def _get_opt_serv_id(cls, core_opt_area_ver):
        if len(core_opt_area_ver) == 4:  # core-opt-area-ver
            opt_item_ids = ['o' + opt_item for opt_item in core_opt_area_ver[1].split('o')[1::]]
        elif len(core_opt_area_ver) == 3:  # core--area-ver
            opt_item_ids = []
        elif len(core_opt_area_ver) == 1:  # core--- . core_id from legacy papers(csv)
            opt_item_ids = []
        else:
            raise Exception('サービスIDの構造に不具合があります。core_opt_area_ver {}'.format(core_opt_area_ver))
        return opt_item_ids

    @classmethod
    def _get_area_code__ver(cls, core_opt_area_ver):
        if len(core_opt_area_ver) in [4, 3]:  # core-opt-area-ver or core--area-ver
            area_code = int(core_opt_area_ver[-2])
            ver = int(core_opt_area_ver[-1])
        elif len(core_opt_area_ver) == 1:  # core--- . core_id from legacy papers(csv)
            area_code = None
            ver = None
        else:
            raise Exception('サービスIDの構造に不具合があります。core_opt_area_ver {}'.format(core_opt_area_ver))
        return area_code,ver
