from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.forms.widgets import NumberInput, DateInput
from .models import Billet, Client, Paiement, Reservation, Ville, Gare, Trajet, Horaire, Remboursement, TicketBonus
from datetime import datetime, timedelta

class GareForm(forms.ModelForm):
    """
    Formulaire pour l'ajout et la modification d'une gare
    """
    class Meta:
        model = Gare
        fields = ['nom', 'ville', 'adresse']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de la gare',
                'required': True
            }),
            'ville': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
                'hx-get': '/reservations/gares-par-ville/',
                'hx-target': '#id_ville',
                'hx-trigger': 'change'
            }),
            'adresse': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Adresse complète de la gare',
                'required': True
            })
        }
        labels = {
            'nom': 'Nom de la gare',
            'ville': 'Ville',
            'adresse': 'Adresse complète'
        }
        help_texts = {
            'nom': 'Nom officiel de la gare',
            'adresse': 'Adresse complète incluant la rue, le code postal et la ville'
        }

    def clean_nom(self):
        nom = self.cleaned_data.get('nom')
        ville = self.cleaned_data.get('ville')
        
        # Vérifier l'unicité du nom de la gare dans la même ville
        if nom and ville:
            queryset = Gare.objects.filter(nom__iexact=nom, ville=ville)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError('Une gare avec ce nom existe déjà dans cette ville.')
        
        return nom.strip()

class VilleForm(forms.ModelForm):
    """
    Formulaire pour l'ajout et la modification d'une ville
    """
    class Meta:
        model = Ville
        fields = ['nom', 'code']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le nom de la ville',
                'required': True
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le code de la ville',
                'style': 'text-transform: uppercase;',
                'required': True
            })
        }
        labels = {
            'nom': 'Nom de la ville',
            'code': 'Code (3 lettres)'
        }
        help_texts = {
            'code': 'Code de la ville (sera converti en majuscules)'
        }

    def clean_code(self):
        return self.cleaned_data.get('code', '').upper()

class HoraireForm(forms.ModelForm):
    """
    Formulaire pour l'ajout et la modification d'un horaire avec différents types de billets
    """
    class Meta:
        model = Horaire
        fields = [
            'trajet', 'date_depart', 'date_arrivee',
            'prix_standard', 'prix_business', 'prix_premiere',
            'places_standard', 'places_business', 'places_premiere'
        ]
        widgets = {
            'trajet': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'date_depart': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'required': True
            }),
            'date_arrivee': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'required': True
            }),
            # Champs pour les prix
            'prix_standard': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '100',
                'required': True
            }),
            'prix_business': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '100',
                'required': True
            }),
            'prix_premiere': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '100',
                'required': True
            }),
            # Champs pour les places disponibles
            'places_standard': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'required': True
            }),
            'places_business': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'required': True
            }),
            'places_premiere': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'required': True
            })
        }
        labels = {
            'trajet': 'Trajet',
            'date_depart': 'Date et heure de départ',
            'date_arrivee': 'Date et heure d\'arrivée',
            'prix_standard': 'Prix Standard (BIF)',
            'prix_business': 'Prix Business (BIF)',
            'prix_premiere': 'Prix Première Classe (BIF)',
            'places_standard': 'Places Standard',
            'places_business': 'Places Business',
            'places_premiere': 'Places Première Classe'
        }

    def clean(self):
        cleaned_data = super().clean()
        date_depart = cleaned_data.get('date_depart')
        date_arrivee = cleaned_data.get('date_arrivee')
        trajet = cleaned_data.get('trajet')

        # Vérifier que la date d'arrivée est postérieure à la date de départ
        if date_depart and date_arrivee and date_arrivee <= date_depart:
            raise forms.ValidationError({
                'date_arrivee': 'La date d\'arrivée doit être postérieure à la date de départ.'
            })

        # Vérifier que l'horaire ne chevauche pas un autre horaire pour le même trajet
        if date_depart and date_arrivee and trajet:
            # Vérifier les chevauchements avec d'autres horaires du même trajet
            queryset = Horaire.objects.filter(
                trajet=trajet,
                date_depart__lt=date_arrivee,
                date_arrivee__gt=date_depart
            )
            
            # Exclure l'instance actuelle si on est en mode édition
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError(
                    'Un horaire existe déjà pour ce trajet sur cette plage horaire.'
                )

        return cleaned_data

class TrajetForm(forms.ModelForm):
    """
    Formulaire pour l'ajout et la modification d'un trajet
    """
    class Meta:
        model = Trajet
        fields = ['depart', 'arrivee', 'duree', 'distance', 'actif']
        widgets = {
            'depart': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'arrivee': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'duree': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'required': True
            }),
            'distance': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'required': True
            }),
            'actif': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'depart': 'Gare de départ',
            'arrivee': 'Gare d\'arrivée',
            'duree': 'Durée du trajet',
            'distance': 'Distance (km)',
            'actif': 'Trajet actif'
        }

    def clean(self):
        cleaned_data = super().clean()
        depart = cleaned_data.get('depart')
        arrivee = cleaned_data.get('arrivee')

        if depart and arrivee and depart == arrivee:
            raise forms.ValidationError({
                'arrivee': 'La gare d\'arrivée doit être différente de la gare de départ.'
            })

        # Vérification de l'unicité du trajet
        if depart and arrivee:
            queryset = Trajet.objects.filter(depart=depart, arrivee=arrivee)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError(
                    'Un trajet entre ces deux gares existe déjà.'
                )

        return cleaned_data

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


class FiltreRapportForm(forms.Form):
    """Formulaire pour filtrer les rapports de vente par période"""
    date_debut = forms.DateField(
        label='Date de début',
        widget=DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'max': timezone.now().strftime('%Y-%m-%d')
        }),
        required=False
    )
    
    date_fin = forms.DateField(
        label='Date de fin',
        widget=DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'max': timezone.now().strftime('%Y-%m-%d')
        }),
        required=False
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')
        
        # Si une seule des deux dates est renseignée
        if bool(date_debut) ^ bool(date_fin):
            raise forms.ValidationError("Veuillez spécifier à la fois une date de début et une date de fin.")
        
        # Vérifier que la date de début est avant la date de fin
        if date_debut and date_fin and date_debut > date_fin:
            raise forms.ValidationError("La date de début doit être antérieure à la date de fin.")
            
        return cleaned_data
