from django.db import models
from django.utils import timezone
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)


# ----------------------------------
class Resident(models.Model):
    """
    my_number_id : for all people of japanese nationality, some of foreign people
    residence_number : for all of foreign people
    """
    id = models.AutoField(primary_key=True)
    my_num_id = models.CharField(max_length=12, unique=True)
    resident_num = models.CharField(max_length=12, unique=True, blank=True, null=True)
    last_name = models.CharField(max_length=32, blank=True, null=True)
    first_name = models.CharField(max_length=32, blank=True, null=True)
    birthday = models.DateTimeField(blank=True, null=True)
    address = models.CharField(max_length=64)
    # phone_number = PhoneField(blank=True, null=True, help_text='phone number')
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return ' '.join([self.last_name, self.first_name])
