from django.urls import path
from antifpl.views import AntiPointsTableView

app_name = "antifpl"

urlpatterns = [path("", AntiPointsTableView.as_view(), name="anti-home")]
