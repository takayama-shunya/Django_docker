from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.views import View
from ..models import Service_Name, Service_Item, Name_Start, Name_End, Item_Start, Item_End, Joint
import logging

logger = logging.getLogger(__name__)


def index(request):
    return HttpResponseRedirect(reverse('words:set_is_standard', args=('serv_item',)))


class MergeWords(View):
    def get(self, request, *args, **kwargs):
        if kwargs['key'] == 'serv_name':
            phrases = self._get_merged_words(Service_Name, Name_Start, Name_End)
        elif kwargs['key'] == 'serv_item':
            phrases = self._get_merged_words(Service_Item, Item_Start, Item_End)
        else:
            txt = 'Key for set_is_standard/<str:key>/ : item or service_stock.\nitem : Form_Item\nform : Form_Name'
            raise Http404(txt)
        return render(request, 'words/word/merge_words.html', {'phrases': phrases})

    def _get_merged_words(self, Service, Start, End):
        word_families = []
        for _start in Start.objects.all():
            for joint in Joint.objects.all():
                for _end in End.objects.all():
                    serv_item = Joint.join_words_without_blank(_start, joint, _end)
                    is_saved = self._save(Service, _start, joint, _end)
                    if is_saved:
                        word_families.append(serv_item)
        return word_families

    def _save(self, Service, _start, joint, _end):
        is_saved = Service.save_serv(_start, joint, _end)
        return is_saved


class UpdateWords(MergeWords):
    def _save(self, Service, _start, joint, _end):
        is_saved = Service.update_serv(_start, joint, _end)
        return is_saved
