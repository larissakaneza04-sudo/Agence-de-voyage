from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string, get_template
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import models
from django.db.models import Q, F, Sum
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.template import RequestContext, Template, Context
from django.http import HttpResponseForbidden, HttpResponseServerError, HttpResponseNotFound, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Horaire, Gare, Trajet, Reservation, Client, Billet, Remboursement, User, Ville, TicketBonus
from .forms import VilleForm, TrajetForm, HoraireForm, GareForm
from .forms import ContactForm, ClientForm, ReservationForm, PaiementForm, RemboursementForm, FiltreHorairesForm

class SearchView(ListView):
    model = Horaire
    template_name = 'reservations/search.html'
    context_object_name = 'horaires'
    paginate_by = 10

    def get_queryset(self):
        # Filtrer uniquement les horaires futurs avec des places disponibles
        now = timezone.now()
        queryset = Horaire.objects.filter(
            date_depart__gt=now,  # Utilisation de __gt pour exclure les départs en cours
            places_standard__gt=0  # On filtre sur les places standard par défaut
        ).select_related(
            'trajet__depart__ville',
            'trajet__arrivee__ville'
        )
        
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
            # S'assurer que la date est valide avant de filtrer
            try:
                date_obj = timezone.datetime.strptime(date, '%Y-%m-%d').date()
                queryset = queryset.filter(
                    date_depart__date=date_obj,
                    date_depart__gt=now  # S'assurer que c'est dans le futur
                )
            except (ValueError, TypeError):
                # En cas d'erreur de format de date, on ignore le filtre
                pass
            
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
        # Filtrer uniquement les horaires futurs avec des places disponibles
        now = timezone.now()
        queryset = Horaire.objects.filter(
            date_depart__gt=now  # Utilisation de __gt pour exclure les départs en cours
        ).annotate(
            total_places=models.F('places_standard') + models.F('places_business') + models.F('places_premiere')
        ).filter(
            total_places__gt=0  # Ne montrer que les horaires avec au moins une place disponible
        ).select_related(
            'trajet__depart__ville', 
            'trajet__arrivee__ville'
        ).order_by('date_depart')
        
        # Filtrage par ville de départ et d'arrivée
        depart = self.request.GET.get('depart')
        arrivee = self.request.GET.get('arrivee')
        date = self.request.GET.get('date')
        
        if depart:
            queryset = queryset.filter(trajet__depart__ville__id=depart)
        if arrivee:
            queryset = queryset.filter(trajet__arrivee__ville__id=arrivee)
        if date:
            # S'assurer que la date est valide avant de filtrer
            try:
                date_obj = timezone.datetime.strptime(date, '%Y-%m-%d').date()
                next_day = date_obj + timezone.timedelta(days=1)
                queryset = queryset.filter(
                    date_depart__date__gte=date_obj,
                    date_depart__date__lt=next_day,
                    date_depart__gt=now  # S'assurer que c'est dans le futur
                )
            except (ValueError, TypeError):
                # En cas d'erreur de format de date, on ignore le filtre
                pass
            
        return queryset
    
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
from .emails import envoyer_email_confirmation_reservation

