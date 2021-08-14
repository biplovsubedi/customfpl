from django import template
from django.template.defaulttags import register

register = template.Library()


@register.filter
def remove_zero(val):
    return "" if val == 0 else val


@register.filter
def normalize_team_value(val):
    return val / 10.0
