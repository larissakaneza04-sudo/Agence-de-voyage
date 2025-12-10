from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone

def envoyer_email_confirmation_reservation(reservation):
    """
    Envoie un email de confirmation de réservation au client
    """
    subject = f'Confirmation de votre réservation {reservation.reference}'
    
    # Récupération du nom complet du client
    user = reservation.client.user
    nom_complet = f"{user.first_name} {user.last_name}".strip()
    if not nom_complet:
        nom_complet = user.username
    
    # Préparation du contexte pour le template d'email
    context = {
        'reservation': reservation,
        'client_nom': nom_complet,
        'trajet': f"{reservation.horaire.trajet.depart.ville.nom} → {reservation.horaire.trajet.arrivee.ville.nom}",
        'date_depart': reservation.horaire.date_depart,
        'date_arrivee': reservation.horaire.date_arrivee,
        'montant_total': f"{reservation.montant_total:,.2f}".replace(',', ' ').replace('.', ','),
        'site_url': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
        'contact_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'contact@agence-voyage.com'),
        'contact_phone': getattr(settings, 'CONTACT_PHONE', '+33 1 23 45 67 89'),
        'annee_courante': timezone.now().year
    }
    
    # Rendu du template HTML
    html_message = render_to_string('reservations/emails/confirmation_reservation.html', context)
    
    # Version texte brut du message
    plain_message = strip_tags(html_message)
    
    # Envoi de l'email
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[reservation.client.user.email],
        html_message=html_message,
        fail_silently=False,
    )

def envoyer_email_ticket_bonus(ticket_bonus):
    """
    Envoie un email de notification de ticket bonus au client
    """
    subject = '🎉 Félicitations ! Vous avez gagné un ticket bonus !'
    
    # Récupération du nom complet du client
    user = ticket_bonus.client.user
    nom_complet = f"{user.first_name} {user.last_name}".strip()
    if not nom_complet:
        nom_complet = user.username
    
    # Préparation du contexte pour le template d'email
    context = {
        'ticket': ticket_bonus,
        'client_nom': nom_complet,
        'date_expiration': ticket_bonus.date_expiration,
        'nombre_places': ticket_bonus.nombre_places,
        'code': ticket_bonus.code,
        'site_url': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
        'contact_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'contact@agence-voyage.com'),
        'contact_phone': getattr(settings, 'CONTACT_PHONE', '+33 1 23 45 67 89'),
        'annee_courante': timezone.now().year
    }
    
    # Rendu du template HTML
    html_message = render_to_string('reservations/emails/notification_ticket_bonus.html', context)
    
    # Version texte brut du message
    plain_message = strip_tags(html_message)
    
    # Envoi de l'email
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
