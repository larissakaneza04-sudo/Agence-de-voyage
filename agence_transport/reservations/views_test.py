from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context

def test_currency_filter(request):
    # Création d'un contexte avec une valeur de test
    context = {
        'test_value': 15000,
    }
    
    # Chargement du template avec le filtre
    template = get_template('reservations/test_filter.html')
    
    # Rendu du template avec le contexte
    rendered = template.render(context)
    
    # Retourne le résultat du rendu
    return HttpResponse(rendered)
