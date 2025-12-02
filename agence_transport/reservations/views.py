from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.template import RequestContext
from django.http import HttpResponseForbidden, HttpResponseServerError, HttpResponseNotFound
from .models import *
from .forms import ContactForm, ClientForm, ReservationForm, PaiementForm, RemboursementForm, FiltreHorairesForm

class SearchView(ListView):
    model = Horaire
    template_name = 'reservations/search.html'
    context_object_name = 'horaires'
    paginate_by = 10

    def get_queryset(self):
        queryset = Horaire.objects.filter(
            date_depart__gte=timezone.now(),
            places_disponibles__gt=0
        ).select_related('trajet__depart__ville', 'trajet__arrivee__ville')
        
        # Get search parameters from GET request
        departure_id = self.request.GET.get('departure')
        arrival_id = self.request.GET.get('arrival')
        date = self.request.GET.get('date')
        
        # Apply filters if they exist
        if departure_id:
            queryset = queryset.filter(trajet__depart_id=departure_id)
        if arrival_id:
            queryset = queryset.filter(trajet__arrivee_id=arrival_id)
        if date:
            queryset = queryset.filter(date_depart__date=date)
            
        return queryset.order_by('date_depart')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add all gares to the context for the dropdowns
        context['gares'] = Gare.objects.select_related('ville').all()
        return context

class ContactView(FormView):
    template_name = 'reservations/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('reservations:contact')
    
    def form_valid(self, form):
        # Envoyer l'email
        sujet = f"[Contact] {form.cleaned_data['sujet']}"
        message = f"De: {form.cleaned_data['email']}\n\n{form.cleaned_data['message']}"
        
        send_mail(
            sujet,
            message,
            settings.DEFAULT_FROM_EMAIL,
            ['larissainspirationspirittravel@gmail.com'],
            fail_silently=False,
        )
        
        # Envoyer une copie à l'utilisateur si demandé
        if form.cleaned_data.get('copie'):
            send_mail(
                f"[Copie] {sujet}",
                f"Voici une copie du message que vous nous avez envoyé :\n\n{message}",
                settings.DEFAULT_FROM_EMAIL,
                [form.cleaned_data['email']],
                fail_silently=False,
            )
        
        messages.success(self.request, 'Votre message a bien été envoyé. Nous vous répondrons dans les plus brefs délais.')
        return super().form_valid(form)

# Vues pour les utilisateurs standards
class HomeView(ListView):
    model = Horaire
    template_name = 'reservations/home.html'
    context_object_name = 'horaires'
    paginate_by = 10

    def get_queryset(self):
        queryset = Horaire.objects.filter(
            date_depart__gte=timezone.now(),
            places_disponibles__gt=0
        ).select_related('trajet__depart__ville', 'trajet__arrivee__ville')
        
        # Filtrage par ville de départ et d'arrivée
        depart = self.request.GET.get('depart')
        arrivee = self.request.GET.get('arrivee')
        date = self.request.GET.get('date')
        
        if depart:
            queryset = queryset.filter(trajet__depart__ville__id=depart)
        if arrivee:
            queryset = queryset.filter(trajet__arrivee__ville__id=arrivee)
        if date:
            queryset = queryset.filter(date_depart__date=date)
            
        return queryset.order_by('date_depart')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['villes'] = Ville.objects.all()
        return context

class HoraireDetailView(LoginRequiredMixin, DetailView):
    model = Horaire
    template_name = 'reservations/horaire_detail.html'
    context_object_name = 'horaire'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ReservationForm()
        return context

from django.core.mail import send_mail
from django.conf import settings

