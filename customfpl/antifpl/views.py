from django.shortcuts import render
from django.views import generic
from fplservice.models import Footballer, Gameweek

from antifpl.models import FootballerPerformanceAnti, Manager, PointsTable

from .lib import Antifpl

# Create your views here.


class AntiPointsTableView(generic.View):
    template_name = "antifpl/points_table.html"

    def get(self, request, *args, **kwargs):

        antifpl = Antifpl()
        context_data = {
            "anti_table": antifpl.get_anti_points_table(),
            "gameweeks": Gameweek.objects.filter(completed=True),
            "current_gw": Gameweek.objects.get(id=antifpl.gw),
        }

        return render(request, self.template_name, context_data)


class AntiPreviousPointsTableView(generic.DetailView):
    template_name = "antifpl/points_table.html"

    def get(self, request, *args, **kwargs):
        gw = self.get_object()
        antifpl = Antifpl()
        context_data = {
            "anti_table": PointsTable.objects.filter(gw=gw.id),
            "gameweeks": Gameweek.objects.filter(completed=True),
            "current_gw": gw,
        }

        return render(request, self.template_name, context_data)

    def get_queryset(self):
        return Gameweek.objects.all()


class AntiRulesView(generic.TemplateView):
    template_name = "antifpl/rules.html"


class AntiGWStatsView(generic.View):
    template_name = "antifpl/stats.html"

    def get(self, request, *args, **kwargs):
        antifpl = Antifpl()
        # context_data = {"stats": antifpl.get_footballer_stats()}
        context_data = {
            "player_data": antifpl.get_footballer_stats(),
            "gameweeks": Gameweek.objects.filter(stats_completed=True),
            "current_gw": antifpl.gw,
        }
        return render(request, self.template_name, context_data)


class AntiPrevGWStatsView(generic.DetailView):
    template_name = "antifpl/stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gw = self.get_object()
        context.update(
            {
                "player_data": FootballerPerformanceAnti.objects.filter(gw=gw),
                "gameweeks": Gameweek.objects.filter(stats_completed=True),
                "current_gw": gw.id,
            }
        )
        return context

    def get_queryset(self):
        return Gameweek.objects.all()


class AntiManagerDetailView(generic.DetailView):
    template_name = "antifpl/manager_detail.html"
    context_object_name = "manager"

    def get_queryset(self):
        return Manager.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        manager = self.get_object()

        context.update(
            {"manager_history": PointsTable.objects.filter(manager=manager, gw__gt=0)}
        )
        return context


class FootballerDetailView(generic.DetailView):
    template_name = "antifpl/footballer.html"
    context_object_name = "footballer"

    def get_queryset(self):
        return Footballer.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        footballer = self.get_object()
        context.update(
            {
                "footballer_performance": FootballerPerformanceAnti.objects.filter(
                    footballer=footballer
                )
            }
        )
        return context
