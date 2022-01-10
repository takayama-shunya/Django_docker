from django import forms
from typing import List, Dict, Union
import logging

logger = logging.getLogger(__name__)


class ValidateCandidatesForm(forms.Form):
    @classmethod
    def abstract_els(cls, request, key):
        parsed_els = []
        for el in request.POST:
            if key in el:
                logging.debug('[el] {} {}'.format(el, request.POST[el]))
                parsed_els.append(request.POST[el])
        return parsed_els
