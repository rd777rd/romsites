from django import template

register = template.Library()

@register.filter
def to_review_stars(value, arg):
    return range(value)

@register.filter
def to_review_stars_empty(value, total_stars):
    return range(value, total_stars)
