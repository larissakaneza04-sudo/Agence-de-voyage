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
    prix_base = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    places_disponibles = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['date_depart']
        
    def __str__(self):
        return f"{self.trajet} - {self.date_depart.strftime('%d/%m/%Y %H:%M')}"

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    date_naissance = models.DateField(blank=True, null=True)
    points_fidelite = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

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

class TicketBonus(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='tickets_bonus')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateTimeField()
    utilise = models.BooleanField(default=False)
    code = models.CharField(max_length=20, unique=True)
    
    def est_valide(self):
        return not self.utilise and self.date_expiration > timezone.now()
    
    def __str__(self):
        return f"Ticket Bonus {self.code} - {self.montant}€"
