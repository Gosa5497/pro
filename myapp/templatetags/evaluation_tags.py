# templatetags/evaluation_tags.py
from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def divide(value, arg):
    try:
        return int(value) / int(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def add_days(date, days):
    try:
        return date + timedelta(days=int(days))
    except (TypeError, ValueError):
        return date