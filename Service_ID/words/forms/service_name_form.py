from django import forms
from ..models import Service_Name
import logging

logger = logging.getLogger(__name__)


class ServiceNameForm(forms.Form):
    phrase = forms.CharField(min_length=1, max_length=20)

    def __init__(self, *args, **kwd):
        super(ServiceNameForm, self).__init__(*args, **kwd)

    class Meta:
        model = Service_Name
        fields = ('phrase')
        labels = {
            'phrase': 'サービス名',
        }

    def validate(self):
        data = self.cleaned_data['phrase']
        is_exists = Service_Name.objects.filter(phrase__exact=data).exists()
        logger.debug('[item] {} is_exists {}'.format(data, is_exists))
        if is_exists:
            serv_name = Service_Name.objects.filter(phrase__exact=data).get()
            if serv_name.is_std:
                raise forms.ValidationError('すでにこの表現は標準として使われています。')
            else:
                resembles = Service_Name.objects.filter(
                    word_family_id_serial__exact=serv_name.word_family_id_serial).all()
                logger.debug('[resembles] {}'.format(resembles))
                for item in resembles:
                    if item.is_std:
                        txt = '同じword_familyの他の表現が、すでに標準として使われています。[{}]'
                        raise forms.ValidationError(txt.format(item))
                else:
                    pass
        else:
            raise forms.ValidationError('この表現は非標準として登録されていません')
        return data
