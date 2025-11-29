"""
URL configuration for agence_transport project.

Inclut les configurations URL pour l'administration Django et l'application de réservation.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

# Configuration des URLs principales
urlpatterns = [
    # URL de l'administration Django
    path('admin/', admin.site.urls),
    
    # URL de l'application de réservation
    path('', include('reservations.urls', namespace='reservations')),
    
    # URL d'authentification (django-allauth)
    path('compte/', include('allauth.urls')),
    
    # Redirection de la racine vers la page d'accueil
    path('', RedirectView.as_view(pattern_name='reservations:home', permanent=False)),
]

# Configuration pour servir les fichiers média en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Outils de débogage
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Configuration des pages d'erreur personnalisées
handler403 = 'reservations.views.handler403'
handler404 = 'reservations.views.handler404'
handler500 = 'reservations.views.handler500'
