from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app_gestion_interne.models import Etudiant
from .models import Livre, JournalOperation, Categorie
from .forms import LivreForm, CategorieForm

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Livre, JournalOperation, Categorie
# Importe ton modèle Etudiant (ajuste le chemin si nécessaire)
@login_required
def bibliotheque_dashboard(request):
    # --- STATISTIQUES LIVRES ---
    nb_livres = Livre.objects.count()
    livres_publies = Livre.objects.filter(is_publie=True).count()
    livres_brouillons = nb_livres - livres_publies

    # --- MÉMOIRES / ÉTUDIANTS ---
    # On remplace 'date_post_depot' par 'id' pour éviter l'erreur FieldError
    etudiants_en_attente = Etudiant.objects.filter(
        dossier__is_post_depot_fait=True,
        dossier__is_publie=False
    ).select_related('classe', 'dossier').order_by('-dossier__id')[:5]

    a_publier = Etudiant.objects.filter(
        dossier__is_post_depot_fait=True,
        dossier__is_publie=False
    ).count()

    # --- ACTIVITÉS RÉCENTES ---
    logs = JournalOperation.objects.all().order_by('-date_action')[:6]

    context = {
        'nb_livres': nb_livres,
        'livres_publies': livres_publies,
        'livres_brouillons': livres_brouillons,
        'a_publier': a_publier,
        'etudiants_recents': etudiants_en_attente,
        'logs': logs,
    }
    return render(request, 'bibliotheque/dashboard.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from app_gestion_interne.models import Etudiant, DossierMemoire
from app_administration.models import Filiere, Classe, AnneeScolaire
from django.contrib import messages

from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test # <--- Ajoutez user_passes_test ici

# Fonction de test de rôle pour le décorateur
def is_biblio_ou_de(user):
    return user.is_authenticated and user.role in ['BIBLIO', 'DE']

@login_required
@user_passes_test(is_biblio_ou_de, login_url='app_auth:login')
def liste_memoires_publication(request):
    f_id = request.GET.get('filiere')
    c_id = request.GET.get('classe')
    a_id = request.GET.get('annee')
    statut = request.GET.get('statut')
    search = request.GET.get('q')

    # Base : Étudiants ayant fait le dépôt final post-soutenance
    etudiants = Etudiant.objects.filter(dossier__is_post_depot_fait=True).select_related('dossier', 'classe', 'annee')

    if f_id: etudiants = etudiants.filter(classe__filiere_id=f_id)
    if c_id: etudiants = etudiants.filter(classe_id=c_id)
    if a_id: etudiants = etudiants.filter(annee_id=a_id)
    if search:
        etudiants = etudiants.filter(Q(nom__icontains=search) | Q(prenom__icontains=search) | Q(matricule__icontains=search))
    
    if statut == 'publie':
        etudiants = etudiants.filter(dossier__is_publie=True)
    elif statut == 'non_publie':
        etudiants = etudiants.filter(dossier__is_publie=False)

    etudiants = etudiants.order_by('-dossier__is_publie', 'nom')

    context = {
        'etudiants': etudiants,
        'filieres': Filiere.objects.all(),
        'classes': Classe.objects.filter(filiere_id=f_id) if f_id else Classe.objects.all(),
        'annees': AnneeScolaire.objects.all().order_by('-libelle'),
    }

    # Redirection vers le template Superadmin si DE
    if request.user.role == 'DE':
        return render(request, 'administration/supervision/biblio_memoires.html', context)
    return render(request, 'bibliotheque/liste_memoires.html', context)

@login_required
@user_passes_test(is_biblio_ou_de, login_url='app_auth:login')
def toggle_publication(request, matricule):
    etudiant = get_object_or_404(Etudiant, matricule=matricule)
    dossier = etudiant.dossier
    dossier.is_publie = not dossier.is_publie
    dossier.save()

    JournalOperation.objects.create(
        action="MEMOIRE_PUBLI" if dossier.is_publie else "LIVRE_SUPP",
        details=f"{'Publication' if dossier.is_publie else 'Retrait'} du mémoire de {etudiant.nom}",
        effectue_par=request.user
    )
    
    # Reste sur la page actuelle avec les filtres conservés
    return redirect(request.META.get('HTTP_REFERER', 'app_bibliotheque:dashboard'))

# --- GESTION DES MÉMOIRES ---
@login_required
def liste_memoires_attente(request):
    etudiants = Etudiant.objects.filter(
        dossier__is_post_depot_fait=True,
        dossier__is_publie=False
    ).select_related('dossier', 'classe')
    return render(request, 'bibliotheque/liste_memoires.html', {'etudiants': etudiants})


@login_required
def publier_memoire(request, matricule):
    etudiant = get_object_or_404(Etudiant, matricule=matricule)
    dossier = etudiant.dossier
    dossier.is_publie = True
    dossier.save()

    JournalOperation.objects.create(
        action="MEMOIRE_PUBLI",
        details=f"Publication du mémoire de {etudiant.nom} {etudiant.prenom}",
        effectue_par=request.user
    )
    messages.success(request, f"Le mémoire de {etudiant.nom} est maintenant disponible au public.")
    return redirect('app_bibliotheque:liste_memoires_attente')


# --- CRUD LIVRES
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Categorie, JournalOperation
from .forms import CategorieForm

# --- GESTION DES CATÉGORIES (Adaptée DE) ---
@login_required
@user_passes_test(is_biblio_ou_de, login_url='app_auth:login')
def gestion_categories(request):
    categories = Categorie.objects.all().order_by('nom')
    is_de = (request.user.role == 'DE')

    if request.method == 'POST':
        if 'delete_id' in request.POST:
            cat = get_object_or_404(Categorie, id=request.POST.get('delete_id'))
            nom_cat = cat.nom
            cat.delete()
            messages.warning(request, f"Catégorie '{nom_cat}' supprimée.")
        else:
            instance_id = request.POST.get('cat_id')
            instance = get_object_or_404(Categorie, id=instance_id) if instance_id else None
            form = CategorieForm(request.POST, instance=instance)
            if form.is_valid():
                cat = form.save()
                messages.success(request, f"Catégorie '{cat.nom}' enregistrée.")
        
        return redirect('app_bibliotheque:gestion_categories')

    form = CategorieForm()
    context = {'categories': categories, 'form': form, 'is_de': is_de}
    
    # Template miroir si c'est le DE
    template = 'administration/supervision/biblio_categories.html' if is_de else 'bibliotheque/gestion_categories.html'
    return render(request, template, context)

# --- GESTION DES LIVRES (Adaptée DE) ---
@login_required
@user_passes_test(is_biblio_ou_de, login_url='app_auth:login')
def liste_livres(request):
    query = request.GET.get('q', '')
    cat_id = request.GET.get('categorie', '')
    is_de = (request.user.role == 'DE')

    livres = Livre.objects.all().select_related('categorie')
    if query:
        livres = livres.filter(Q(titre__icontains=query) | Q(auteur__icontains=query) | Q(isbn__icontains=query))
    if cat_id:
        livres = livres.filter(categorie_id=cat_id)

    context = {
        'livres': livres,
        'categories_list': Categorie.objects.all(),
        'query': query,
        'is_de': is_de
    }
    
    template = 'administration/supervision/biblio_livres_liste.html' if is_de else 'bibliotheque/liste_livres.html'
    return render(request, template, context)
@login_required
def toggle_publication_livre(request, pk):
    livre = get_object_or_404(Livre, pk=pk)
    livre.is_publie = not livre.is_publie
    livre.save()

    status = "publié" if livre.is_publie else "retiré de la publication"
    messages.info(request, f"Le livre '{livre.titre}' est désormais {status}.")

    # Redirige vers la page précédente (le catalogue avec les filtres actuels)
    return redirect(request.META.get('HTTP_REFERER', 'app_bibliotheque:liste_livres'))


@login_required
@user_passes_test(is_biblio_ou_de)
def ajouter_livre(request):
    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        # ATTENTION : Il faut ajouter request.FILES ici !
        form = LivreForm(request.POST, request.FILES)

        if form.is_valid():
            livre = form.save()
            messages.success(request, f"Le livre '{livre.titre}' a été enregistré.")
            if next_url:
                return redirect(next_url)
            return redirect('app_bibliotheque:liste_livres')
        else:
            # Si le formulaire est invalide, on affiche les erreurs dans la console pour déboguer
            print(form.errors)
            messages.error(request, "Erreur lors de l'enregistrement. Vérifiez les champs.")
    else:
        form = LivreForm()

    is_de = (request.user.role == 'DE')
    template = 'administration/supervision/biblio_form_livre.html' if is_de else 'bibliotheque/form_livre.html'
    return render(request, template, {'form': form, 'next': next_url, 'title': "Ajouter un livre"})
# modifier_livre et supprimer_livre restent identiques à ton code,
# ils fonctionnent déjà avec l'ID (pk)


@login_required
def modifier_livre(request, pk):
    livre = get_object_or_404(Livre, pk=pk)
    if request.method == 'POST':
        form = LivreForm(request.POST, request.FILES, instance=livre)
        if form.is_valid():
            form.save()
            messages.success(request, "Livre mis à jour.")
            return redirect('app_bibliotheque:liste_livres')
    else:
        form = LivreForm(instance=livre)
    return render(request, 'bibliotheque/form_livre.html', {'form': form, 'title': "Modifier le livre"})


@login_required
def supprimer_livre(request, pk):
    livre = get_object_or_404(Livre, pk=pk)
    titre = livre.titre
    livre.delete()
    messages.warning(request, f"Livre '{titre}' supprimé.")
    return redirect('app_bibliotheque:liste_livres')


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Livre


@login_required
def etudiant_dashboard(request):
    # Sécurité : vérifier que c'est bien un étudiant
    if request.user.role != 'ETUDIANT':
        return redirect('app_auth:login')

    # Dernier livre publié
    dernier_livre = Livre.objects.filter(is_publie=True).order_by('-id').first()

    # Dernier mémoire publié
    dernier_memoire = Etudiant.objects.filter(dossier__is_publie=True).select_related('classe', 'dossier').order_by(
        '-dossier__id').first()

    # Compteurs pour les badges d'actions rapides
    total_livres = Livre.objects.filter(is_publie=True).count()
    total_memoires = Etudiant.objects.filter(dossier__is_publie=True).count()

    context = {
        'dernier_livre': dernier_livre,
        'dernier_memoire': dernier_memoire,
        'total_livres': total_livres,
        'total_memoires': total_memoires,
    }
    return render(request, 'etudiant/dashboard.html', context)

@login_required
def liste_memoires_etudiant(request):
    if request.user.role != 'ETUDIANT':
        return redirect('app_auth:login')

    # Base : Etudiants ayant un dossier publie
    memoires = Etudiant.objects.filter(
        dossier__is_publie=True
    ).select_related('classe', 'classe__filiere', 'dossier', 'dossier__vague').order_by('-dossier__id')

    # Recuperation des filtres
    filiere_id = request.GET.get('filiere')
    classe_id = request.GET.get('classe')
    annee = request.GET.get('annee')
    query = request.GET.get('q')

    if filiere_id:
        memoires = memoires.filter(classe__filiere_id=filiere_id)
    if classe_id:
        memoires = memoires.filter(classe_id=classe_id)
    if annee:
        memoires = memoires.filter(dossier__vague__annee=annee)
    if query:
        memoires = memoires.filter(
            Q(dossier__theme__icontains=query) |
            Q(nom__icontains=query) |
            Q(prenom__icontains=query)
        )

    context = {
        'memoires': memoires,
        'filieres': Filiere.objects.all(),
        'classes': Classe.objects.all(),
        'annees': range(2022, 2027), # Ajuste selon tes besoins
    }
    return render(request, 'etudiant/liste_memoires.html', context)

@login_required
def liste_livres_etudiant(request):
    if request.user.role != 'ETUDIANT':
        return redirect('app_auth:login')

    # On récupère uniquement les livres marqués comme publiés
    livres = Livre.objects.filter(is_publie=True).select_related('categorie').order_by('titre')

    # Gestion des filtres
    categorie_id = request.GET.get('categorie')
    query = request.GET.get('q')

    if categorie_id:
        livres = livres.filter(categorie_id=categorie_id)
    if query:
        livres = livres.filter(
            Q(titre__icontains=query) | Q(auteur__icontains=query)
        )

    context = {
        'livres': livres,
        'categories': Categorie.objects.all(),
    }
    return render(request, 'etudiant/liste_livres.html', context)