class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'reservations/reservation_create.html'
    client_form_class = ClientForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        horaire = get_object_or_404(Horaire, pk=self.kwargs['pk'])
        context['horaire'] = horaire
        
        # Vérifier les tickets bonus disponibles
        tickets_bonus = []
        if self.request.user.is_authenticated and hasattr(self.request.user, 'client'):
            tickets_bonus = TicketBonus.objects.filter(
                client=self.request.user.client,
                utilise=False,
                date_expiration__gt=timezone.now()
            )
        
        context.update({
            'tickets_bonus': tickets_bonus,
            'afficher_rappel_bonus': tickets_bonus.exists()
        })
        
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
            
            # Vérifier les places disponibles pour les billets standard
            if horaire.get_places_disponibles('STD') <= 0:
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
            
            # Récupérer le type de billet et le nombre de billets
            type_billet = form.cleaned_data.get('type_billet', Billet.TypeBillet.STANDARD)
            nombre_billets = form.cleaned_data.get('nombre_billets', 0)
            
            # Vérifier les places disponibles selon le type de billet
            places_disponibles = 0
            message_erreur = ""
            
            if type_billet == Billet.TypeBillet.STANDARD:
                places_disponibles = horaire.places_standard
                message_erreur = "Désolé, il n'y a pas assez de places disponibles en classe Standard pour ce trajet."
            elif type_billet == Billet.TypeBillet.BUSINESS:
                places_disponibles = horaire.places_business
                message_erreur = "Désolé, il n'y a pas assez de places disponibles en classe Business pour ce trajet."
            elif type_billet == Billet.TypeBillet.PREMIERE:
                places_disponibles = horaire.places_premiere
                message_erreur = "Désolé, il n'y a pas assez de places disponibles en Première Classe pour ce trajet."
            
            if places_disponibles < nombre_billets:
                messages.error(self.request, message_erreur)
                return self.form_invalid(form, client_form)
            
            # Déterminer le prix en fonction du type de billet
            if type_billet == Billet.TypeBillet.STANDARD:
                prix_unitaire = horaire.prix_standard
            elif type_billet == Billet.TypeBillet.BUSINESS:
                prix_unitaire = horaire.prix_business
            elif type_billet == Billet.TypeBillet.PREMIERE:
                prix_unitaire = horaire.prix_premiere
            
            # Vérifier si l'utilisateur a un ticket bonus valide à utiliser
            ticket_bonus = None
            if hasattr(self.request.user, 'client'):
                ticket_bonus = TicketBonus.objects.filter(
                    client=self.request.user.client,
                    utilise=False,
                    date_expiration__gt=timezone.now()
                ).first()
                
                if ticket_bonus and nombre_billets <= ticket_bonus.nombre_places:
                    # Utiliser le ticket bonus
                    prix_unitaire = 0
                    ticket_bonus.utiliser()
                    messages.success(
                        self.request, 
                        f"Votre ticket bonus {ticket_bonus.code} a été utilisé pour cette réservation !"
                    )
            
            # Calculer le prix total
            prix_total = prix_unitaire * nombre_billets
            
            # Création de la réservation
            reservation = Reservation.objects.create(
                client=client,
                horaire=horaire,
                montant_total=prix_total,  # Utilisation de la variable prix_total définie plus haut
                reference=f"RES-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                statut=Reservation.StatutReservation.CONFIRMEE
            )
            
            # Création des billets
            for i in range(nombre_billets):
                Billet.objects.create(
                    reservation=reservation,
                    type_billet=type_billet,
                    prix=prix_unitaire,
                    siege=f"{type_billet}-{i+1}"
                )
            
            # Mise à jour des places disponibles selon le type de billet
            if type_billet == Billet.TypeBillet.STANDARD:
                horaire.places_standard -= nombre_billets
            elif type_billet == Billet.TypeBillet.BUSINESS:
                horaire.places_business -= nombre_billets
            elif type_billet == Billet.TypeBillet.PREMIERE:
                horaire.places_premiere -= nombre_billets
            
            # Mettre à jour le compteur de places réservées pour le client
            # et vérifier si un ticket bonus est gagné
            tickets_gagnes = client.ajouter_reservation(nombre_billets)
            
            # Si des tickets bonus ont été gagnés, les créer
            for _ in range(tickets_gagnes):
                ticket = TicketBonus.creer_ticket_bonus(
                    client=client,
                    montant=0,  # Ou le montant de réduction si vous le souhaitez
                    nombre_places=1
                )
                # Envoyer une notification au client
                messages.success(
                    self.request,
                    f"Félicitations ! Vous avez gagné un ticket bonus pour votre prochain voyage ! "
                    f"Code: {ticket.code} (Valable jusqu'au {ticket.date_expiration.strftime('%d/%m/%Y')})"
                )
            
            try:
                horaire.save()
                
                # Envoyer l'email de confirmation de réservation
                from .emails import envoyer_email_confirmation_reservation
                envoyer_email_confirmation_reservation(reservation)
                
                messages.success(
                    self.request,
                    f"Réservation effectuée avec succès ! Un email de confirmation a été envoyé à {user.email}."
                )
                
            except Exception as e:
                # En cas d'erreur lors de la sauvegarde
                messages.error(self.request, f"Erreur lors de la mise à jour des places disponibles : {str(e)}")
                return self.form_invalid(form, client_form)
            
            return redirect('reservations:paiement-create', pk=reservation.pk)
            
        except Exception as e:
            # En cas d'erreur, afficher un message d'erreur et revenir au formulaire
            messages.error(
                self.request,
                f"Une erreur est survenue lors de la création de la réservation : {str(e)}"
            )
            return self.form_invalid(form, client_form)
    
    def form_invalid(self, form, client_form=None):
        # Get the error messages
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f"{form.fields[field].label}: {error}")
        
        # If we have error messages, store them in the session
        if error_messages:
            messages.error(self.request, ". ".join(error_messages))
        
        # Get the horaire ID from the URL
        horaire_id = self.kwargs.get('pk')
        
        # Redirect back to the reservation form with the error message
        return redirect('reservations:reservation-create', pk=horaire_id)
    
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
        return redirect('reservations:reservation-detail', pk=reservation.pk)
    
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
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Vérifier si l'utilisateur a un client associé
        print(f"[DEBUG] Utilisateur: {self.request.user}")
        print(f"[DEBUG] Client associé: {hasattr(self.request.user, 'client')}")
        
        if hasattr(self.request.user, 'client'):
            # Vérifier le nombre de places réservées
            print(f"[DEBUG] Nombre de places réservées: {self.request.user.client.places_reservees}")
            
            # Vérifier les tickets bonus existants
            tickets_bonus = TicketBonus.objects.filter(
                client=self.request.user.client,
                utilise=False,
                date_expiration__gt=timezone.now()
            ).order_by('date_expiration')
            
            print(f"[DEBUG] Tickets bonus trouvés: {tickets_bonus.count()}")
            
            context['tickets_bonus'] = tickets_bonus
            context['afficher_notification_bonus'] = tickets_bonus.exists()
            
            # Vérifier si on doit créer un nouveau ticket bonus
            if self.request.user.client.places_reservees >= 5:
                print("[DEBUG] Nombre de places suffisant pour un ticket bonus")
                # Créer un ticket bonus
                nouveau_ticket = TicketBonus.creer_ticket_bonus(
                    client=self.request.user.client,
                    montant=0,  # ou le montant de réduction souhaité
                    nombre_places=1
                )
                print(f"[DEBUG] Nouveau ticket bonus créé: {nouveau_ticket}")
                
                # Mettre à jour le contexte avec le nouveau ticket
                tickets_bonus = TicketBonus.objects.filter(
                    client=self.request.user.client,
                    utilise=False,
                    date_expiration__gt=timezone.now()
                ).order_by('date_expiration')
                context['tickets_bonus'] = tickets_bonus
                context['afficher_notification_bonus'] = True
        else:
            print("[DEBUG] Aucun client associé à cet utilisateur")
            
        return context


