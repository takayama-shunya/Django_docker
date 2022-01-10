from django.db import models
from django.utils import timezone
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)


# ----------------------------------
class Area(models.Model):
    id = models.AutoField(primary_key=True)
    # name could be used some different large area. ex. 広島の府中市 & 東京都府中市
    name = models.CharField(max_length=64, unique=True)
    code = models.IntegerField(default=1, unique=True)
    large_area = models.CharField(max_length=32)
    large_area_sound = models.CharField(max_length=64)
    small_area = models.CharField(max_length=32)
    small_area_sound = models.CharField(max_length=64)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["large_area", "small_area"],
                name="unique_large_small_area_serial"
            ),
        ]

    @classmethod
    def save_area_from_csv(cls, csv_row):
        logger.info('[save_area_from_csv] {}'.format(csv_row))
        area = Area()
        if not Area.objects.filter(code__exact=csv_row[0]).exists():
            area.code = csv_row[0]
            area.large_area = csv_row[1]
            area.large_area_sound = csv_row[3]
            area.small_area = csv_row[2]
            area.small_area_sound = csv_row[4]
            area.name = csv_row[1] + csv_row[2]
            try:
                area.save()
            except IntegrityError:
                logger.warning('[WARNING] {} is not saved by duplication'.format(csv_row[1] + csv_row[2]))
                pass
