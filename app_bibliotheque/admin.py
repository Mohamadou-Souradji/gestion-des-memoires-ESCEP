from django.contrib import admin
from .models import Livre, JournalOperation, Categorie


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description')
    search_fields = ('nom',)
    # Si tu as ajouté un champ slug, on peut le pré-remplir automatiquement
    # prepopulated_fields = {'slug': ('nom',)}


@admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    # Ajout de 'categorie' dans la liste pour une meilleure visibilité
    list_display = ('titre', 'auteur', 'categorie', 'isbn', 'is_publie', 'date_creation')

    # On permet la recherche aussi par le nom de la catégorie
    search_fields = ('titre', 'auteur', 'isbn', 'categorie__nom')

    # Ajout du filtre par catégorie pour retrouver les livres par rayon
    list_filter = ('categorie', 'is_publie', 'date_creation')

    # Permet de modifier la catégorie et le statut de publication sans ouvrir le livre
    list_editable = ('categorie', 'is_publie')

    # Organisation des champs dans le formulaire d'édition
    fieldsets = (
        ("Informations Générales", {
            'fields': ('titre', 'auteur', 'categorie', 'isbn', 'description')
        }),
        ("Fichiers & Visuels", {
            'fields': ('image_couverture', 'fichier_numerique')
        }),
        ("Statut", {
            'fields': ('is_publie',)
        }),
    )


@admin.register(JournalOperation)
class JournalOperationAdmin(admin.ModelAdmin):
    list_display = ('action', 'date_action', 'effectue_par', 'details_courts')
    list_filter = ('action', 'date_action', 'effectue_par')
    readonly_fields = ('action', 'date_action', 'effectue_par', 'details')

    def details_courts(self, obj):
        return obj.details[:50] + "..." if obj.details else "-"

    details_courts.short_description = "Aperçu des détails"

    # Empêcher la modification manuelle des logs pour l'intégrité
    def has_add_permission(self, request): return False

    def has_change_permission(self, request, obj=None): return False