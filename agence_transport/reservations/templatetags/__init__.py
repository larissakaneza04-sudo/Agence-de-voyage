"""
Ce module contient les filtres personnalisés pour les templates Django.
Il est nécessaire pour que Django puisse charger les filtres définis dans ce package.
"""

# Import des filtres personnalisés
from .currency_filters import register as currency_register
from .custom_filters import register as custom_register

# Cette variable est nécessaire pour que Django reconnaisse les filtres personnalisés
register = currency_register

# Pour éviter les avertissements de l'éditeur
__all__ = ['currency_register', 'custom_register']
