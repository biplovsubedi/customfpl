from django.shortcuts import render
from django.views import generic

from .lib import Antifpl

# Create your views here.


class AntiPointsTableView(generic.View):
    template_name = "antifpl/points_table.html"

    def get(self, request, *args, **kwargs):

        antifpl = Antifpl()
        context_data = {"anti_table": antifpl.get_data()}

        return render(request, self.template_name, context_data)
