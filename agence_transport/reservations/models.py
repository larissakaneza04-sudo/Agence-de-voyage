from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

class Ville(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return f"{self.nom} ({self.code})"

class Gare(models.Model):
    nom = models.CharField(max_length=100)
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE, related_name='gares')
    adresse = models.TextField()
    
    class Meta:
        unique_together = ('nom', 'ville')
        
    def __str__(self):
        return f"{self.nom} - {self.ville.nom}"

class Trajet(models.Model):
    depart = models.ForeignKey(Gare, on_delete=models.CASCADE, related_name='departs')
    arrivee = models.ForeignKey(Gare, on_delete=models.CASCADE, related_name='arrivees')
    duree = models.DurationField()
    distance = models.PositiveIntegerField(help_text="Distance en kilomètres")
    actif = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('depart', 'arrivee')
        
    def __str__(self):
        return f"{self.depart} → {self.arrivee} ({self.duree})"

class Horaire(models.Model):
    trajet = models.ForeignKey(Trajet, on_delete=models.CASCADE, related_name='horaires')
    date_depart = models.DateTimeField()
    date_arrivee = models.DateTimeField()
    
    # Prix pour chaque type de billet
    prix_standard = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name="Prix Standard (BIF)"
    )
    prix_business = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name="Prix Business (BIF)"
    )
    prix_premiere = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name="Prix Première Classe (BIF)"
    )
    
    # Places disponibles pour chaque type de billet
    places_standard = models.PositiveIntegerField(verbose_name="Places Standard")
    places_business = models.PositiveIntegerField(verbose_name="Places Business")
    places_premiere = models.PositiveIntegerField(verbose_name="Places Première Classe")
    
    class Meta:
        ordering = ['date_depart']
        verbose_name = "Horaire"
        verbose_name_plural = "Horaires"
        
    def __str__(self):
        return f"{self.trajet} - {self.date_depart.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def places_disponibles_total(self):
        """Retourne le nombre total de places disponibles"""
        return self.places_standard + self.places_business + self.places_premiere
    
    def get_prix_par_type(self, type_billet):
        """Retourne le prix en fonction du type de billet"""
        prix_par_type = {
            'STD': self.prix_standard,
            'BUS': self.prix_business,
            'PRE': self.prix_premiere,
        }
        return prix_par_type.get(type_billet, self.prix_standard)
    
    def get_places_disponibles(self, type_billet):
        """Retourne le nombre de places disponibles pour un type de billet"""
        places_par_type = {
            'STD': self.places_standard,
            'BUS': self.places_business,
            'PRE': self.places_premiere,
        }
        return places_par_type.get(type_billet, 0)
        
    def get_prix_min(self):
        """Retourne le prix minimum parmi les classes disponibles"""
        prix_disponibles = []
        
        if self.places_standard > 0:
            prix_disponibles.append(self.prix_standard)
        if self.places_business > 0:
            prix_disponibles.append(self.prix_business)
        if self.places_premiere > 0:
            prix_disponibles.append(self.prix_premiere)
            
        return min(prix_disponibles) if prix_disponibles else 0

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    date_naissance = models.DateField(blank=True, null=True)
    points_fidelite = models.PositiveIntegerField(default=0)
    places_reservees = models.PositiveIntegerField(default=0, help_text="Nombre total de places réservées")
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"
        
    def verifier_bonus_places(self, nombre_places=5):
        """
        Vérifie si le client a atteint le nombre de places nécessaires pour un bonus
        Retourne le nombre de tickets bonus gagnés
        """
        tickets_gagnes = 0
        # Vérifier si le client a atteint le seuil de 5 places
        if self.places_reservees >= nombre_places:
            tickets_gagnes = self.places_reservees // nombre_places
            self.places_reservees = self.places_reservees % nombre_places
            self.save()
        return tickets_gagnes
    
    def ajouter_reservation(self, nombre_places):
        """
        Ajoute le nombre de places réservées et vérifie si un bonus est gagné
        Retourne le nombre de tickets bonus gagnés (0 ou 1)
        """
        self.places_reservees += nombre_places
        self.save()
        return self.verifier_bonus_places()

