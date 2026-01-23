# app_administration/admin.py
from django.contrib import admin
from .models import Departement, Filiere, Classe, AnneeScolaire, Vague,ClotureVagueDepartement

@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)

@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'departement')
    list_filter = ('departement',)
    search_fields = ('code', 'nom')

@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'filiere')
    list_filter = ('filiere',)
    search_fields = ('code', 'nom')

@admin.register(AnneeScolaire)
class AnneeScolaireAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'est_active')
    list_editable = ('est_active',)

@admin.register(Vague)
class VagueAdmin(admin.ModelAdmin):
    # On remplace 'annee' par la fonction 'afficher_annees'
    list_display = ('libelle', 'afficher_annees', 'date_ouverture', 'date_fermeture', 'est_cloturee')
    
    # On utilise filter_horizontal pour une sélection plus jolie des années
    filter_horizontal = ('annees_concernees',)
    
    list_filter = ('est_cloturee', 'annees_concernees')
    search_fields = ('libelle',)

    # Fonction pour afficher les années dans la liste
    def afficher_annees(self, obj):
        return ", ".join([a.libelle for a in obj.annees_concernees.all()])
    
    afficher_annees.short_description = 'Années Concernées'

@admin.register(ClotureVagueDepartement)
class ClotureVagueDepartementAdmin(admin.ModelAdmin):
    list_display = ('vague', 'departement', 'is_cloturee')
    list_filter = ('vague', 'departement', 'is_cloturee')