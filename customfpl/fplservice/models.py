from django.db import models
import auto_prefetch
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

# Create your models here.


class Gameweek(models.Model):

    id = models.IntegerField(_("GW ID"), unique=True, primary_key=True)
    name = models.CharField(_("GW Name"), unique=True, max_length=12)
    start_time = models.PositiveBigIntegerField(_("Start Time"))
    end_time = models.PositiveBigIntegerField(_("End Time"))
    completed = models.BooleanField(_("GW Completed"), default=False)
    is_current = models.BooleanField(_("Is Current GW"), default=False)

    last_updated = models.DateTimeField(_("Last Updated Time"), auto_now=True)

    class Meta:
        verbose_name = _("Gameweek")
        verbose_name_plural = _("Gameweeks")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("_detail", kwargs={"pk": self.pk})

    @staticmethod
    def is_gw_completed(gw: int):
        try:
            return Gameweek.objects.get(gw).completed
        except ObjectDoesNotExist:
            return False


class TeamMeta(models.Model):
    """Model class for each PL teams"""

    id = models.IntegerField(_("Id"), unique=True, primary_key=True)
    name = models.CharField(_("Name"), max_length=20, unique=True)
    short_name = models.CharField(_("Short Name"), max_length=3, unique=True)
    code = models.IntegerField(_("Team Code"), unique=True)

    class Meta:
        verbose_name = _("EPL Team")
        verbose_name_plural = _("EPL Teams")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("TeamMeta_detail", kwargs={"pk": self.pk})
