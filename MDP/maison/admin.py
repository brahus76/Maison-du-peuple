
 
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Client, Acteur, Espace, 
    EvenementCulturel, EvenementPolitique, EvenementEconomique, EvenementSocial,
    TarifEvenement, Ticket, Reservation, Facture
)




from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'espace', 'date_debut', 'statut', 'montant_total')
    list_filter = ('statut', 'espace')

    # Ajout de l'action de confirmation groupée
    actions = ['confirmer_reservations_action']

    @admin.action(description="Confirmer les réservations sélectionnées")
    def confirmer_reservations_action(self, request, queryset):
        nb_maj = queryset.update(statut='confirme')
        self.message_user(request, f"{nb_maj} réservation(s) confirmée(s). Le client peut payer.")
    # Pas de get_urls ici, pas de boutons personnalisés
    def voir_facture(self, obj):
        # L'administrateur peut voir le bouton si le statut est 'paye'
        if obj.statut == 'paye':
            # On utilise le nom de l'URL définie dans votre urls.py principal
            # On passe l'ID de l'objet à la fin de format_html pour respecter Django 6.0
            return format_html(
                '<a class="button" href="/facture/{}/" target="_blank" '
                'style="background-color: #417690; color: white; padding: 3px 10px; border-radius: 4px; text-decoration: none;">'
                '📄 Facture PDF</a>',
                obj.id
            )
        return format_html('<span style="color: #999;">Non payé</span>')

    voir_facture.short_description = "Document"
# 1. INLINES
# Permet de gérer les tarifs directement sur la page de création d'un événement
class TarifEvenementInline(admin.TabularInline):
    model = TarifEvenement
    extra = 1

# 2. CONFIGURATIONS ADMIN

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('email', 'nom', 'prenom', 'phone', 'is_staff', 'is_active')
    search_fields = ('email', 'nom', 'prenom')
    list_filter = ('is_staff', 'is_active')

@admin.register(Espace)
class EspaceAdmin(admin.ModelAdmin):
    list_display = ('nom', 'capacite', 'prix_journalier', 'est_disponible')
    list_editable = ('est_disponible', 'prix_journalier')
    list_filter = ('est_disponible',)






    

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'espace', 'montant_total', 'statut', 'date_emission')
    list_filter = ('statut', 'date_emission')
    list_editable = ('statut',)
    readonly_fields = ('montant_total',)
    actions = ['envoyer_factures_action']

    def envoyer_factures_action(self, request, queryset):
        for facture in queryset:
            facture.envoyer_par_email()
        self.message_user(request, f"Email(s) envoyé(s) avec succès à {queryset.count()} client(s).")
    envoyer_factures_action.short_description = "Envoyer les factures sélectionnées par Email"

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'choix_tarif', 'numero_place', 'date_achat', 'get_prix')
    search_fields = ('client__nom', 'code_barre_qr')
    
    def get_prix(self, obj):
        return f"{obj.montant} FCFA"
    get_prix.short_description = "Prix payé"

@admin.register(EvenementCulturel, EvenementPolitique, EvenementEconomique, EvenementSocial)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ('titre_stockage', 'type_evenement', 'date_debut', 'display_espaces', 'nombre_de_places','description')
    list_filter = ('date_debut', 'espace')
    search_fields = ('titre_stockage', 'intervenant__nom')
    readonly_fields = ('type_evenement',)
    inlines = [TarifEvenementInline] # Ajoute la gestion des prix (VIP, STD...) ici

    def display_espaces(self, obj):
        return ", ".join([e.nom for e in obj.espace.all()])
    display_espaces.short_description = 'Espaces réservés'

@admin.register(Acteur)
class ActeurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'telephone')
    search_fields = ('nom',)

# TarifEvenement est déjà géré via l'inline dans EvenementAdmin, 
# mais on peut l'enregistrer seul si besoin de modifications directes.
admin.site.register(TarifEvenement)