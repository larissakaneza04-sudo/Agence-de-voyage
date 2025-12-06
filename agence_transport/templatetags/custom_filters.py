from django import template
from datetime import datetime, timedelta
import re

register = template.Library()

@register.filter
def duration_format(start, end):
    if not start or not end:
        return "Non spécifié"
        
    # Calculer la différence
    delta = end - start
    
    # Extraire les heures et minutes
    total_seconds = int(delta.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    
    # Formater la durée
    if hours > 0 and minutes > 0:
        return f"{hours}h {minutes:02d}min"
    elif hours > 0:
        return f"{hours}h"
    else:
        return f"{minutes}min"
