from django.contrib.admin.filters import AllValuesFieldListFilter

class DropdownFilter(AllValuesFieldListFilter):
    template = "admin_dropdown_filter.html"