class MesTicketsBonusView(LoginRequiredMixin, ListView):
    model = TicketBonus
    template_name = 'reservations/mes_tickets_bonus.html'
    context_object_name = 'tickets'
    paginate_by = 10
    
    def get_queryset(self):
        # Get or create client for the user
        client, created = Client.objects.get_or_create(user=self.request.user)
        
        # Return valid tickets (not used and not expired) for the client
        return TicketBonus.objects.filter(
            client=client,
            utilise=False,
            date_expiration__gt=timezone.now()
        ).order_by('date_expiration')

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
        return reverse_lazy('reservations:mes-reservations')
    
    def form_valid(self, form):
        reservation = self.object
        
        # Vérifier que la réservation peut être annulée
        if reservation.statut != 'CONF':  # Confirmée
            messages.error(self.request, "Cette réservation ne peut pas être annulée.")
            return redirect('reservations:mes-reservations')
        
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
        
        # Décrémenter le compteur de places réservées
        reservation.client.places_reservees = max(0, reservation.client.places_reservees - reservation.billets.count())
        reservation.client.save()
        
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

# Vues pour la gestion des gares
class GareListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Gare
    template_name = 'reservations/gares/gare_list.html'
    context_object_name = 'gares'
    paginate_by = 15
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        queryset = Gare.objects.select_related('ville').order_by('ville__nom', 'nom')
        
        # Filtrage par ville
        ville_id = self.request.GET.get('ville')
        if ville_id:
            queryset = queryset.filter(ville_id=ville_id)
            
        # Filtrage par recherche
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(nom__icontains=search) |
                Q(adresse__icontains=search) |
                Q(ville__nom__icontains=search)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['villes'] = Ville.objects.all().order_by('nom')
        context['filter_ville'] = self.request.GET.get('ville', '')
        context['search'] = self.request.GET.get('q', '')
        return context

