# app_bibliotheque/admin.py
from django.contrib import admin
from .models import Livre

@admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'isbn', 'est_disponible')
    search_fields = ('titre', 'isbn')
    list_editable = ('est_disponible',)