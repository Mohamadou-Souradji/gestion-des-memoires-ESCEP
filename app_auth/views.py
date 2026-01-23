from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def get_redirect_url(user):
    """
    Centralisation des redirections selon le rôle utilisateur.
    """
    # On vérifie si l'utilisateur a un rôle, sinon on le déconnecte ou redirige vers login
    if not hasattr(user, 'role') or not user.role:
        return redirect('app_auth:login')

    if user.role == 'CHEF_DEPT':
        return redirect('administration:accueil_chef')

    elif user.role == 'SURVEILLANT':
        return redirect('app_gestion_interne:surveillant_dashboard')

    elif user.role == 'SCOLARITE':
        return redirect('app_gestion_interne:scolarite_dashboard')

    # AJOUT DU RÔLE COMPTABILITE
    elif user.role == 'COMPTABLE':
        return redirect('app_gestion_interne:liste_etudiants_comptabilite')

    elif user.role == 'DE':
        return redirect('administration:dashboard_de')

    # Redirection par défaut pour les autres rôles administratifs
    return redirect('administration:dashboard_de')


def connexion_view(request):
    if request.user.is_authenticated:
        return get_redirect_url(request.user)

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)

        if user:
            login(request, user)
            messages.success(request, f"Connexion réussie. Bienvenue {user.username} !")
            return get_redirect_url(user)
        else:
            messages.error(request, "Identifiant ou mot de passe incorrect.")

    return render(request, 'auth/login.html')


def deconnexion_view(request):
    logout(request)
    return redirect('app_auth:login')