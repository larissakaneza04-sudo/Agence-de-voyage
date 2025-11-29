from django.urls import path
from django.views.generic import TemplateView
from . import views
from .views import SearchView
from .views_paiement import PaiementCreateView

app_name = 'reservations'

urlpatterns = [
    # Pages publiques
    path('', views.HomeView.as_view(), name='home'),
    path('rechercher/', SearchView.as_view(), name='search'),
    path('a-propos/', TemplateView.as_view(template_name='reservations/a_propos.html'), name='a-propos'),
    path('contact/', TemplateView.as_view(template_name='reservations/contact.html'), name='contact'),
    path('mentions-legales/', TemplateView.as_view(template_name='reservations/mentions_legales.html'), name='mentions-legales'),
    path('cgu/', TemplateView.as_view(template_name='reservations/cgu.html'), name='cgu'),
    
    # Gestion des comptes
    path('compte/', views.MesReservationsView.as_view(), name='mon-compte'),
    path('compte/reservations/', views.MesReservationsView.as_view(), name='mes-reservations'),
    path('compte/profil/', views.ProfilUpdateView.as_view(), name='profil'),
    
    # Réservations
    path('horaires/<int:pk>/', views.HoraireDetailView.as_view(), name='horaire-detail'),
    path('reservations/nouvelle/<int:pk>/', views.ReservationCreateView.as_view(), name='reservation-create'),
    path('reservations/<int:pk>/', views.ReservationDetailView.as_view(), name='reservation-detail'),
    path('reservations/<int:pk>/annuler/', views.ReservationAnnulerView.as_view(), name='reservation-annuler'),
    path('reservations/<int:pk>/paiement/', PaiementCreateView.as_view(), name='paiement-create'),
    path('reservations/<int:pk>/remboursement/', views.RemboursementDemandeView.as_view(), name='demande-remboursement'),
    
    # API Endpoints (AJAX)
    path('api/gares-par-ville/<int:ville_id>/', views.get_gares_par_ville, name='api-gares-par-ville'),
    path('api/trajets-par-gares/', views.get_trajets_par_gares, name='api-trajets-par-gares'),
    
    # Espace administrateur
    path('admin/reservations/', views.GestionReservationsView.as_view(), name='gestion-reservations'),
    path('admin/remboursements/', views.GestionRemboursementsView.as_view(), name='gestion-remboursements'),
    path('admin/remboursements/<int:pk>/traiter/', views.TraiterRemboursementView.as_view(), name='traiter-remboursement'),
]
