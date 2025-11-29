from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import *

# Enregistrement des modèles avec des configurations personnalisées

class VilleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code')
    search_fields = ('nom', 'code')
    ordering = ('nom',)

class GareAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ville', 'adresse')
    list_filter = ('ville',)
    search_fields = ('nom', 'ville__nom', 'adresse')
    ordering = ('ville__nom', 'nom')

class TrajetAdmin(admin.ModelAdmin):
    list_display = ('depart', 'arrivee', 'duree', 'distance', 'actif')
    list_filter = ('actif', 'depart__ville', 'arrivee__ville')
    search_fields = ('depart__nom', 'arrivee__nom')
    list_editable = ('actif',)
    ordering = ('depart__ville__nom', 'arrivee__ville__nom')

class HoraireAdmin(admin.ModelAdmin):
    list_display = ('trajet', 'date_depart', 'date_arrivee', 'prix_base', 'places_disponibles')
    list_filter = ('trajet__depart__ville', 'trajet__arrivee__ville', 'date_depart')
    search_fields = ('trajet__depart__nom', 'trajet__arrivee__nom')
    date_hierarchy = 'date_depart'
    ordering = ('-date_depart',)

class ClientInline(admin.StackedInline):
    model = Client
    can_delete = False
    verbose_name_plural = 'Profil Client'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (ClientInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_phone')
    list_select_related = ('client',)

    def get_phone(self, instance):
        return instance.client.telephone if hasattr(instance, 'client') else ''
    get_phone.short_description = 'Téléphone'

class BilletInline(admin.TabularInline):
    model = Billet
    extra = 0
    readonly_fields = ('type_billet', 'prix', 'siege')
    can_delete = False

class PaiementInline(admin.StackedInline):
    model = Paiement
    extra = 0
    can_delete = False
    readonly_fields = ('date_paiement', 'montant', 'statut')

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('reference', 'client', 'horaire', 'date_reservation', 'montant_total', 'statut')
    list_filter = ('statut', 'horaire__trajet__depart__ville', 'horaire__trajet__arrivee__ville')
    search_fields = ('reference', 'client__user__username', 'client__user__first_name', 'client__user__last_name')
    date_hierarchy = 'date_reservation'
    inlines = [BilletInline, PaiementInline]
    readonly_fields = ('date_reservation', 'reference')
    ordering = ('-date_reservation',)

class BilletAdmin(admin.ModelAdmin):
    list_display = ('id', 'reservation', 'type_billet', 'prix', 'siege')
    list_filter = ('type_billet',)
    search_fields = ('reservation__reference', 'siege')
    readonly_fields = ('code_qr',)

class PaiementAdmin(admin.ModelAdmin):
    list_display = ('id', 'reservation', 'montant', 'date_paiement', 'statut')
    list_filter = ('statut', 'date_paiement')
    search_fields = ('reservation__reference', 'stripe_payment_intent_id')
    readonly_fields = ('date_paiement', 'stripe_payment_intent_id')
    date_hierarchy = 'date_paiement'

class RemboursementAdmin(admin.ModelAdmin):
    list_display = ('id', 'paiement', 'montant', 'date_demande', 'traite')
    list_filter = ('traite', 'date_demande')
    search_fields = ('paiement__reservation__reference', 'motif')
    readonly_fields = ('date_demande', 'date_traitement')
    date_hierarchy = 'date_demande'

class TicketBonusAdmin(admin.ModelAdmin):
    list_display = ('code', 'client', 'montant', 'date_creation', 'date_expiration', 'utilise')
    list_filter = ('utilise', 'date_creation', 'date_expiration')
    search_fields = ('client__user__username', 'client__user__first_name', 'client__user__last_name', 'code')
    readonly_fields = ('date_creation',)
    date_hierarchy = 'date_creation'

# Désenregistrer le modèle User par défaut
admin.site.unregister(User)

# Enregistrer nos modèles avec les configurations personnalisées
admin.site.register(User, CustomUserAdmin)
admin.site.register(Ville, VilleAdmin)
admin.site.register(Gare, GareAdmin)
admin.site.register(Trajet, TrajetAdmin)
admin.site.register(Horaire, HoraireAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Billet, BilletAdmin)
admin.site.register(Paiement, PaiementAdmin)
admin.site.register(Remboursement, RemboursementAdmin)
admin.site.register(TicketBonus, TicketBonusAdmin)
