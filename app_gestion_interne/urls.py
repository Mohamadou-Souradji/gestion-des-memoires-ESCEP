from django.urls import path
from . import views

app_name = 'gestion_interne'

urlpatterns = [
    path('dashboard/', views.dashboard_surveillant, name='surveillant_dashboard'),

    # On enlève <int:vague_id>/ ici car le surveillant voit tout le monde
    path('pre-depot/', views.surveillant_pre_depot_liste, name='surveillant_pre_depot'),

    path('save-pdf/<int:dossier_id>/', views.action_save_pdf, name='action_save_pdf'),

    # On enlève <int:vague_id>/ ici aussi
    path('post-depot/liste/', views.surveillant_post_depot_liste, name='post_depot_liste'),

    path('post-depot/save/<int:dossier_id>/', views.action_save_post_pdf, name='action_save_post_pdf'),

# Tableau de bord et Validation
    path('scolarite/dashboard/', views.scolarite_dashboard, name='scolarite_dashboard'),
    path('scolarite/etudiants/', views.liste_etudiants_scolarite, name='scolarite_etudiants'),
    path('scolarite/valider/<str:matricule>/', views.toggle_semestres, name='toggle_semestres'),


    path('scolarite/attestations/', views.scolarite_detail_attestations,  name='scolarite_detail_attestations'),
path('comptabilite/liste/', views.liste_etudiants_comptabilite, name='liste_etudiants_comptabilite'),
path('comptabilite/toggle/<str:matricule>/', views.toggle_inscription, name='toggle_inscription'),
]
