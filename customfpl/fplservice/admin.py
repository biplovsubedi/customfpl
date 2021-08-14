from django.contrib import admin
from fplservice.models import Footballer, Gameweek, Position, TeamMeta

from fplservice.filters import DropdownFilter

# Register your models here.


@admin.display(description="Name", ordering="cost")
def footballer_display(obj):
    return f"{obj.name} ({obj.team} - {obj.cost})"


class FootballerAdmin(admin.ModelAdmin):
    list_filter = [
        ("team__name", DropdownFilter),
        ("position__name", DropdownFilter),
    ]
    list_display = (footballer_display,)
    search_fields = (
        "name",
        "team__name",
        "yellow_cards",
        "red_cards",
    )


admin.site.register(Gameweek)
admin.site.register(TeamMeta)
admin.site.register(Position)
admin.site.register(Footballer, FootballerAdmin)
