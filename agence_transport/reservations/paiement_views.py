from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone

from .models import Reservation, Paiement
from .forms import PaiementForm

class ChoixPaiementView(TemplateView):
    template_name = 'reservations/choix_paiement.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reservation = get_object_or_404(Reservation, pk=self.kwargs['pk'])
        context['reservation'] = reservation
        
        # Options de paiement disponibles
        context['paiement_options'] = [
            {'code': 'lumicash', 'nom': 'Lumicash', 'logo': 'img/paiement/lumicash.png'},
            {'code': 'ecocash', 'nom': 'Ecocash', 'logo': 'img/paiement/ecocash.png'},
            {'code': 'ihela', 'nom': 'Ihela', 'logo': 'img/paiement/ihela.png'},
            {'code': 'paypal', 'nom': 'PayPal', 'logo': 'img/paiement/paypal.png'},
            {'code': 'carte', 'nom': 'Carte bancaire', 'logo': 'img/paiement/carte.png'},
        ]
        
        return context

    def post(self, request, *args, **kwargs):
        reservation = get_object_or_404(Reservation, pk=self.kwargs['pk'])
        mode_paiement = request.POST.get('mode_paiement')
        
        if not mode_paiement:
            messages.error(request, "Veuillez sélectionner un mode de paiement.")
            return self.get(request, *args, **kwargs)
        
        # Enregistrer le choix du mode de paiement
        reservation.mode_paiement = mode_paiement
        reservation.save()
        
        # Rediriger vers la page de traitement du paiement correspondant
        if mode_paiement in ['lumicash', 'ecocash', 'ihela']:
            return redirect('reservations:paiement-mobile', pk=reservation.pk, operateur=mode_paiement)
        elif mode_paiement == 'paypal':
            return redirect('reservations:paiement-paypal', pk=reservation.pk)
        else:  # carte bancaire
            return redirect('reservations:paiement-carte', pk=reservation.pk)


class PaiementMobileView(TemplateView):
    template_name = 'reservations/paiement_mobile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reservation = get_object_or_404(Reservation, pk=self.kwargs['pk'])
        operateur = self.kwargs['operateur']
        
        context.update({
            'reservation': reservation,
            'operateur': operateur,
            'operateur_nom': dict(Paiement.OPERATEUR_CHOICES).get(operateur, operateur.capitalize()),
            'montant': f"{reservation.montant_total:,.2f}".replace(',', ' ').replace('.', ',')
        })
        return context
    
    def post(self, request, *args, **kwargs):
        reservation = get_object_or_404(Reservation, pk=self.kwargs['pk'])
        numero = request.POST.get('numero')
        
        # Ici, vous intégrerez l'API de paiement réelle
        # Pour l'instant, on simule un paiement réussi
        
        # Créer un enregistrement de paiement
        Paiement.objects.create(
            reservation=reservation,
            montant=reservation.montant_total,
            operateur=self.kwargs['operateur'],
            statut='VALIDE',
            date_paiement=timezone.now(),
            reference=f"PAY-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        )
        
        # Mettre à jour le statut de la réservation
        reservation.statut = 'PAYE'
        reservation.save()
        
        messages.success(request, "Paiement effectué avec succès !")
        return redirect('reservations:reservation-detail', pk=reservation.pk)
