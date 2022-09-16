from django.db import models
import auto_prefetch
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

# Create your models here.


class Position(models.Model):
    id = models.IntegerField(_("Type"), unique=True, primary_key=True)
    name = models.CharField(_("Name"), max_length=20, unique=True)

    squad_max_play = models.IntegerField(_("Max Playing"), default=1)
    squad_min_play = models.IntegerField(_("Min Playing"), default=1)
    squad_max_select = models.IntegerField(_("Max in Squad"), default=1)

    class Meta:
        verbose_name = _("Position")

    def __str__(self):
        return self.name


class Gameweek(models.Model):

    id = models.IntegerField(_("GW ID"), unique=True, primary_key=True)
    name = models.CharField(_("GW Name"), unique=True, max_length=12)
    start_time = models.PositiveBigIntegerField(_("Start Time"))
    end_time = models.PositiveBigIntegerField(_("End Time"))
    completed = models.BooleanField(_("GW Completed"), default=False)
    is_current = models.BooleanField(_("Is Current GW"), default=False)
    stats_completed = models.BooleanField(_("Stats Completed"), default=False)

    last_updated = models.DateTimeField(_("Last Updated Time"), auto_now=True)
    last_stats_updated = models.DateTimeField(
        _("Last Stats Updated Time"), auto_now=True
    )
    active_gameweek = models.BooleanField(_("Active Gameweek"), default=True)

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


class Footballer(models.Model):
    """Model class for each Footballer Basic Details"""

    id = models.IntegerField(_("Id"), unique=True, primary_key=True)
    name = models.CharField(_("Name"), max_length=20)  # web_name
    team = auto_prefetch.ForeignKey(
        "fplservice.TeamMeta", verbose_name=_("Team"), on_delete=models.CASCADE
    )
    cost = models.IntegerField(_("Cost"), default=0)
    assists = models.IntegerField(_("assists"), default=0)
    goals_conceded = models.IntegerField(_("goals_conceded"), default=0)
    clean_sheets = models.IntegerField(_("clean_sheets"), default=0)
    goals_scored = models.IntegerField(_("goals_scored"), default=0)
    yellow_cards = models.IntegerField(_("yellow_cards"), default=0)
    red_cards = models.IntegerField(_("red_cards"), default=0)

    form_5_gw = models.FloatField(_("Form (5 GW)"), default=0)
    form_season = models.FloatField(_("Form (Season)"), default=0)
    points_per_mil_5_gw = models.FloatField(_("Points Per Million (5 GW)"), default=0)
    points_per_mil_season = models.FloatField(
        _("Points Per Million (Season)"), default=0
    )

    position = auto_prefetch.ForeignKey(
        "fplservice.Position",
        verbose_name=_("Position"),
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Footballer")
        verbose_name_plural = _("Footballers")
        ordering = ("-cost",)

    def __str__(self):
        return f"{self.name} - {self.team} - {self.cost}"

    def get_absolute_url(self):
        return reverse("Footballer_detail", kwargs={"pk": self.pk})


class FootballerPerformance(models.Model):

    """Model class to store footballer's performance each gw"""

    footballer = auto_prefetch.ForeignKey(
        "fplservice.Footballer", verbose_name=_("Footballer"), on_delete=models.CASCADE
    )
    gw = auto_prefetch.ForeignKey(
        "fplservice.Gameweek", verbose_name=_("Gameweek"), on_delete=models.CASCADE
    )

    minutes = models.PositiveIntegerField(_("GW Minutes"), null=True)
    points = models.IntegerField(_("GW Points"), null=True)
    starting_xi = models.IntegerField(_("Starting XI Selection"), default=0)
    squad_xv = models.IntegerField(_("Squad Selection"), default=0)
    captains = models.IntegerField(_("Captaincy"), default=0)
    cvc = models.IntegerField(_("Captain/Vice Captain"), default=0)

    class Meta:
        verbose_name = _("Footballer GW Performance")
        unique_together = ('footballer', 'gw')
