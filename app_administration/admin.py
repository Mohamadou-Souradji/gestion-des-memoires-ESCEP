# app_administration/admin.py
from django.contrib import admin
from .models import Departement, Filiere, Classe, AnneeScolaire, Vague

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
    list_display = ('libelle', 'annee', 'date_ouverture', 'date_fermeture')
    list_filter = ('annee',)