class Reservation(models.Model):
    class StatutReservation(models.TextChoices):
        CONFIRMEE = 'CONF', _('Confirmée')
        ANNULEE = 'ANNU', _('Annulée')
        UTILISEE = 'UTIL', _('Utilisée')
        REMBOURSEE = 'REMB', _('Remboursée')
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reservations')
    horaire = models.ForeignKey(Horaire, on_delete=models.PROTECT, related_name='reservations')
    date_reservation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(
        max_length=4,
        choices=StatutReservation.choices,
        default=StatutReservation.CONFIRMEE
    )
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=10, unique=True)
    
    class Meta:
        ordering = ['-date_reservation']
        
    def __str__(self):
        return f"Réservation {self.reference} - {self.client}"
        
    def get_display_status(self):
        """
        Retourne le statut à afficher en fonction de la date de départ et du statut actuel
        """
        now = timezone.now()
        
        # Si la réservation est annulée, remboursée ou échouée, on affiche ce statut
        if self.statut in [self.StatutReservation.ANNULEE, 
                          self.StatutReservation.REMBOURSEE]:
            return self.get_statut_display()
        elif self.statut == 'FAIL':
            return 'Échoué'
            
        # Pour les réservations confirmées ou utilisées, on vérifie la date
        if self.horaire.date_depart > now:
            # Date de départ dans le futur
            return 'À venir'
        else:
            # Date de départ dans le passé
            if self.statut == self.StatutReservation.UTILISEE:
                return 'Effectué'
            else:
                return 'Passé'
    
    def get_status_badge_class(self):
        """
        Retourne la classe CSS à utiliser pour le badge de statut
        """
        now = timezone.now()
        
        # Si la réservation est annulée, remboursée ou échouée
        if self.statut == self.StatutReservation.ANNULEE:
            return 'secondary'  # Gris pour les réservations annulées
        elif self.statut == self.StatutReservation.REMBOURSEE:
            return 'info'  # Bleu clair pour les remboursements
        elif self.statut == 'FAIL':  # Si jamais ce statut est utilisé
            return 'danger'  # Rouge pour les échecs
            
        # Pour les réservations confirmées ou utilisées, on vérifie la date
        if self.horaire.date_depart > now:
            # Date de départ dans le futur
            if self.statut == self.StatutReservation.CONFIRMEE:
                return 'primary'  # Bleu pour les réservations à venir
            elif self.statut == self.StatutReservation.UTILISEE:
                return 'primary'  # Bleu pour les réservations marquées comme utilisées (cas inhabituel pour une date future)
        else:
            # Date de départ dans le passé
            if self.statut == self.StatutReservation.UTILISEE:
                return 'success'  # Vert pour les trajets effectués
            else:
                return 'warning'  # Jaune/Orange pour les trajets passés non marqués comme utilisés
                
        # Par défaut, on retourne une classe secondaire
        return 'secondary'

class Billet(models.Model):
    class TypeBillet(models.TextChoices):
        STANDARD = 'STD', _('Standard')
        PREMIERE = 'PRE', _('Première Classe')
        BUSINESS = 'BUS', _('Business')
    
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='billets')
    type_billet = models.CharField(
        max_length=3,
        choices=TypeBillet.choices,
        default=TypeBillet.STANDARD
    )
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    siege = models.CharField(max_length=10)
    code_qr = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    
    def __str__(self):
        return f"Billet {self.id} - {self.get_type_billet_display()}"

