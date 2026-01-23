# core/urls.py
from django.contrib import admin
from django.urls import path, include
from app_auth.views import connexion_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls), # Ajoute le 's' ici
    path('', connexion_view, name='login'),
    path('auth/', include('app_auth.urls')),
    path('administration/', include('app_administration.urls')),
path('gestion/', include('app_gestion_interne.urls', namespace='app_gestion_interne')),
    path('biblio/', include('app_bibliotheque.urls')),
]

# AJOUTEZ CECI POUR LE DÉVELOPPEMENT
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)