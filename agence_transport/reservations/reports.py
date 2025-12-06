from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Reservation, Paiement
from .forms import FiltreRapportForm
from django.contrib import messages

@login_required
def rapports_ventes(request):
    if not request.user.is_staff:
        messages.error(request, "Accès refusé. Vous n'avez pas les droits nécessaires.")
        return redirect('reservations:home')
    
    # Initialiser le formulaire avec les données de la requête
    form = FiltreRapportForm(request.GET or None)
    
    # Définir les dates par défaut (30 derniers jours)
    date_fin = timezone.now()
    date_debut = date_fin - timedelta(days=30)
    
    # Si le formulaire est valide, utiliser les dates sélectionnées
    if form.is_bound and form.is_valid():
        date_debut = form.cleaned_data.get('date_debut')
        date_fin = form.cleaned_data.get('date_fin')
        
        # Si les deux dates sont fournies, les utiliser
        if date_debut and date_fin:
            # Ajouter un jour à la date de fin pour inclure toute la journée
            date_fin = date_fin + timedelta(days=1)
        else:
            # Sinon, utiliser les dates par défaut (30 derniers jours)
            date_fin = timezone.now()
            date_debut = date_fin - timedelta(days=30)
    
    # Récupérer les réservations selon la période sélectionnée
    reservations = Reservation.objects.filter(
        date_reservation__gte=date_debut,
        date_reservation__lte=date_fin,
        statut__in=[Reservation.StatutReservation.CONFIRMEE, Reservation.StatutReservation.UTILISEE]
    )
    
    # Grouper par jour et calculer le total
    ventes_par_jour = reservations.extra(
        {'date': "date(date_reservation)"}
    ).values('date').annotate(
        total=Sum('montant_total'),
        nombre_reservations=Count('id')
    ).order_by('date')
    
    # Préparer les données pour le graphique
    dates = []
    montants = []
    for vente in ventes_par_jour:
        # Convertir la date en chaîne de caractères si ce n'est pas déjà fait
        date_str = vente['date'].strftime('%Y-%m-%d') if hasattr(vente['date'], 'strftime') else vente['date']
        dates.append(date_str)
        montants.append(float(vente['total'] or 0))
    
    # Calculer le total général
    total_general = sum(montants)
    nombre_total_reservations = sum(vente['nombre_reservations'] for vente in ventes_par_jour)
    
    # Calculer le total des paiements par méthode de paiement
    paiements_par_methode = Paiement.objects.filter(
        date_paiement__gte=date_debut,
        statut=Paiement.StatutPaiement.PAID
    ).values('operateur').annotate(
        total=Sum('montant'),
        nombre=Count('id')
    ).order_by('-total')
    
    # Ajuster la date de fin pour l'affichage (on enlève le jour ajouté précédemment)
    date_fin_affichage = date_fin - timedelta(days=1) if form.is_bound and form.is_valid() and form.cleaned_data.get('date_fin') else date_fin
    
    context = {
        'form': form,
        'ventes_par_jour': ventes_par_jour,
        'total_general': total_general,
        'nombre_total_reservations': nombre_total_reservations,
        'paiements_par_methode': paiements_par_methode,
        'dates': dates,
        'montants': montants,
        'periode_debut': date_debut.strftime('%d/%m/%Y'),
        'periode_fin': date_fin_affichage.strftime('%d/%m/%Y'),
    }
    
    return render(request, 'reservations/rapports/ventes.html', context)
