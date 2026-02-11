# app_auth/urls.py
from django.urls import path
from . import views  

app_name = 'app_auth'

urlpatterns = [
    path('login/', views.connexion_view, name='login'),
    path('logout/', views.deconnexion_view, name='logout'),
path('mot-de-passe-oublie/', views.mot_de_passe_oublie, name='password_reset'),
]