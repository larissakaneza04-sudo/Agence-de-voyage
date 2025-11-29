from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator
from .models import Billet, Client, Paiement, Reservation, Ville, Gare, Trajet, Horaire, Remboursement, TicketBonus

class ClientForm(forms.Form):
    """
    Formulaire pour les informations client et utilisateur.
    Utilise des champs personnalisés qui ne sont pas liés directement au modèle Client.
    """
    prenom = forms.CharField(
        label='Prénom',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre prénom'}),
        required=True
    )
    nom = forms.CharField(
        label='Nom',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}),
        required=True
    )
    email = forms.EmailField(
        label='Adresse email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'votre@email.com'}),
        required=True
    )
    telephone = forms.CharField(
        label='Téléphone',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre numéro de téléphone'}),
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pré-remplir avec les données de l'utilisateur connecté si disponible
        if self.user and self.user.is_authenticated:
            self.fields['prenom'].initial = self.user.first_name
            self.fields['nom'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
            
            # Essayer de récupérer le numéro de téléphone du client s'il existe
            if hasattr(self.user, 'client'):
                self.fields['telephone'].initial = self.user.client.telephone

class ReservationForm(forms.Form):
    """
    Formulaire pour les informations de réservation.
    Ce formulaire gère la création des billets associés à la réservation.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Définir les choix pour le type de billet
        self.fields['type_billet'] = forms.ChoiceField(
            label='Type de billet',
            choices=Billet.TypeBillet.choices,
            widget=forms.Select(attrs={'class': 'form-select'}),
            required=True
        )
        self.fields['nombre_billets'] = forms.IntegerField(
            label='Nombre de billets',
            min_value=1,
            max_value=10,
            widget=forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'id_nombre_billets'
            }),
            required=True
        )
        self.fields['commentaires'] = forms.CharField(
            label='Commentaires',
            widget=forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Commentaires ou demandes spéciales...'
            }),
            required=False
        )
    
    def clean_nombre_billets(self):
        nombre_billets = self.cleaned_data.get('nombre_billets')
        if nombre_billets is None:
            raise ValidationError(_("Veuillez spécifier un nombre de billets."))
        if nombre_billets < 1 or nombre_billets > 10:
            raise ValidationError(_("Le nombre de billets doit être compris entre 1 et 10."))
        return nombre_billets


class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['moyen_paiement']
        
    moyen_paiement = forms.ChoiceField(
        label=_("Moyen de paiement"),
        choices=[
            ('CB', _('Carte bancaire')),
            ('PAYPAL', 'PayPal'),
            ('TICKET', _('Ticket bon d\'achat')),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    code_bon = forms.CharField(
        label=_("Code bon de réduction"),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _("Entrez votre code de réduction")
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['code_bon'].widget.attrs.update({
            'class': 'form-control mt-2',
            'style': 'display: none;',
            'id': 'code-bon-field',
            'disabled': True
        })


class RemboursementForm(forms.ModelForm):
    class Meta:
        model = Remboursement
        fields = ['motif']
        widgets = {
            'motif': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _("Veuillez indiquer la raison de votre demande de remboursement...")
            })
        }


class FiltreHorairesForm(forms.Form):
    depart = forms.ModelChoiceField(
        label=_("Ville de départ"),
        queryset=Ville.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'ville-depart',
            'hx-get': '/reservations/gares-par-ville/',
            'hx-target': '#gare-depart',
            'hx-indicator': '.htmx-indicator',
        })
    )
    
    gare_depart = forms.ModelChoiceField(
        label=_("Gare de départ"),
        queryset=Gare.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'gare-depart',
            'disabled': True
        })
    )
    
    arrivee = forms.ModelChoiceField(
        label=_("Ville d'arrivée"),
        queryset=Ville.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'ville-arrivee',
            'hx-get': '/reservations/gares-par-ville/',
            'hx-target': '#gare-arrivee',
            'hx-indicator': '.htmx-indicator',
        })
    )
    
    gare_arrivee = forms.ModelChoiceField(
        label=_("Gare d'arrivée"),
        queryset=Gare.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'gare-arrivee',
            'disabled': True
        })
    )
    
    date_depart = forms.DateField(
        label=_("Date de départ"),
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': timezone.now().strftime('%Y-%m-%d'),
            'max': (timezone.now() + timezone.timedelta(days=90)).strftime('%Y-%m-%d')
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si une ville de départ est déjà sélectionnée, on charge les gares correspondantes
        if 'depart' in self.data:
            try:
                ville_id = int(self.data.get('depart'))
                self.fields['gare_depart'].queryset = Gare.objects.filter(ville_id=ville_id)
                self.fields['gare_depart'].widget.attrs['disabled'] = False
            except (ValueError, TypeError):
                pass
                
        # Si une ville d'arrivée est déjà sélectionnée, on charge les gares correspondantes
        if 'arrivee' in self.data:
            try:
                ville_id = int(self.data.get('arrivee'))
                self.fields['gare_arrivee'].queryset = Gare.objects.filter(ville_id=ville_id)
                self.fields['gare_arrivee'].widget.attrs['disabled'] = False
            except (ValueError, TypeError):
                pass


class ContactForm(forms.Form):
    sujet = forms.CharField(
        label=_("Sujet"),
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _("Sujet de votre message")
        })
    )
    
    email = forms.EmailField(
        label=_("Votre adresse email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _("votre@email.com")
        })
    )
    
    message = forms.CharField(
        label=_("Votre message"),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': _("Décrivez-nous votre demande...")
        })
    )
    
    copie = forms.BooleanField(
        label=_("Recevoir une copie du message"),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
