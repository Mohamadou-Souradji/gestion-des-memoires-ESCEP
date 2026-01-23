from django.urls import path
from . import views

app_name = 'gestion_interne'

urlpatterns = [
    path('dashboard/', views.dashboard_surveillant, name='surveillant_dashboard'),
    path('vagues/', views.surveillant_vagues, name='surveillant_vagues'),
    path('pre-depot/<int:vague_id>/', views.surveillant_pre_depot_liste, name='surveillant_pre_depot'),
  #  path('upload-pdf/<int:dossier_id>/', views.action_upload_pre_depot, name='action_upload_pre_depot'),
    path('save-pdf/<int:dossier_id>/', views.action_save_pdf, name='action_save_pdf'),
   # 1. Liste des vagues pour le post-dépôt
    path('post-depot/vagues/', views.surveillant_vagues_post, name='surveillant_vagues_post'),
    
    # 2. Liste des étudiants éligibles (Soutenus) pour le dépôt final
    path('post-depot/liste/<int:vague_id>/', views.surveillant_post_depot_liste, name='post_depot_liste'),
    
    # 3. Action Upload/Delete du PDF final
    path('post-depot/save/<int:dossier_id>/', views.action_save_post_pdf, name='action_save_post_pdf'),
# Tableau de bord et Validation
    path('scolarite/dashboard/', views.scolarite_dashboard, name='scolarite_dashboard'),
    path('scolarite/etudiants/', views.liste_etudiants_scolarite, name='scolarite_etudiants'),
    path('scolarite/valider/<str:matricule>/', views.toggle_semestres, name='toggle_semestres'),


    path('scolarite/attestations/', views.scolarite_vagues_attestations, name='scolarite_vagues_attestations'),  # Nom pour la liste

    path('scolarite/attestations/<int:vague_id>/', views.scolarite_detail_attestations,  name='scolarite_detail_attestations'),
path('comptabilite/liste/', views.liste_etudiants_comptabilite, name='liste_etudiants_comptabilite'),
path('comptabilite/toggle/<str:matricule>/', views.toggle_inscription, name='toggle_inscription'),
]