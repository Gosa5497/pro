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
@register.filter
def subtract(value, arg):
    try:
        return int(value) - int(arg)
    except (TypeError, ValueError):
        return 0
@register.filter
def get_item(dictionary, key):
    """Returns an item from the dictionary by its key."""
    return dictionary.get(key)
