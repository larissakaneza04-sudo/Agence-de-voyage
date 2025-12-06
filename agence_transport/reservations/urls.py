from django.urls import path
from django.views.generic import TemplateView
from . import views
from .views import SearchView, ajouter_ville, ajouter_trajet, ajouter_horaire, ajouter_gare
from .views_paiement import PaiementCreateView
from .reports import rapports_ventes

app_name = 'reservations'

urlpatterns = [
    # Pages publiques
    path('', views.HomeView.as_view(), name='home'),
    path('rechercher/', SearchView.as_view(), name='search'),
    path('a-propos/', TemplateView.as_view(template_name='reservations/a_propos.html'), name='a-propos'),
    path('contact/', views.ContactView.as_view(), name='contact'),
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
    
    # Gestion des villes
    path('villes/', views.VilleListView.as_view(), name='ville-list'),
    path('villes/ajouter/', ajouter_ville, name='ville-ajouter'),
    path('villes/<int:pk>/modifier/', views.VilleUpdateView.as_view(), name='ville-update'),
    path('villes/<int:pk>/supprimer/', views.VilleDeleteView.as_view(), name='ville-delete'),
    
    # Gestion des trajets
    path('trajets/', views.TrajetListView.as_view(), name='trajet-list'),
    path('trajets/ajouter/', ajouter_trajet, name='trajet-ajouter'),
    path('trajets/<int:pk>/modifier/', views.TrajetUpdateView.as_view(), name='trajet-update'),
    path('trajets/<int:pk>/supprimer/', views.TrajetDeleteView.as_view(), name='trajet-delete'),
    
    # Gestion des gares
    path('gares/', views.GareListView.as_view(), name='gare-list'),
    path('gares/ajouter/', ajouter_gare, name='gare-ajouter'),
    path('gares/<int:pk>/modifier/', views.GareUpdateView.as_view(), name='gare-update'),
    path('gares/<int:pk>/supprimer/', views.GareDeleteView.as_view(), name='gare-delete'),
    
    # Gestion des horaires
    path('horaires/', views.HoraireListView.as_view(), name='horaire-list'),
    path('horaires/ajouter/', ajouter_horaire, name='horaire-ajouter'),
    path('horaires/<int:pk>/modifier/', views.HoraireUpdateView.as_view(), name='horaire-update'),
    path('horaires/<int:pk>/supprimer/', views.HoraireDeleteView.as_view(), name='horaire-delete'),
    
    # Rapports
    path('rapports/ventes/', rapports_ventes, name='rapports-ventes'),
]
