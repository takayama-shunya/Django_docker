from django import forms
from ..models import Service_Item
import logging

logger = logging.getLogger(__name__)


class ServiceItemForm(forms.Form):
    phrase = forms.CharField(min_length=1, max_length=20)
    is_app_con = forms.BooleanField(required=False)

    def __init__(self, *args, **kwd):
        super(ServiceItemForm, self).__init__(*args, **kwd)

    class Meta:
        model = Service_Item
        fields = ('phrase', 'is_app_con')
        labels = {
            'phrase': '表現',
            'is_app_con': '適用条件',
        }

    def validate(self):
        data = self.cleaned_data['phrase']
        is_exists = Service_Item.objects.filter(phrase__exact=data).exists()
        logger.debug('[item] {} is_exists {}'.format(data, is_exists))
        if is_exists:
            serv_item = Service_Item.objects.filter(phrase__exact=data).get()
            if serv_item.is_core_std:
                raise forms.ValidationError('すでにこの表現は標準として使われています。')
            else:
                fis = Service_Item.objects.filter(word_family_id_serial__exact=serv_item.word_family_id_serial).all()
                logger.log(10, '[ris] {}'.format(fis))
                for item in fis:
                    if item.is_core_std:
                        txt = '同じword_familyの他の表現が、すでに標準として使われています。[{}]'
                        raise forms.ValidationError(txt.format(item))
                else:
                    pass
        else:
            raise forms.ValidationError('この表現は非標準として登録されていません。')
        return data
