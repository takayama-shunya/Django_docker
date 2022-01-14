from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.views import View
from ..models import Service_Name, Service_Item
from ..forms import ServiceItemForm, ServiceNameForm
import logging

logger = logging.getLogger(__name__)


def index(request):
    return HttpResponseRedirect(reverse('words:set_is_standard', args=('serv_item',)))


class SetIsStandard(View):
    def get(self, request, *args, **kwargs):
        is_item, is_form = kwargs['key'] == 'serv_item', kwargs['key'] == 'serv_name'
        form = ServiceItemForm() if is_item else (ServiceNameForm() if is_form else self._raise_error())
        logger.debug('[service_stock] {}'.format(form))
        return render(request, 'words/is_standard/set.html', {'serv_name': form, 'key': kwargs['key']})

    def _raise_error(self):
        txt = 'Key for set_is_standard/<str:key>/ : item or service_stock.\nitem : Form_Item\nform : Form_Name'
        raise Http404(txt)


class ValidateIsStandard(View):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('words:set_is_standard'))

    def post(self, request, *args, **kwargs):
        is_item, is_form = kwargs['key'] == 'serv_item', kwargs['key'] == 'serv_name'
        item_instances, name_instances = [Service_Item, ServiceItemForm], [Service_Name, ServiceNameForm]
        instances = item_instances if is_item else (name_instances if is_form else self._raise_error())
        return self._validate_process(request, kwargs['key'], *instances)

    def _raise_error(self):
        raise Http404(
            'Key for set_is_standard/<str:key>/ : item or service_stock.\nitem : Form_Item\nform : Form_Name')

    def _validate_process(self, request, key, Model, Form):
        form = Form(request.POST)
        if form.is_valid():
            validated_form = form.validate()
            model_name, resemble = Model.set_is_core_std(phrase=validated_form['phrase'], is_app_con=validated_form['is_app_con'])
            request.session['context'] = {
                'model_name': model_name,
                'resemble': resemble
            }
            return HttpResponseRedirect(reverse('words:is_standard_registered'))
        else:
            return render(request, 'words/is_standard/set.html', {'serv_name': form, 'key': key})


def registered_is_standard(request):
    return render(request, 'words/is_standard/registered.html', request.session['context'])