class Paiement(models.Model):
    class StatutPaiement(models.TextChoices):
        PENDING = 'PEND', _('En attente')
        PAID = 'PAID', _('Payé')
        FAILED = 'FAIL', _('Échoué')
        REFUNDED = 'REFD', _('Remboursé')
    
    class OperateurPaiement(models.TextChoices):
        LUMICASH = 'lumicash', 'Lumicash'
        ECOCASH = 'ecocash', 'Ecocash'
        IHELA = 'ihela', 'Ihela'
        PAYPAL = 'paypal', 'PayPal'
        CARTE = 'carte', 'Carte bancaire'
    
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='paiement')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(
        max_length=4,
        choices=StatutPaiement.choices,
        default=StatutPaiement.PENDING
    )
    operateur = models.CharField(
        max_length=20,
        choices=OperateurPaiement.choices,
        null=True,
        blank=True
    )
    reference_paiement = models.CharField(max_length=100, blank=True, null=True)
    numero_telephone = models.CharField(max_length=20, blank=True, null=True)
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"Paiement {self.get_statut_display()} - {self.montant}€ - {self.operateur or 'Non spécifié'} - {self.reservation}"

class Remboursement(models.Model):
    paiement = models.OneToOneField(Paiement, on_delete=models.CASCADE, related_name='remboursement')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_demande = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(blank=True, null=True)
    motif = models.TextField()
    traite = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Remboursement {self.id} - {self.montant}€"

import uuid
from datetime import timedelta

class TicketBonus(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='tickets_bonus')
    montant = models.DecimalField(max_digits=10, decimal_places=2, help_text="Montant du bon de réduction")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateTimeField(help_text="Date d'expiration du ticket (30 jours après création)")
    utilise = models.BooleanField(default=False)
    code = models.CharField(max_length=20, unique=True, default=uuid.uuid4, editable=False)
    nombre_places = models.PositiveIntegerField(default=1, help_text="Nombre de places offertes par ce ticket")
    
    def save(self, *args, **kwargs):
        # Si c'est une nouvelle instance, définir la date d'expiration à 30 jours
        if not self.id:
            self.date_expiration = timezone.now() + timedelta(days=30)
            # Générer un code unique si non fourni
            if not self.code:
                self.code = f"BONUS-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def est_valide(self):
        """Vérifie si le ticket est valide (non utilisé et non expiré)"""
        return not self.utilise and self.date_expiration > timezone.now()
    
    def utiliser(self):
        """Marque le ticket comme utilisé"""
        if self.est_valide():
            self.utilise = True
            self.save()
            return True
        return False
    
    @classmethod
    def creer_ticket_bonus(cls, client, montant=0, nombre_places=1):
        """
        Crée un nouveau ticket bonus pour un client et envoie une notification par email
        """
        ticket = cls.objects.create(
            client=client,
            montant=montant,
            nombre_places=nombre_places
        )
        
        # Envoyer un email de notification de manière asynchrone
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from django.conf import settings
        from django.utils import timezone
        
        try:
            user = client.user
            subject = '🎉 Félicitations ! Vous avez gagné un ticket bonus !'
            
            context = {
                'ticket': ticket,
                'client_nom': f"{user.first_name} {user.last_name}".strip() or user.username,
                'date_expiration': ticket.date_expiration,
                'nombre_places': ticket.nombre_places,
                'code': ticket.code,
                'site_url': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
                'contact_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'contact@agence-voyage.com'),
                'contact_phone': getattr(settings, 'CONTACT_PHONE', '+33 1 23 45 67 89'),
                'annee_courante': timezone.now().year
            }
            
            html_message = render_to_string('reservations/emails/notification_ticket_bonus.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception as e:
            # En cas d'erreur d'envoi d'email, on ne fait rien pour ne pas perturber le flux
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erreur lors de l'envoi de l'email de ticket bonus: {str(e)}")
        
        return ticket
    
    def __str__(self):
        return f"Ticket Bonus {self.code} - {self.nombre_places} place(s) offerte(s) - {'Valide' if self.est_valide() else 'Expiré'}"
