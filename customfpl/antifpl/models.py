from django.db import models
import auto_prefetch
from django.utils.translation import ugettext as _
from django.urls import reverse

from fplservice.models import FootballerPerformance

# Create your models here.


class Manager(models.Model):

    team_id = models.IntegerField(_("Team Id"), unique=True, primary_key=True)
    team_name = models.CharField(_("Team Name"), max_length=50)

    manager_id = models.IntegerField(_("Manager Id"), unique=True)
    manager_name = models.CharField(_("Manager Name"), max_length=50)

    class Meta:
        verbose_name = _("Manager")
        verbose_name_plural = _("Managers")

    def __str__(self):
        return f"{self.team_name} - {self.manager_name}"

    def get_absolute_url(self):
        return reverse("Manager_detail", kwargs={"pk": self.pk})


class PointsTable(auto_prefetch.Model):

    manager = auto_prefetch.ForeignKey(
        "antifpl.Manager", verbose_name=_("manager"), on_delete=models.CASCADE
    )
    gw = models.IntegerField(_("Gameweek"))
    team_value = models.IntegerField(_("Team Value"))
    itb = models.IntegerField(_("In the Bank"))
    transfers = models.IntegerField(_("Transfers"))
    transfers_hits = models.IntegerField(_("Transfer Hits"))
    chip = models.CharField(_("Chip"), max_length=10, null=True)
    last_gw = models.IntegerField(_("Last GW Points"))
    site_points = models.IntegerField(_("Site Points"), default=0)
    cvc_pens = models.IntegerField(_("Captain/VC Penalty"), null=True)
    inactive_players = models.IntegerField(_("Inactive Players"), null=True)
    inactive_players_pens = models.IntegerField(
        _("Inactive Players Penalty"), null=True
    )
    gw_points = models.IntegerField(_("GW Points (+Pens)"), default=0)

    rank = models.IntegerField(_("GW Rank"), null=True)
    last_rank = models.IntegerField(_("Last GW Rank"))

    total = models.IntegerField(_("Total"))

    class Meta:
        verbose_name = _("Points Table")
        unique_together = [("manager", "gw")]

    def __str__(self):
        return f"{self.manager.team_name} - {self.gw} - {self.total}"


class FootballerPerformanceAnti(FootballerPerformance):

    anti_points = models.IntegerField(_("Anti Points"), null=True, default=0)

    form_5_gw = models.FloatField(_("Form (5 GW)"), default=0)
    form_season = models.FloatField(_("Form (Season)"), default=0)
    points_per_mil_5_gw = models.FloatField(_("Points Per Million (5 GW)"), default=0)
    points_per_mil_season = models.FloatField(
        _("Points Per Million (Season)"), default=0
    )

    class Meta:
        verbose_name = _("Footballer's Performance Anti")
        verbose_name_plural = _("Footballer Performance Anti")

    def __str__(self):
        return f"{self.footballer} - {self.gw} - {self.anti_points}"
