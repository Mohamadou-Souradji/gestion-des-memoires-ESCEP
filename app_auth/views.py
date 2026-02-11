from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.cache import never_cache

def get_redirect_url(user):
    """
    Redirection stricte par rôle après connexion.
    L'étudiant est redirigé vers son propre dashboard sécurisé.
    """
    if not hasattr(user, 'role') or not user.role:
        logout(user)
        return redirect('app_auth:login')

    # Mapping mis à jour avec le rôle ETUDIANT
    destinations = {
        'DE': 'administration:dashboard_de',
        'CHEF_DEPT': 'administration:accueil_chef',
        'SCOLARITE': 'app_gestion_interne:scolarite_dashboard',
        'COMPTABLE': 'app_gestion_interne:liste_etudiants_comptabilite',
        'SURVEILLANT': 'app_gestion_interne:surveillant_dashboard',
        'BIBLIO': 'app_bibliotheque:dashboard',
        'ETUDIANT': 'app_bibliotheque:etudiant_dashboard', # Point vers la nouvelle vue
    }

    target = destinations.get(user.role)

    if target:
        return redirect(target)

    # Sécurité : Si rôle inconnu, on déconnecte
    logout(user)
    return redirect('app_auth:login')

@never_cache
def connexion_view(request):
    """
    Gère la connexion. Si l'utilisateur est déjà connecté,
    il est renvoyé vers son espace dédié selon son rôle.
    """
    if request.user.is_authenticated:
        return get_redirect_url(request.user)

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)

        if user:
            login(request, user)
            # Message de bienvenue personnalisé
            messages.success(request, f"Bienvenue, {user.first_name if user.first_name else user.username} !")
            return get_redirect_url(user)
        else:
            messages.error(request, "Nom utilisateur ou mot de passe incorrect.")

    return render(request, 'auth/login.html')

@never_cache
def deconnexion_view(request):
    """
    Déconnexion sécurisée avec destruction de session et de cache.
    """
    logout(request)
    request.session.flush()

    messages.info(request, "Session fermée. À bientôt !")

    response = redirect('app_auth:login')
    # Empêche de revenir en arrière après déconnexion (Crucial sur PC partagés)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
# REMPLACEZ l'import de User par celui-ci :
from django.contrib.auth import get_user_model

# Récupération du modèle utilisateur actif
User = get_user_model()


def mot_de_passe_oublie(request):
    step = 1

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'verifier':
            username = request.POST.get('username')
            email = request.POST.get('email')

            # Utilisation du modèle récupéré via get_user_model()
            try:
                user = User.objects.get(username=username, email=email)
                request.session['reset_user_id'] = user.id
                step = 2
            except User.DoesNotExist:
                messages.error(request, "Aucun compte ne correspond à ces informations.")

        elif action == 'reinitialiser':
            user_id = request.session.get('reset_user_id')
            new_password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if user_id and new_password == confirm_password:
                try:
                    user = User.objects.get(id=user_id)
                    user.password = make_password(new_password)
                    user.save()
                    del request.session['reset_user_id']
                    messages.success(request, "Mot de passe modifié avec succès !")
                    return redirect('app_auth:login')
                except User.DoesNotExist:
                    messages.error(request, "Utilisateur introuvable.")
                    return redirect('app_auth:password_reset')
            else:
                messages.error(request, "Les mots de passe ne correspondent pas.")
                step = 2

    return render(request, 'auth/password_reset.html', {'step': step})