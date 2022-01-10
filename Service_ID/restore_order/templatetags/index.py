from django import template

register = template.Library()


@register.filter
def index(_list, i):
    return _list[i]


@register.filter
def index_minus_1(_list, i):
    return _list[i - 1]

