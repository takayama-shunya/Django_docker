from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib import messages
from django.views import View
from django.contrib.staticfiles.storage import staticfiles_storage
from .models import Area
import os, csv
import logging

logger = logging.getLogger(__name__)


def index(request):
    return HttpResponse('This is offices')


class MergeAreaCsv(View):
    def get(self, request, *args, **kwargs):
        _path = os.path.join('offices', 'csv', '都道府県市区町村_5.csv')
        csv_rows = self._get_csv_rows(_path)
        for csv_row in csv_rows:
            Area.save_area_from_csv(csv_row)
        context = {
            'csv_rows': csv_rows
        }
        return render(request, 'offices/merge_area_csv.html', context)

    def _get_csv_rows(cls, _path):

        path = staticfiles_storage.path(_path)
        logging.debug('[staticfiles_storage] {}'.format(path))
        csv_rows = []
        with open(path, 'r') as f:
            rows = csv.reader(f)
            for idx, row in enumerate(rows):
                if idx == 0:
                    continue
                row[0] = int(row[0])
                csv_rows.append(list(row))
                logging.debug('[csv_row] {}'.format(row))
            return csv_rows