class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'reservations/reservation_create.html'
    client_form_class = ClientForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['horaire'] = get_object_or_404(Horaire, pk=self.kwargs['pk'])
        if 'client_form' not in context:
            context['client_form'] = self.client_form_class(user=self.request.user)
        if 'form' not in context:
            context['form'] = self.form_class()
        return context
    
    def get_success_url(self):
        return reverse_lazy('reservations:paiement-create', kwargs={'pk': self.object.pk})
    
    def get(self, request, *args, **kwargs):
        try:
            # Vérifier si l'utilisateur est connecté
            if not request.user.is_authenticated:
                messages.warning(request, 'Veuillez vous connecter pour effectuer une réservation.')
                return redirect('account_login')
            
            # Récupérer l'horaire
            horaire = get_object_or_404(Horaire, pk=kwargs['pk'])
            
            # Vérifier les places disponibles
            if horaire.places_disponibles <= 0:
                messages.error(request, 'Désolé, il n\'y a plus de places disponibles pour ce trajet.')
                return redirect('reservations:home')
            
            # Préparer le contexte avec les formulaires
            form = self.form_class()
            client_form = self.client_form_class(user=request.user)
            
            # Si l'utilisateur est connecté, pré-remplir les champs
            if request.user.is_authenticated:
                client_form.initial = {
                    'prenom': request.user.first_name or '',
                    'nom': request.user.last_name or '',
                    'email': request.user.email or '',
                    'telephone': request.user.client.telephone if hasattr(request.user, 'client') else ''
                }
            
            # Préparer le contexte
            context = {
                'form': form,
                'client_form': client_form,
                'horaire': horaire
            }
            
            return render(request, self.template_name, context)
            
        except Exception as e:
            messages.error(request, f'Une erreur est survenue : {str(e)}')
            return redirect('reservations:home')
    
    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.form_class(request.POST)
        client_form = self.client_form_class(request.POST, user=request.user)
        
        if form.is_valid() and client_form.is_valid():
            return self.form_valid(form, client_form)
        else:
            return self.form_invalid(form, client_form)
    
    def form_valid(self, form, client_form):
        try:
            # Vérifier si l'utilisateur est connecté
            user = self.request.user
            
            # Créer ou mettre à jour l'utilisateur
            if user.is_authenticated:
                # Mettre à jour les informations de l'utilisateur
                user.first_name = client_form.cleaned_data['prenom']
                user.last_name = client_form.cleaned_data['nom']
                user.email = client_form.cleaned_data['email']
                user.save()
            else:
                # Créer un nouvel utilisateur (si l'authentification est requise, cette partie ne sera jamais atteinte)
                user = User.objects.create_user(
                    username=client_form.cleaned_data['email'],
                    email=client_form.cleaned_data['email'],
                    first_name=client_form.cleaned_data['prenom'],
                    last_name=client_form.cleaned_data['nom']
                )
            
            # Créer ou mettre à jour le profil client
            client, created = Client.objects.get_or_create(
                user=user,
                defaults={
                    'telephone': client_form.cleaned_data['telephone']
                }
            )
            
            # Mettre à jour le téléphone si nécessaire
            if not created:
                client.telephone = client_form.cleaned_data['telephone']
                client.save()
            
            # Récupérer l'horaire
            horaire = get_object_or_404(Horaire, pk=self.kwargs['pk'])
            
            # Vérifier les places disponibles
            nombre_billets = form.cleaned_data.get('nombre_billets', 0)
            if horaire.places_disponibles < nombre_billets:
                messages.error(self.request, "Désolé, il n'y a pas assez de places disponibles pour ce trajet.")
                return self.form_invalid(form, client_form)
            
            # Calcul du montant total
            montant_total = float(horaire.prix_base) * nombre_billets
            
            # Création de la réservation
            reservation = Reservation.objects.create(
                client=client,
                horaire=horaire,
                montant_total=montant_total,
                reference=f"RES-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                statut=Reservation.StatutReservation.CONFIRMEE
            )
            
            # Création des billets
            type_billet = form.cleaned_data.get('type_billet', Billet.TypeBillet.STANDARD)
            for i in range(nombre_billets):
                Billet.objects.create(
                    reservation=reservation,
                    type_billet=type_billet,
                    prix=horaire.prix_base,
                    siege=f"{type_billet}-{i+1}"
                )
            
            # Mise à jour des places disponibles
            horaire.places_disponibles -= nombre_billets
            horaire.save()
            
            # Stocker la réservation créée pour l'utiliser dans send_confirmation_email
            self.object = reservation
            
            # Envoyer un email de confirmation
            self.send_confirmation_email()
            
            # Utiliser user.first_name au lieu de client.prenom
            messages.success(
                self.request, 
                f"Réservation effectuée avec succès ! Un email de confirmation a été envoyé à {user.email}"
            )
            return redirect('reservations:paiement-create', pk=reservation.pk)
            
        except Exception as e:
            # En cas d'erreur, afficher un message d'erreur et revenir au formulaire
            messages.error(
                self.request,
                f"Une erreur est survenue lors de la création de la réservation : {str(e)}"
            )
            return self.form_invalid(form, client_form)
    
    def form_invalid(self, form, client_form=None):
        return self.render_to_response(
            self.get_context_data(form=form, client_form=client_form or self.client_form_class())
        )
    
    def send_confirmation_email(self):
        reservation = self.object
        client = reservation.client
        user = client.user
        
        subject = f'Confirmation de votre réservation {reservation.reference}'
        
        # Utilisation d'un template HTML pour un email plus élégant
        message = f"""
        <html>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
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
                        </div>
                        
                        <p>Vous pouvez consulter les détails de votre réservation en vous connectant à votre <a href="{settings.SITE_URL}/compte/reservations/" style="color: #0d6efd; text-decoration: none;">espace client</a>.</p>
                        
                        <p>Pour toute question, n'hésitez pas à répondre à cet email ou à nous contacter au {settings.CONTACT_PHONE}.</p>
                        
                        <p>Merci d'avoir choisi nos services !</p>
                        
                        <p>Cordialement,<br>L'équipe Larissa Inspiration spirit travel</p>
                    </div>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #6c757d;">
                        <p>© {timezone.now().year} Larissa Inspiration spirit travel - Tous droits réservés</p>
                    </div>
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

        reservation.statut = 'CONF'  # Confirmée
        reservation.save()
        
        # Ajout de points de fidélité (1 point par euro dépensé)
        client = self.request.user.client
        client.points_fidelite += int(reservation.montant_total)
        
        # Vérification des points pour un ticket bonus (1000 points = 10€ de réduction)
        if client.points_fidelite >= 1000:
            montant_bonus = (client.points_fidelite // 1000) * 10
            client.points_fidelite = client.points_fidelite % 1000
            
            # Création d'un ticket bonus
            TicketBonus.objects.create(
                client=client,
                montant=montant_bonus,
                date_expiration=timezone.now() + timezone.timedelta(days=365),  # Valable 1 an
                code=f"BONUS-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            )
            
            messages.info(self.request, f"Félicitations ! Vous avez gagné un bon de réduction de {montant_bonus}€ !")
        
        client.save()
        
        messages.success(self.request, "Paiement effectué avec succès ! Votre réservation est confirmée.")
        return redirect('reservation-detail', pk=reservation.pk)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reservation'] = get_object_or_404(Reservation, pk=self.kwargs['pk'], client=self.request.user.client)
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
        return context

class ReservationDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Reservation
    template_name = 'reservations/reservation_detail.html'
    context_object_name = 'reservation'
    
    def test_func(self):
        reservation = self.get_object()
        return self.request.user == reservation.client.user or self.request.user.is_staff

class MesReservationsView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'reservations/mes_reservations.html'
    context_object_name = 'reservations'
    paginate_by = 10
    
    def get_queryset(self):
        # Vérifier si le client existe, sinon le créer
        client, created = Client.objects.get_or_create(user=self.request.user)
        return Reservation.objects.filter(
            client=client
        ).select_related('horaire__trajet__depart__ville', 'horaire__trajet__arrivee__ville').order_by('-date_reservation')

class RemboursementDemandeView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Remboursement
    form_class = RemboursementForm
    template_name = 'reservations/remboursement_demande.html'
    
    def test_func(self):
        # Vérifier que l'utilisateur est propriétaire de la réservation
        reservation = get_object_or_404(Reservation, pk=self.kwargs['pk'])
        return self.request.user == reservation.client.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reservation'] = get_object_or_404(Reservation, pk=self.kwargs['pk'])
        return context
class ReservationAnnulerView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Reservation
    fields = []  # Aucun champ à modifier, juste le statut
    template_name = 'reservations/reservation_annuler.html'
    
    def test_func(self):
        reservation = self.get_object()
        return self.request.user == reservation.client.user
    
    def get_success_url(self):
        return reverse_lazy('reservations:reservation-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        reservation = self.object
        
        # Vérifier que la réservation peut être annulée
        if reservation.statut != 'CONF':  # Confirmée
            messages.error(self.request, "Cette réservation ne peut pas être annulée.")
            return redirect('mes-reservations')
        
        # Mise à jour du statut de la réservation
        reservation.statut = 'ANNU'  # Annulée
        reservation.save()
        
        # Si un paiement a été effectué, créer une demande de remboursement
        if hasattr(reservation, 'paiement') and reservation.paiement.statut == 'PAYE':
            Remboursement.objects.create(
                paiement=reservation.paiement,
                montant=reservation.montant_total * 0.8,  # 80% de remboursement
                motif="Annulation par l'utilisateur"
            )
        
        messages.success(self.request, "La réservation a été annulée avec succès. Un remboursement sera effectué si applicable.")
        return super().form_valid(form)

class ProfilUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'reservations/profil_update.html'
    success_url = reverse_lazy('profil')
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Votre profil a été mis à jour avec succès.')
        return super().form_valid(form)

# Vues pour l'administration (staff)
class GestionReservationsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Reservation
    template_name = 'reservations/admin/gestion_reservations.html'
    context_object_name = 'reservations'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        queryset = Reservation.objects.all().select_related(
            'client__user',
            'horaire__trajet__depart__ville',
            'horaire__trajet__arrivee__ville'
        ).order_by('-date_reservation')
        
        statut = self.request.GET.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
            
        return queryset

class GestionRemboursementsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Remboursement
    template_name = 'reservations/admin/gestion_remboursements.html'
    context_object_name = 'remboursements'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        queryset = Remboursement.objects.all().select_related(
            'paiement__reservation__client__user'
        ).order_by('-date_demande')
        
        traite = self.request.GET.get('traite')
        if traite is not None:
            queryset = queryset.filter(traite=traite.lower() == 'true')
            
        return queryset

class TraiterRemboursementView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Remboursement
    fields = []  # Pas de champs à modifier, juste une action
    template_name = 'reservations/admin/traiter_remboursement.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        remboursement = self.get_object()
        
        # Marquer le remboursement comme traité
        remboursement.traite = True
        remboursement.date_traitement = timezone.now()
        remboursement.save()
        
        # Mettre à jour le statut du paiement
        remboursement.paiement.statut = 'REFU'  # Remboursé
        remboursement.paiement.save()
        
        # Ici, vous pourriez ajouter une logique pour effectuer le remboursement via l'API de paiement
        
        messages.success(self.request, f"Le remboursement de {remboursement.montant}€ a été traité avec succès.")
        return redirect('gestion-remboursements')

# Vues pour l'API (utilisées pour les requêtes AJAX)
@login_required
def get_gares_par_ville(request, ville_id):
    gares = Gare.objects.filter(ville_id=ville_id).values('id', 'nom')
    return JsonResponse(list(gares), safe=False)

@login_required
def get_trajets_par_gares(request):
    depart_id = request.GET.get('depart')
    arrivee_id = request.GET.get('arrivee')
    
    if not depart_id or not arrivee_id:
        return JsonResponse([], safe=False)
    
    trajets = Trajet.objects.filter(
        depart_id=depart_id,
        arrivee_id=arrivee_id,
        actif=True
    ).values('id', 'duree', 'distance')
    
    return JsonResponse(list(trajets), safe=False)

# Vues d'erreur personnalisées
def handler403(request, exception=None, template_name='errors/403.html'):
    return render(request, template_name, status=403)

def handler404(request, exception=None, template_name='errors/404.html'):
    return render(request, template_name, status=404)

def handler500(request, template_name='errors/500.html'):
    return render(request, template_name, status=500)