@login_required
def ajouter_gare(request):
    """
    Vue pour l'ajout d'une nouvelle gare
    """
    if not request.user.is_staff:
        return redirect('account_login')
        
    if request.method == 'POST':
        form = GareForm(request.POST)
        if form.is_valid():
            try:
                gare = form.save()
                messages.success(request, f'La gare {gare.nom} a été ajoutée avec succès.')
                return redirect('reservations:gare-list')
            except Exception as e:
                messages.error(request, f'Une erreur est survenue : {str(e)}')
    else:
        form = GareForm()
    
    return render(request, 'reservations/gares/gare_form.html', {
        'form': form,
        'title': 'Ajouter une gare',
        'btn_text': 'Ajouter',
        'villes': Ville.objects.all().order_by('nom')
    })

class GareUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Gare
    form_class = GareForm
    template_name = 'reservations/gares/gare_form.html'
    context_object_name = 'gare'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_success_url(self):
        messages.success(self.request, 'La gare a été mise à jour avec succès.')
        return reverse_lazy('reservations:gare-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier la gare'
        context['btn_text'] = 'Mettre à jour'
        context['villes'] = Ville.objects.all().order_by('nom')
        return context

class GareDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Gare
    template_name = 'reservations/gares/gare_confirm_delete.html'
    success_url = reverse_lazy('reservations:gare-list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        gare = self.get_object()
        
        # Vérifier s'il y a des trajets associés à cette gare
        if gare.departs.exists() or gare.arrivees.exists():
            messages.error(
                request,
                "Impossible de supprimer cette gare car elle est utilisée dans des trajets."
            )
            return redirect('reservations:gare-list')
        
        messages.success(request, f'La gare {gare.nom} a été supprimée avec succès.')
        return super().delete(request, *args, **kwargs)

# Vues pour la gestion des horaires
class HoraireListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Horaire
    template_name = 'reservations/horaires/horaire_list.html'
    context_object_name = 'horaires'
    paginate_by = 15
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        queryset = Horaire.objects.select_related(
            'trajet__depart__ville', 
            'trajet__arrivee__ville'
        ).order_by('-date_depart')
        
        # Filtrage par trajet
        trajet_id = self.request.GET.get('trajet')
        if trajet_id:
            queryset = queryset.filter(trajet_id=trajet_id)
            
        # Filtrage par date de départ
        date_depart = self.request.GET.get('date_depart')
        if date_depart:
            try:
                date_obj = datetime.strptime(date_depart, '%Y-%m-%d').date()
                next_day = date_obj + timedelta(days=1)
                queryset = queryset.filter(
                    date_depart__date__gte=date_obj,
                    date_depart__date__lt=next_day
                )
            except ValueError:
                pass
                
        # Filtrage par statut (passé/à venir)
        statut = self.request.GET.get('statut')
        now = timezone.now()
        if statut == 'passe':
            queryset = queryset.filter(date_depart__lt=now)
        elif statut == 'a_venir':
            queryset = queryset.filter(date_depart__gte=now)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trajets'] = Trajet.objects.select_related('depart__ville', 'arrivee__ville').all()
        context['filter_trajet'] = self.request.GET.get('trajet', '')
        context['filter_date'] = self.request.GET.get('date_depart', '')
        context['filter_statut'] = self.request.GET.get('statut', '')
        return context

@login_required
def ajouter_horaire(request):
    """
    Vue pour l'ajout d'un nouvel horaire
    """
    if not request.user.is_staff:
        return redirect('account_login')
        
    if request.method == 'POST':
        form = HoraireForm(request.POST)
        if form.is_valid():
            try:
                horaire = form.save()
                messages.success(request, f"L'horaire a été ajouté avec succès.")
                return redirect('reservations:horaire-list')
            except Exception as e:
                messages.error(request, f'Une erreur est survenue : {str(e)}')
    else:
        form = HoraireForm()
    
    return render(request, 'reservations/horaires/horaire_form.html', {
        'form': form,
        'title': 'Ajouter un horaire',
        'btn_text': 'Ajouter'
    })

class HoraireUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Horaire
    form_class = HoraireForm
    template_name = 'reservations/horaires/horaire_form.html'
    context_object_name = 'horaire'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_success_url(self):
        messages.success(self.request, "L'horaire a été mis à jour avec succès.")
        return reverse_lazy('reservations:horaire-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier l\'horaire'
        context['btn_text'] = 'Mettre à jour'
        return context

class HoraireDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Horaire
    template_name = 'reservations/horaires/horaire_confirm_delete.html'
    success_url = reverse_lazy('reservations:horaire-list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        horaire = self.get_object()
        
        # Vérifier s'il y a des réservations pour cet horaire
        if horaire.reservations.exists():
            messages.error(
                request,
                "Impossible de supprimer cet horaire car il a des réservations associées."
            )
            return redirect('reservations:horaire-list')
        
        messages.success(request, "L'horaire a été supprimé avec succès.")
        return super().delete(request, *args, **kwargs)

# Vues pour la gestion des trajets
class TrajetListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Trajet
    template_name = 'reservations/trajets/trajet_list.html'
    context_object_name = 'trajets'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        queryset = Trajet.objects.select_related('depart__ville', 'arrivee__ville')
        
        # Filtrage par gare de départ
        depart = self.request.GET.get('depart')
        if depart:
            queryset = queryset.filter(depart_id=depart)
            
        # Filtrage par gare d'arrivée
        arrivee = self.request.GET.get('arrivee')
        if arrivee:
            queryset = queryset.filter(arrivee_id=arrivee)
            
        # Filtrage par statut actif/inactif
        actif = self.request.GET.get('actif')
        if actif == '1':
            queryset = queryset.filter(actif=True)
        elif actif == '0':
            queryset = queryset.filter(actif=False)
            
        return queryset.order_by('depart__ville__nom', 'arrivee__ville__nom')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gares'] = Gare.objects.select_related('ville').order_by('ville__nom', 'nom')
        context['filter_depart'] = self.request.GET.get('depart', '')
        context['filter_arrivee'] = self.request.GET.get('arrivee', '')
        context['filter_actif'] = self.request.GET.get('actif', '')
        return context

@login_required
def ajouter_trajet(request):
    """
    Vue pour l'ajout d'un nouveau trajet
    """
    if not request.user.is_staff:
        return redirect('account_login')
        
    if request.method == 'POST':
        form = TrajetForm(request.POST)
        if form.is_valid():
            try:
                trajet = form.save()
                messages.success(request, f'Le trajet {trajet} a été ajouté avec succès.')
                return redirect('reservations:trajet-list')
            except Exception as e:
                messages.error(request, f'Une erreur est survenue : {str(e)}')
    else:
        form = TrajetForm()
    
    return render(request, 'reservations/trajets/trajet_form.html', {
        'form': form,
        'title': 'Ajouter un trajet',
        'btn_text': 'Ajouter'
    })

class TrajetUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Trajet
    form_class = TrajetForm
    template_name = 'reservations/trajets/trajet_form.html'
    context_object_name = 'trajet'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_success_url(self):
        messages.success(self.request, 'Le trajet a été mis à jour avec succès.')
        return reverse_lazy('reservations:trajet-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier le trajet'
        context['btn_text'] = 'Mettre à jour'
        return context

class TrajetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Trajet
    template_name = 'reservations/trajets/trajet_confirm_delete.html'
    success_url = reverse_lazy('reservations:trajet-list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trajet = self.get_object()
        
        # Récupérer les réservations associées
        reservations = []
        horaires_count = 0
        
        for horaire in trajet.horaires.all():
            horaires_count += 1
            for reservation in horaire.reservations.all():
                reservations.append(reservation)
        
        context['reservations'] = reservations
        context['has_reservations'] = len(reservations) > 0
        context['horaires_count'] = horaires_count
        return context
    
    def post(self, request, *args, **kwargs):
        trajet = self.get_object()
        
        # Vérifier si l'utilisateur a confirmé la suppression des réservations
        confirm_delete = request.POST.get('confirm_delete', 'no') == 'yes'
        
        # Vérifier s'il y a des réservations associées
        has_reservations = False
        reservations_to_delete = []
        
        for horaire in trajet.horaires.all():
            for reservation in horaire.reservations.all():
                has_reservations = True
                reservations_to_delete.append(reservation)
        
        if has_reservations and not confirm_delete:
            # Afficher la page de confirmation pour la suppression des réservations
            return self.render_to_response(self.get_context_data(show_confirmation=True))
        
        try:
            # Supprimer d'abord les réservations associées (si confirmé)
            if confirm_delete and reservations_to_delete:
                for reservation in reservations_to_delete:
                    reservation.delete()
            
            # Supprimer les horaires associés
            horaires_count = trajet.horaires.count()
            trajet.horaires.all().delete()
            
            # Enfin, supprimer le trajet
            trajet.delete()
            
            messages.success(
                request,
                f'Le trajet {trajet} et ses {horaires_count} horaires associés ont été supprimés avec succès.'
            )
            return redirect(self.get_success_url())
            
        except Exception as e:
            messages.error(
                request,
                f'Une erreur est survenue lors de la suppression : {str(e)}'
            )
            return redirect('reservations:trajet-list')

def ajouter_ville(request):
    """
    Vue pour l'ajout d'une nouvelle ville
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('account_login')
        
    if request.method == 'POST':
        form = VilleForm(request.POST)
        if form.is_valid():
            try:
                ville = form.save()
                messages.success(request, f'La ville {ville.nom} a été ajoutée avec succès.')
                return redirect('reservations:ville-list')
            except Exception as e:
                messages.error(request, f'Une erreur est survenue : {str(e)}')
    else:
        form = VilleForm()
    
    return render(request, 'reservations/villes/ajouter_ville.html', {
        'form': form,
        'title': 'Ajouter une ville'
    })

# Vues pour la gestion des villes
class VilleListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Ville
    template_name = 'reservations/villes/ville_list.html'
    context_object_name = 'villes'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.is_staff

class VilleCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Ville
    fields = ['nom', 'code']
    template_name = 'reservations/villes/ville_form.html'
    success_url = reverse_lazy('reservations:ville-list')
    success_message = 'La ville a été ajoutée avec succès.'
    
    def test_func(self):
        return self.request.user.is_staff
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter une ville'
        context['btn_text'] = 'Ajouter'
        return context

class VilleUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Ville
    fields = ['nom', 'code']
    template_name = 'reservations/villes/ville_form.html'
    success_url = reverse_lazy('reservations:ville-list')
    success_message = 'La ville a été mise à jour avec succès.'
    
    def test_func(self):
        return self.request.user.is_staff
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier la ville'
        context['btn_text'] = 'Mettre à jour'
        return context

class VilleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Ville
    template_name = 'reservations/villes/ville_confirm_delete.html'
    success_url = reverse_lazy('reservations:ville-list')
    success_message = 'La ville a été supprimée avec succès.'
    
    def test_func(self):
        return self.request.user.is_staff
        
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
