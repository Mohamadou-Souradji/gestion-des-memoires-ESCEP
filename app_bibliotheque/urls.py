from django.urls import path
from . import views

app_name = 'app_bibliotheque'

urlpatterns = [
    # Dashboard principal
    path('dashboard/', views.bibliotheque_dashboard, name='dashboard'),

    # --- SECTION MÉMOIRES ---
    # Liste des mémoires en attente de publication
     path('memoires/attente/', views.liste_memoires_attente, name='liste_memoires_attente'),
    # Action de publication
    path('memoires/publier/<str:matricule>/', views.publier_memoire, name='publier_memoire'),

    # --- SECTION LIVRES (CRUD) ---
    path('livres/', views.liste_livres, name='liste_livres'),
    path('livres/ajouter/', views.ajouter_livre, name='ajouter_livre'),
    path('livres/modifier/<int:pk>/', views.modifier_livre, name='modifier_livre'),
    path('livres/supprimer/<int:pk>/', views.supprimer_livre, name='supprimer_livre'),
path('categories/', views.gestion_categories, name='gestion_categories'),
    path('memoires/liste/', views.liste_memoires_publication, name='liste_memoires_attente'),
path('livres/toggle-pub/<int:pk>/', views.toggle_publication_livre, name='toggle_publication_livre'),

path('memoires/toggle/<str:matricule>/', views.toggle_publication, name='toggle_publication'),

    path('espace-etudiant/', views.etudiant_dashboard, name='etudiant_dashboard'),

    # Liste des livres pour étudiants
    path('espace-etudiant/livres/', views.liste_livres_etudiant, name='liste_livres_etudiant'),

    # Liste des mémoires pour étudiants
    path('espace-etudiant/memoires/', views.liste_memoires_etudiant, name='liste_memoires_etudiant'),

]