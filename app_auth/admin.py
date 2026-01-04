# app_auth/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # On ajoute nos champs personnalisés (role et departement) à l'interface
    fieldsets = UserAdmin.fieldsets + (
        ('Informations de Poste', {'fields': ('role', 'departement')}),
    )
    list_display = ['username', 'email', 'role', 'departement', 'is_staff']
    list_filter = ['role', 'departement']

admin.site.register(User, CustomUserAdmin)