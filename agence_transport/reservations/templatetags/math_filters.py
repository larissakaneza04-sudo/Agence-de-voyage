from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    """Soustrait l'argument de la valeur"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        try:
            return value - arg
        except Exception:
            return ''

@register.filter
def mul(value, arg):
    """Multiplie la valeur par l'argument"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        try:
            return value * arg
        except Exception:
            return ''
