# app_gestion_interne/admin.py
from django.contrib import admin
from .models import Etudiant, DossierMemoire,Jury,Soutenance

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

@admin.register(Jury)
class JuryAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste
    list_display = ('nom', 'prenom', 'specialite', 'statut', 'telephone')
    # Filtres sur le côté droit
    list_filter = ('statut', 'specialite')
    # Barre de recherche (Nom, Prénom ou Spécialité)
    search_fields = ('nom', 'prenom', 'specialite')
    # Tri par défaut (Alphabétique sur le nom)
    ordering = ('nom',)


@admin.register(Soutenance)
class SoutenanceAdmin(admin.ModelAdmin):
    list_display = ('get_etudiant', 'status', 'date', 'heure', 'salle')
    list_filter = ('status', 'date')
    search_fields = ('dossier__etudiant__nom', 'dossier__etudiant__prenom', 'salle')
    
    # Organisation des champs pour la vue détaillée
    fieldsets = (
        ('Dossier Concerné', {
            'fields': ('dossier',)
        }),
        ('Membres du Jury', {
            'fields': ('president', 'rapporteur', 'examinateur')
        }),
        ('Décision Direction', {
            'fields': ('status', 'motif_rejet')
        }),
        ('Logistique (Planning)', {
            'fields': ('date', 'heure', 'salle')
        }),
    )

    # Fonction pour afficher le nom de l'étudiant dans la liste
    def get_etudiant(self, obj):
        return f"{obj.dossier.etudiant.nom} {obj.dossier.etudiant.prenom}"
    get_etudiant.short_description = 'Étudiant'