from django import forms
from django.contrib.staticfiles.storage import staticfiles_storage
from words.models import Service_Item, Service_Name
from django.conf import settings
from typing import List, Dict, Union
import logging
import csv, os
import glob

logger = logging.getLogger(__name__)


class SelectCandidatesForm(forms.Form):
    @classmethod
    def get_data_from_raw_data(cls, path: str) -> List:
        """
        :return: ex.
        inputs = ['あらき\u3000あきら', '01-1111-1111', 'A市X区', 'A市Z区']

        """
        csv_rows = cls._get_csv_rows(path)
        serv_name, can_name = cls._get_serv_can_name(csv_rows)
        serv_item_phrases = cls._get_serv_item_phrases_from_csv(csv_rows)
        can_items = cls._get_can_items(serv_item_phrases)
        inputs = cls._get_inputs(csv_rows)
        return [[serv_name], [[can_name]], serv_item_phrases, can_items, inputs]

    @classmethod
    def get_file_path(cls, area_name, abs_or_rel):
        _path = os.path.join('restore_order', 'csv', area_name + '.csv')
        if abs_or_rel == 'abs':
            path = staticfiles_storage.path(_path)
        elif abs_or_rel == 'rel':
            path = os.path.join(settings.PROJECT_DIR_NAME, _path)
        else:
            raise Exception('abs_or_relにabs、rel以外の値が代入されています。{}'.format(abs_or_rel))
        logging.debug('[staticfiles_storage] {}'.format(path))
        return path

    @classmethod
    def get_file_paths(cls, area_name):
        pattern = os.path.join(settings.STATIC_ROOT, 'restore_order', 'csv', area_name + '*.csv')
        _paths = glob.glob(pattern)
        logger.debug('[get_file_paths() pattern] {}'.format(pattern))
        logger.debug('[get_file_paths() _paths] {}'.format(_paths))
        return _paths

    @classmethod
    def _get_csv_rows(cls, path):
        csv_rows = []
        with open(path, 'r') as f:
            rows = csv.reader(f)
            for row in rows:
                logging.debug('[csv_row] {}'.format(row))
                csv_rows.append(list(row))
            return csv_rows

    @classmethod
    def _get_serv_can_name(cls, csv_rows):
        serv_name = csv_rows[0][0]
        logging.debug('[name] {}'.format(serv_name))
        id_serial = Service_Name.objects.filter(phrase__contains=serv_name).first().word_family_id_serial
        can_name = Service_Name.objects.filter(word_family_id_serial=id_serial, is_std=True).get()
        return serv_name, can_name

    @classmethod
    def _get_serv_item_phrases_from_csv(cls, csv_rows: List[Union[List]], ) -> List[Union[str]]:
        """
        :param csv_rows: [header, row1, row2,,,]
        :return: [item1, item2,,,]
        """
        serv_items = [_item[0] for _item in csv_rows[1::]]
        logging.debug('[serv_items] {}'.format(serv_items))
        return serv_items

    @classmethod
    def _get_inputs(cls, csv_rows):
        inputs = [_item[1] for _item in csv_rows[1::]]
        logging.debug('[inputs] {}'.format(inputs))
        return inputs

    @classmethod
    def _get_can_items(cls, serv_item_phrases):
        id_serials = [[]]
        for idx, phrase in enumerate(serv_item_phrases):
            serv_items = Service_Item.objects.filter(phrase__contains=phrase).all()
            for serv_item in serv_items:
                id_serials[idx].append(serv_item.word_family_id_serial)
                logging.debug('[serv_item, serial] {} {}'.format(serv_item, serv_item.word_family_id_serial))
            id_serials[idx] = list(set(id_serials[idx]))
            if idx < len(serv_item_phrases):
                id_serials.append([])

        can_items = [[]]
        for idx, serv_item_phrases in enumerate(id_serials):
            for phrase in serv_item_phrases:
                query = Service_Item.objects.filter(word_family_id_serial=phrase, is_core_std=True)
                if query.exists():
                    can_item = query.get()
                    can_items[idx].append(can_item)
                    logging.debug('[phrase, can_item] {} {}'.format(phrase, can_item))
            if idx < len(id_serials):
                can_items.append([])
        return can_items
