from django import forms
from ..models import Service_Stock, Used_Service
from .service_stock_form import ServiceStockForm
import logging

logger = logging.getLogger(__name__)


class UsedServiceForm(forms.Form):
    serv_name = forms.CharField()
    my_num_id = forms.IntegerField(min_value=0, max_value=999999999999)

    def __init__(self, *args, **kwd):
        super(UsedServiceForm, self).__init__(*args, **kwd)

    class Meta:
        model = Used_Service
        fields = ('serv_name')
        labels = {
            'serv_name': 'サービス名'
        }

    @classmethod
    def clean_fields(cls, request_post):
        inputs = dict(request_post)
        area_name, _serv_id, _serv_name = cls._get_serv_id_name(inputs)
        serv_id = cls.clean_serv_id(_serv_id)
        serv_name = ServiceStockForm._clean_serv_name(_serv_name)
        return [area_name, serv_name, serv_id, inputs]

    @classmethod
    def _get_serv_id_name(cls, inputs):
        _ = inputs.pop('csrfmiddlewaretoken')
        area_name = inputs.pop('area_name')[0]
        serv_id = inputs.pop('serv_id')[0]
        serv_name = inputs.pop('serv_name')[0]
        return area_name, serv_id, serv_name

    @classmethod
    def clean_serv_id(self, serv_id):
        serv_stock = Service_Stock.objects.filter(serv_id__exact=serv_id).first()
        if serv_stock is None:
            raise forms.ValidationError('このserv_idはService_Stockにありません。')
        else:
            return serv_stock.serv_id

