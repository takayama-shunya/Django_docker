from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import View
from django.urls import reverse
from ..forms import SelectCandidatesForm, ValidateCandidatesForm, Formatter
from words.models import Service_Item
from ..models import Raw_Item
from peace_keeping.models import Service_Stock
from utils.views import Decode
import logging

logger = logging.getLogger(__name__)


def index(request):
    return HttpResponseRedirect(reverse('restore_order:select_candidates'))


class SelectCandidates(View):
    def get(self, request, *args, **kwargs):
        logger.debug('[WARNING] {}'.format('run "python3 manage.py collectstatic" before run this class'))
        path = SelectCandidatesForm.get_file_path(kwargs['area_name'], 'abs')
        serv_name, can_name, serv_item_phrases, can_items, inputs \
            = SelectCandidatesForm.get_data_from_raw_data(path)
        context = {
            'area_name': kwargs['area_name'],
            'phrases': serv_name + serv_item_phrases,
            'cans': can_name + can_items,
            'inputs': inputs,
        }
        logging.debug('[context] {}'.format(context))
        return render(request, 'restore_order/select_candidates.html', context)


class ConfirmCandidates(View):
    def post(self, request, *args, **kwargs):
        context = {
            'area_name': request.POST['area_name'],
            'phrases': [request.POST['serv_name']] + ValidateCandidatesForm.abstract_els(request, 'serv_item'),
            'cans': [request.POST['can_name']] + ValidateCandidatesForm.abstract_els(request, 'can_item'),
            'inputs': ValidateCandidatesForm.abstract_els(request, 'input'),
        }
        logging.debug('[context] {}'.format(context))
        return render(request, 'restore_order/confirm_candidates.html', context)


class ValidateCandidates(View):
    def post(self, request, *args, **kwargs):
        logging.debug('[request.POST] {}'.format(request.POST))
        _serv_items = ValidateCandidatesForm.abstract_els(request, 'serv_item')
        can_items = ValidateCandidatesForm.abstract_els(request, 'can_item')
        serv_id = Service_Stock.objects.filter(serv_name__exact=request.POST['serv_name'],
                                               area__name='内閣中央省庁').get().serv_id
        logger.debug('[serv_id] {}'.format(serv_id))
        serv_items = Decode.to_4_els_dict(serv_id, Service_Item)
        sent_items = Decode.to_4_els_dict(Raw_Item.get_service_id(can_items), Service_Item)
        logger.debug('[serv_items] {}'.format(serv_items))
        logger.debug('[sent_items] {}'.format(sent_items))
        serv_id_dict = Formatter.categorize_core_or_opt(serv_items, sent_items, request.POST['area_name'])

        context = {
            'area_name': request.POST['area_name'],
            'phrases': [request.POST['serv_name']] + _serv_items,
            'cans': [request.POST['can_name']] + can_items,
            'inputs': ValidateCandidatesForm.abstract_els(request, 'input'),
            'file_path': SelectCandidatesForm.get_file_path(request.POST['area_name'], 'rel'),
            'serv_id_dict': serv_id_dict,
        }

        logging.warning('[WARNING] {}'.format('バリデーション無しで保存が実行されます。'))
        # todo バリデーションの際にコア項目かオプション項目かの分類を行う。

        logger.debug('[context] {}'.format(context))
        serv_id = Raw_Item.save_raw_item(context)
        is_std_items = Raw_Item.set_is_opt_std_to_serv_item(serv_id)
        Service_Stock.save_item_from_raw_item(Raw_Item.objects.get(serv_id=serv_id))
        context.update({
            'raw_item_id': serv_id
        })
        del context['serv_id_dict']
        request.session['context'] = context

        logging.debug('[context] {}'.format(context))
        return HttpResponseRedirect(reverse('restore_order:register_candidates'))


class RegisterCandidates(View):
    def get(self, request, *args, **kwargs):
        context = request.session['context']
        return render(request, 'restore_order/confirm_candidates.html', context)
