from django import template
from ..constants import CURRENCY, CURRENCY_SYMBOL, EXCHANGE_RATE_EUR

# Création d'une instance de Library
register = template.Library()

@register.filter(name='currency')
def currency(value):
    """
    Formate un montant avec le symbole de la devise
    Exemple: {{ 15000|currency }} -> 15 000 Fbu
    """
    if value is None or value == '':
        return f"0 {CURRENCY_SYMBOL}"
    try:
        # Convertit en entier et formate avec des espaces comme séparateurs de milliers
        return f"{int(value):,} {CURRENCY_SYMBOL}".replace(',', ' ')
    except (ValueError, TypeError):
        return f"0 {CURRENCY_SYMBOL}"

@register.filter(name='to_eur')
def to_eur(value):
    """
    Convertit un montant en euros
    Exemple: {{ 15000|to_eur }} -> 5.00 €
    """
    if not value or not EXCHANGE_RATE_EUR:
        return "0.00 €"
    try:
        return f"{float(value) / EXCHANGE_RATE_EUR:.2f} €"
    except (ValueError, TypeError):
        return "0.00 €"
