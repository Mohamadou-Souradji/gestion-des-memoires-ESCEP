# app_gestion_interne/admin.py
from django.contrib import admin
from .models import Etudiant, DossierMemoire

@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'nom', 'prenom', 'classe', 'annee')
    search_fields = ('matricule', 'nom')
    list_filter = ('classe', 'annee')

@admin.register(DossierMemoire)
class DossierMemoireAdmin(admin.ModelAdmin):
    # Regrouper les champs par responsable pour plus de clarté
    fieldsets = (
        ('Info Étudiant', {
            'fields': ('etudiant', 'vague')
        }),
        ('Validation Chef Dept', {
            'fields': ('theme', 'encadreur', 'lieu_stage', 'is_theme_valide', 'is_soutenu')
        }),
        ('Validation Scolarité & Compta', {
            'fields': ('is_semestres_valides', 'is_inscription_validee')
        }),
        ('Dépôts Surveillant', {
            'fields': ('fichier_pre_depot', 'is_pre_depot_fait', 'fichier_post_depot', 'is_post_depot_fait')
        }),
        ('Bibliothèque', {
            'fields': ('is_publie',)
        }),
    )
    list_display = ('etudiant', 'vague', 'is_theme_valide', 'is_pre_depot_fait', 'is_soutenu', 'is_publie')
    list_filter = ('is_theme_valide', 'is_soutenu', 'vague')