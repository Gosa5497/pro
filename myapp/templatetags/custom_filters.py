# myapp/templatetags/custom_filters.py
from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def add_days(date, days):
    return date + timedelta(days=days)

@register.filter
def times(number):
    return range(number)

@register.filter
def get_item(l, index):
    try:
        return l[index]
    except IndexError:
        return None
@register.filter
def divided_by(value, divisor):
    try:
        return int(value) // int(divisor)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def div(value, arg):
    try:
        return int(value) // int(arg)
    except (ValueError, ZeroDivisionError):
        return 0
from django import template

register = template.Library()

@register.filter
def split_by(value, delimiter=','):
    """Split a string by a given delimiter."""
    if not value:
        return []
    return [item.strip() for item in value.split(delimiter)]
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
from django import template

register = template.Library()

@register.filter
def div(value, divisor):
    try:
        return int(value) // int(divisor)
    except (ValueError, ZeroDivisionError):
        return 0
