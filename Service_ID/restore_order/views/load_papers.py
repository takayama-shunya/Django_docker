from django.shortcuts import render
from django.views import View
from ..forms import SelectCandidatesForm
from ..models import Raw_Item, Archived_Data

import logging

logger = logging.getLogger(__name__)


class ReadyToLoadPapers(View):
    def get(self, request, *args, **kwargs):
        raw_item = Raw_Item.objects.select_related('area').filter(area__name=kwargs['area_name']).get()
        logger.debug('[raw_item] {}'.format(raw_item))
        path = SelectCandidatesForm.get_file_path(kwargs['area_name'], 'abs')
        _, _, _, _, inputs = SelectCandidatesForm.get_data_from_raw_data(path)

        # todo 未実装；取り込む項目と記入内容に齟齬がないかバリデーションかける
        logger.warning('[WARNING] {}'.format('未実装；取り込む項目と記入内容に齟齬がないかバリデーションかける'))

        context = {
            'serv_id': raw_item.serv_id,
            'area_name': kwargs['area_name'],
            'phrases': [raw_item.serv_name] + raw_item.items_in_paper_serial.split('|'),
            'serv_ids': [raw_item.serv_id] + raw_item.items_order_by_serv_item_id_serial.split('|'),
            'inputs': inputs,
            'file_path': SelectCandidatesForm.get_file_path(kwargs['area_name'], 'rel'),
        }
        request.session['context'] = context
        logging.debug('[context] {}'.format(context))
        return render(request, 'restore_order/ready_to_load_papers.html', context)


class LoadPapers(View):
    def get(self, request, *args, **kwargs):
        # todo 未実装：保存前にサービスID、日付、入力内容の重複がないかバリデーションかける。
        logger.warning('[WARNING] {}'.format('未実装：保存前にサービスID、日付、入力内容の重複がないかバリデーションかける。'))
        paths = SelectCandidatesForm.get_file_paths(request.session['context']['area_name'])
        _serv_id = request.session['context']['serv_id']
        serv_ids = []
        for path in paths:
            _, _, _, _, inputs = SelectCandidatesForm.get_data_from_raw_data(path)
            serv_ids.append(Archived_Data.save_archive(_serv_id, inputs, path))
        context = {
            'serv_ids': serv_ids,
        }
        logging.debug('[context] {}'.format(context))
        return render(request, 'restore_order/load_papers_done.html', context)
