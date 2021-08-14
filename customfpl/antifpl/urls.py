from django.urls import path
from antifpl.views import (
    AntiGWStatsView,
    AntiManagerDetailView,
    AntiPointsTableView,
    AntiPrevGWStatsView,
    AntiPreviousPointsTableView,
    AntiRulesView,
    FootballerDetailView,
)

app_name = "antifpl"

urlpatterns = [
    path("", AntiPointsTableView.as_view(), name="points-table"),
    path(
        "points/<int:pk>/",
        AntiPreviousPointsTableView.as_view(),
        name="prev-points-table",
    ),
    path(
        "manager/<int:pk>/",
        AntiManagerDetailView.as_view(),
        name="manager",
    ),
    path(
        "footballer/<int:pk>/",
        FootballerDetailView.as_view(),
        name="footballer",
    ),
    path("rules/", AntiRulesView.as_view(), name="rules"),
    path("gw-stats/", AntiGWStatsView.as_view(), name="gw-stats"),
    path("gw-stats/<int:pk>/", AntiPrevGWStatsView.as_view(), name="prev-gw-stats"),
]
