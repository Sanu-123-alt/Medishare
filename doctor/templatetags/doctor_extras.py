from django import template

register = template.Library()

@register.filter
def to_list(value):
    """Convert a comma-separated string to a list"""
    if not value:
        return []
    return [item.strip() for item in value.split(',') if item.strip()]