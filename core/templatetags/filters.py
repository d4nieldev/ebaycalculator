from django import template

register = template.Library()

@register.filter(name='roundFloat')
def round_float(value, arg):
    return format(value, '.' + str(arg) + 'f').rstrip('0').rstrip('.')
