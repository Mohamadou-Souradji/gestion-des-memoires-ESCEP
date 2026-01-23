from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    # =========================================================
    # PARTIE DIRECTEUR DES ÉTUDES (DE)
    # =========================================================
    path('de/dashboard/', views.dashboard_directeur, name='dashboard_de'),
    
    # Gestion des structures
    path('de/annees/', views.liste_annees, name='liste_annees'),
    path('de/annees/activer/<int:pk>/', views.activer_annee, name='activer_annee'),
    path('de/annees/supprimer/<int:pk>/', views.supprimer_annee, name='supprimer_annee'),
    
    path('de/departements/', views.liste_departements, name='liste_departements'),
    path('de/departements/modifier/<int:pk>/', views.modifier_departement, name='modifier_departement'),
    path('de/departements/supprimer/<int:pk>/', views.supprimer_departement, name='supprimer_departement'),
    
    path('de/filieres/', views.liste_filieres, name='liste_filieres'),
    path('de/filieres/modifier/<int:pk>/', views.modifier_filiere, name='modifier_filiere'),
    path('de/filieres/supprimer/<int:pk>/', views.supprimer_filiere, name='supprimer_filiere'),
    
    path('de/classes/', views.liste_classes, name='liste_classes'),
    path('de/classes/modifier/<int:pk>/', views.modifier_classe, name='modifier_classe'),
    
    # Vagues (Vue Globale DE)
    path('de/vagues/', views.liste_vagues, name='liste_vagues'),
    path('de/vagues/modifier/<int:pk>/', views.modifier_vague, name='modifier_vague'),
    path('vagues/cloturer/<int:pk>/', views.cloturer_vague, name='cloturer_vague'),
    
    # Utilisateurs (Chefs)
    path('de/chefs/', views.liste_chefs, name='liste_chefs'),
    path('de/chefs/supprimer/<int:pk>/', views.supprimer_chef, name='supprimer_chef'),

 

    # =========================================================
    # PARTIE CHEF DE DÉPARTEMENT
    # =========================================================
    path('chef/accueil/', views.accueil_chef, name='accueil_chef'),

    # Gestion des Vagues (Isolation par département)
    path('chef/vagues/', views.chef_liste_vagues, name='chef_liste_vagues'),
    path('chef/vagues/<int:pk>/', views.chef_detail_vague, name='chef_detail_vague'),
    
    # Action Clôturer/Réouvrir (Utilise ClotureVagueDepartement)
    path('chef/vagues/<int:pk>/toggle-cloture/', views.chef_toggle_cloture, name='chef_toggle_cloture'),
    
    # Inscriptions et Annulations
    path('chef/vagues/inscrire/<int:pk_dossier>/<int:pk_vague>/', 
         views.chef_inscrire_vague, name='chef_inscrire_vague'),
    path('chef/vagues/annuler/<int:pk_dossier>/<int:pk_vague>/', 
         views.chef_annuler_inscription, name='chef_annuler_inscription'),

    # Thèmes et Stages
    path('chef/themes/', views.liste_themes_etudiants, name='liste_themes_etudiants'),
    path('chef/themes/enregistrer/', views.enregistrer_theme_etudiant, name='enregistrer_theme_etudiant'),
    path('chef/themes/supprimer/<int:pk>/', views.supprimer_dossier_chef, name='supprimer_dossier_chef'),

    # Planning et Jurys
    path('chef/jurys/', views.liste_jurys_chef, name='liste_jurys_chef'),
    path('chef/jurys/enregistrer/', views.enregistrer_jury_chef, name='enregistrer_jury_chef'),
    path('chef/jurys/supprimer/<int:pk>/', views.supprimer_jury_chef, name='supprimer_jury_chef'),
  
    path('chef/planning/vagues/', views.planning_liste_vagues, name='planning_liste_vagues'),
    path('chef/planning/vague/<int:pk>/', views.planning_vague_detail, name='planning_vague_detail'),
    path('chef/planning/proposer/', views.proposer_soutenance, name='proposer_soutenance'),
    path('chef/planning/enregistrer/', views.enregistrer_planning, name='enregistrer_planning'),

  
# Liste des propositions envoyées par les chefs
    path('de/validation-jurys/', views.validation_jury_liste, name='validation_jury_liste'),
    # Action : Valider ou Rejeter (avec PK de la soutenance)
    path('de/validation-jurys/traiter/<int:pk>/', views.traiter_validation_jury, name='traiter_validation_jury'),
    # =========================================================
    # APIS JSON (POUR LE DYNAMISME DES MODALS ET FILTRES)
    # =========================================================
    # Récupérer les classes d'une filière
    path('get-classes/<int:filiere_id>/', views.get_classes, name='get_classes'),
    
    # Récupérer les étudiants par Classe et Année
    path('get-etudiants-par-classe-et-annee/<int:classe_id>/<int:annee_id>/', 
         views.get_etudiants_par_classe_et_annee, name='get_etudiants_par_classe_et_annee'),
         path('chef/rapports/', views.page_rapport_chef, name='page_rapport_chef'),

    # URL unique pour l'exportation (gère Excel et Word via les paramètres GET)
    path('chef/rapports/exporter/', views.exporter_rapport_complet, name='exporter_rapport_complet'),
    
    # URL pour la clôture manuelle des vagues (vu précédemment)
    path('vagues/cloturer/<int:pk>/', views.cloturer_vague, name='cloturer_vague'),
    path('modifier-etat-soutenu/', views.modifier_etat_soutenu, name='modifier_etat_soutenu'),
    path('planning/tout-soutenu/<int:vague_id>/', views.tout_cocher_soutenu, name='tout_cocher_soutenu'),

]