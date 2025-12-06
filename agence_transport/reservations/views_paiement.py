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
        
        try:
            # Envoyer un email de confirmation de réservation
            self.send_confirmation_email(reservation, paiement)
        except Exception as e:
            # Enregistrer l'erreur mais continuer le processus
            print(f"Erreur lors de l'envoi de l'email: {str(e)}")
            messages.warning(
                self.request,
                'Votre réservation a été confirmée, mais nous n\'avons pas pu envoyer l\'email de confirmation.'
            )
        
        messages.success(
            self.request,
            'Votre réservation a été confirmée ! Un email de confirmation a été envoyé à votre adresse email.'
        )
        return redirect('reservations:reservation-detail', pk=reservation.pk)
    
    def send_confirmation_email(self, reservation, paiement):
        """Envoie un email de confirmation de réservation au client"""
        from django.core.mail import EmailMultiAlternatives
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from email.utils import formataddr
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            client = reservation.client
            user = client.user
            
            # Préparer le contexte pour le template d'email
            context = {
                'reservation': reservation,
                'user': user,
                'site_url': settings.SITE_URL,
                'contact_phone': getattr(settings, 'CONTACT_PHONE', ''),
                'current_year': timezone.now().year,
                'DEFAULT_FROM_EMAIL': settings.DEFAULT_FROM_EMAIL,
            }
            
            # Charger le contenu HTML du template
            html_content = render_to_string('reservations/emails/confirmation_reservation.html', context)
            
            # Créer une version texte brut du contenu HTML en remplaçant les caractères spéciaux
            text_content = strip_tags(html_content)
            # Remplacer les entités HTML par leurs équivalents texte
            text_content = text_content.replace('&rarr;', '->').replace('&eacute;', 'e').replace('&apos;', "'")
            
            # Nettoyer le contenu HTML des caractères problématiques
            html_content = html_content.replace('\u2019', "'").replace('\u2013', '-').replace('\u2014', '--')
            
            # Créer l'email avec l'encodage UTF-8 explicite
            subject = f'Confirmation de votre réservation {reservation.reference}'
            from_email = formataddr(('Larissa Inspiration Spirit Travel', settings.DEFAULT_FROM_EMAIL))
            to = [user.email]
            
            # Créer le message avec les deux versions (texte et HTML)
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=to,
                reply_to=[from_email],
                headers={
                    'Content-Type': 'text/plain; charset=utf-8',
                    'Content-Transfer-Encoding': 'quoted-printable',
                    'MIME-Version': '1.0',
                }
            )
            
            # Ajouter la version HTML avec l'encodage spécifié
            msg.attach_alternative(html_content, 'text/html; charset=utf-8')
            
            # Configurer l'encodage du message
            msg.encoding = 'utf-8'
            
            # Envoyer l'email
            msg.send(fail_silently=False)
            
            logger.info(f"Email de confirmation envoyé avec succès à {user.email} pour la réservation {reservation.reference}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email de confirmation pour la réservation {reservation.reference}: {str(e)}", 
                        exc_info=True, stack_info=True)
            raise  # Relancer l'erreur pour la gérer dans la vue
