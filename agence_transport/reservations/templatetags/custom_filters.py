from django import template

register = template.Library()

@register.filter(name='format_currency')
def format_currency(value):
    """
    Formate un montant avec le symbole de la devise
    Exemple: {{ 15000|format_currency }} -> 15 000 BIF
    """
    if value is None or value == '':
        return "0 BIF"
    try:
        # Convertit en entier et formate avec des espaces comme séparateurs de milliers
        return f"{int(value):,} BIF".replace(',', ' ')
    except (ValueError, TypeError):
        return "0 BIF"
