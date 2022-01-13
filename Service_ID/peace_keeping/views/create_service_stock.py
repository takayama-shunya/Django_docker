from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic import TemplateView
from django.urls import reverse
from ..models import Service_Stock
from ..forms import ServiceStockForm
from words.forms import ServiceItemForm
import logging

logger = logging.getLogger(__name__)


def index(request):
    return HttpResponseRedirect(reverse('peace_keeping:create_serv', args=(2,)))


class CreateServiceStock(View):
    def get(self, request, *args, **kwargs):
        context = {
            'area_name': kwargs['area_name'],
            'base_url': Service_Stock.get_base_url(request),
            'serv_items': {0: ServiceItemForm()},
            'phrase': None,
        }
        logger.debug('[context] {}'.format(context))
        return render(request, 'peace_keeping/service_stock/create_serv/create_serv.html', context)


class ValidateServiceStock(View):
    def post(self, request, *args, **kwargs):
        serv_name, serv_items = ServiceStockForm.clean_fields(request.POST)
        serv_id = Service_Stock.save_serv_stock(serv_name, serv_items, 'ValidateServiceStock')
        context = {
            'serv_name': serv_name,
            'serv_items': serv_items,
            'serv_id': serv_id,
        }
        request.session['context'] = context
        logger.warning('[WARNING] core_item_idの順序が変わると別の新たなserv_idが生成されて、異なるレコードとして保存されます。')
        return HttpResponseRedirect(reverse('peace_keeping:register_serv'))


class RegisterServiceStock(View):
    def get(self, request, *args, **kwargs):
        logger.debug('[RegisterServiceStock() request.session["context"]] {}'.format(request.session['context']))
        context = request.session['context']
        return render(request, 'peace_keeping/service_stock/create_serv/register_serv.html', context)
