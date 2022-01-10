from django import template

register = template.Library()


@register.simple_tag
def expand_list(items: list):
    item1, item2 = items
    return item1, item2
