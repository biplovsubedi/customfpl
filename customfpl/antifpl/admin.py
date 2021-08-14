from django.contrib import admin
from antifpl.models import FootballerPerformanceAnti, Manager, PointsTable
from fplservice.filters import DropdownFilter

# Register your models here.


class PointsTableAdmin(admin.ModelAdmin):
    list_filter = [
        ("manager__team_name", DropdownFilter),
        ("gw", DropdownFilter),
    ]

    search_fields = (
        "manager__team_name",
        "manager_manager__name",
    )


admin.site.register(PointsTable, PointsTableAdmin)
admin.site.register(Manager)
admin.site.register(FootballerPerformanceAnti)
