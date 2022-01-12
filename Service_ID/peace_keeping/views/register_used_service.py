from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import View
from django.urls import reverse
from django.conf import settings
from ..models import Service_Stock, Used_Service, Area
from utils.views import Decode
from ..forms import UsedServiceForm, Formatter
import logging
import json
from django.http.response import JsonResponse
from django.http import HttpResponse

logger = logging.getLogger(__name__)


class GetNeeds(View):
    def get(self, request, *args, **kwargs):
        context = {
            'area_name': kwargs['area_name'],
            'base_url': Service_Stock.get_base_url(request),
        }
        return render(request, 'peace_keeping/used_service/get_needs.html', context)


class FuzzySearch(View):
    def get(self, request, *args, **kwargs):
        phrases = [s_s.serv_name.phrase for s_s in Service_Stock.fuzzy_search(kwargs['phrase'], kwargs['area_name'])]
        logger.debug('[phrases] {}'.format(phrases))
        return HttpResponse(','.join(phrases))


class ShowServiceStock(View):
    def get(self, request, *args, **kwargs):
        logger.info('[INFO] Redirected from ValidateFilledForm()')
        logger.debug('[request.session["context"]] {}'.format(request.session['context']))
        return render(request, 'peace_keeping/used_service/show_serv.html', request.session['context'])

    def post(self, request, *args, **kwargs):
        serv_name = request.POST['serv_name']
        area = Area.objects.get(name=request.POST['area_name'])
        logger.debug('[serv_name] {}'.format(serv_name))
        serv_id = Service_Stock.objects.filter(area=area).get(serv_name__phrase=serv_name).serv_id
        decoded_serv_id = Decode.to_4_els_list(serv_id)
        phrase_val_list = Formatter.get_phrase_val_list(*decoded_serv_id)
        context = {
            'area_name': request.POST['area_name'],
            'serv_name': Service_Stock.objects.filter(serv_id__exact=serv_id).get().serv_name,
            'serv_id': serv_id,
            'phrase_val_list': phrase_val_list,
            'serv_item_id_sep': '/',
        }
        logger.debug('[context] {}'.format(context))
        return render(request, 'peace_keeping/used_service/show_serv.html', context)


class ValidateUsedService(View):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('peace_keeping:show_serv'))

    def post(self, request, *args, **kwargs):
        area_name, serv_name, serv_id, inputs = UsedServiceForm.clean_fields(request.POST)
        context = {
            'area_name': area_name,
            'serv_name': serv_name,
            'serv_id': serv_id,
            'phrase_val_list': Formatter.old_phrase_val_list(inputs),
            'serv_item_id_sep': '/',
        }
        request.session['context'] = context
        return HttpResponseRedirect(reverse('peace_keeping:confirm_used_serv'))


class ConfirmUsedService(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'peace_keeping/used_service/confirm_used_serv.html', request.session['context'])


class RegisterUsedService(View):
    def post(self, request, *args, **kwargs):
        if request.POST['submit'] == 'submit':
            return self._proceed(request)
        elif request.POST['submit'] == 'back':
            return HttpResponseRedirect(reverse('peace_keeping:show_serv'))
        else:
            raise Exception('request.POST["submit"] has a wrong value except from "forward" or "back"')

    def _proceed(self, request):
        logger.debug('[serv_id] {}'.format(request.session['context']['serv_id']))
        serv_id = Used_Service.save_used_serv(request.session['context'])
        context = request.session['context']
        context['serv_id'] = serv_id
        return render(request, 'peace_keeping/used_service/register_used_serv.html', context)
