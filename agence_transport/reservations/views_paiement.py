from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone

from .models import Paiement, Reservation
from .forms import PaiementForm

class PaiementCreateView(LoginRequiredMixin, CreateView):
    model = Paiement
    form_class = PaiementForm
    template_name = 'reservations/paiement_create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reservation'] = get_object_or_404(
            Reservation, 
            pk=self.kwargs['pk'], 
            client=self.request.user.client
        )
        return context
    
    def form_valid(self, form):
        reservation = get_object_or_404(
            Reservation, 
            pk=self.kwargs['pk'], 
            client=self.request.user.client
        )
        
        # Créer un paiement factice pour le moment
        paiement = form.save(commit=False)
        paiement.reservation = reservation
        paiement.montant = reservation.montant_total
        paiement.statut = 'EN_ATTENTE'
        paiement.save()
        
        # Mettre à jour le statut de la réservation
        reservation.statut = 'CONFIRMEE'
        reservation.save()
        
        # Envoyer un email de confirmation de réservation
        self.send_confirmation_email(reservation, paiement)
        
        messages.success(
            self.request,
            'Votre réservation a été confirmée ! Un email de confirmation a été envoyé à votre adresse email.'
        )
        return redirect('reservations:reservation-detail', pk=reservation.pk)
    
    def send_confirmation_email(self, reservation, paiement):
        """Envoie un email de confirmation de réservation au client"""
        client = reservation.client
        user = client.user
        
        subject = f'Confirmation de votre réservation {reservation.reference}'
        
        # Création du contenu HTML de l'email
        message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #f8f9fa; padding: 20px; text-align: center;">
                    <h2 style="color: #0d6efd;">Confirmation de réservation</h2>
                </div>
                
                <div style="padding: 20px;">
                    <p>Bonjour {user.first_name} {user.last_name},</p>
                    
                    <p>Nous vous confirmons votre réservation n°<strong>{reservation.reference}</strong> pour le trajet suivant :</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <p><strong>Départ :</strong> {reservation.horaire.trajet.depart.ville.nom} - {reservation.horaire.trajet.depart.nom}</p>
                        <p><strong>Date et heure :</strong> {reservation.horaire.date_depart.strftime('%A %d %B %Y à %H:%M')}</p>
                        <p><strong>Arrivée :</strong> {reservation.horaire.trajet.arrivee.ville.nom} - {reservation.horaire.trajet.arrivee.nom}</p>
                        <p><strong>Date et heure d'arrivée :</strong> {reservation.horaire.date_arrivee.strftime('%A %d %B %Y à %H:%M')}</p>
                    </div>
                    
                    <div style="margin: 20px 0;">
                        <h4>Détails de la réservation :</h4>
                        <p>• Nombre de billets : {reservation.billets.count()}</p>
                        <p>• Montant total : <strong>{reservation.montant_total} €</strong></p>
                        <p>• Statut du paiement : <span style="color: #198754;">En attente</span></p>
                    </div>
                    
                    <p>Vous pouvez consulter les détails de votre réservation en vous connectant à votre <a href="{settings.SITE_URL}/compte/reservations/" style="color: #0d6efd; text-decoration: none;">espace client</a>.</p>
                    
                    <p>Pour toute question, n'hésitez pas à répondre à cet email ou à nous contacter au {settings.CONTACT_PHONE}.</p>
                    
                    <p>Merci d'avoir choisi nos services !</p>
                    
                    <p>Cordialement,<br>L'équipe Agence Transport</p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #6c757d;">
                    <p>© {timezone.now().year} Agence Transport - Tous droits réservés</p>
                </div>
            </body>
        </html>
        """
        
        # Envoyer l'email avec contenu HTML
        send_mail(
            subject=subject,
            message='',  # Le message en texte brut sera vide car on utilise html_message
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=message,
            fail_silently=False,
        )
