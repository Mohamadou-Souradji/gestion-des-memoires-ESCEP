from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from .models import DossierMemoire
from app_administration.models import Vague, Departement, Filiere, AnneeScolaire
from django.db import models  # <--- Ajoutez ceci pour corriger l'erreur
from django.db.models import Q # Importation spécifique pour les requêtes complexes
def is_surveillant(user):
    return user.is_authenticated and user.role == 'SURVEILLANT'


from django.db.models import Count


@login_required
@user_passes_test(is_surveillant, login_url='app_auth:login')
def dashboard_surveillant(request):
    # 1. Base des dossiers éligibles
    base_queryset = DossierMemoire.objects.filter(
        is_inscription_validee=True,
        is_semestres_valides=True,
        is_theme_valide=True
    )

    # 2. Statistiques Globales
    total_global_dossiers = base_queryset.count()
    total_pre_faits = base_queryset.filter(is_pre_depot_fait=True).count()
    total_post_faits = base_queryset.filter(is_post_depot_fait=True).count()
    total_publies = base_queryset.filter(is_soutenu=True).count()

    total_attente_pre = total_global_dossiers - total_pre_faits

    # 3. Statistiques par Filière (Approche simplifiée)
    filieres = Filiere.objects.all()
    stats_list = []

    for f in filieres:
        # On filtre les dossiers éligibles appartenant à cette filière
        dossiers_filiere = base_queryset.filter(etudiant__classe__filiere=f)

        attendus = dossiers_filiere.count()
        faits = dossiers_filiere.filter(is_pre_depot_fait=True).count()

        taux = (faits / attendus * 100) if attendus > 0 else 0

        stats_list.append({
            'filiere__nom': f.nom,
            'total_attendus': attendus,
            'total_faits': faits,
            'taux': taux
        })

    context = {
        'total_global_dossiers': total_global_dossiers,
        'total_pre_depots': total_pre_faits,
        'total_post_depots': total_post_faits,
        'total_attente_pre': total_attente_pre,
        'total_publies': total_publies,
        'stats_filiere': stats_list,
    }

    return render(request, 'surveillant/dashboard.html', context)

# Test de sécurité commun
def is_surveillant_ou_de(user):
    return user.is_authenticated and user.role in ['SURVEILLANT', 'DE']

# --- PRÉ-DÉPÔT (AVANT SOUTENANCE) ---
@login_required
@user_passes_test(is_surveillant_ou_de, login_url='app_auth:login')
def surveillant_pre_depot_liste(request):
    dossiers_queryset = DossierMemoire.objects.filter(
        is_inscription_validee=True,
        is_semestres_valides=True,
        is_theme_valide=True
    ).select_related('etudiant', 'etudiant__classe', 'etudiant__annee', 'etudiant__classe__filiere')

    q_matricule = request.GET.get('matricule', '').strip()
    f_id = request.GET.get('filiere')
    c_id = request.GET.get('classe')
    a_id = request.GET.get('annee_scolaire')

    has_filter = any([q_matricule, f_id, c_id, a_id])

    if q_matricule:
        dossiers_queryset = dossiers_queryset.filter(etudiant__matricule__icontains=q_matricule)
    if f_id:
        dossiers_queryset = dossiers_queryset.filter(etudiant__classe__filiere_id=f_id)
    if c_id:
        dossiers_queryset = dossiers_queryset.filter(etudiant__classe_id=c_id)
    if a_id:
        dossiers_queryset = dossiers_queryset.filter(etudiant__annee_id=a_id)

    dossiers = dossiers_queryset.order_by('etudiant__nom') if has_filter else []

    context = {
        'dossiers': dossiers,
        'filieres': Filiere.objects.all(),
        'classes': Classe.objects.filter(filiere_id=f_id) if f_id else Classe.objects.all(),
        'annees': AnneeScolaire.objects.all().order_by('-id'),
        'q_matricule': q_matricule,
        'has_filter': has_filter,
    }

    if request.user.role == 'DE':
        return render(request, 'administration/supervision/surveillance_pre.html', context)
    return render(request, 'surveillant/pre_depot_liste.html', context)

@login_required
@user_passes_test(is_surveillant_ou_de, login_url='app_auth:login')
def action_save_pdf(request, dossier_id):
    dossier = get_object_or_404(DossierMemoire, id=dossier_id)
    if request.method == 'POST':
        if 'delete' in request.POST:
            if dossier.fichier_pre_depot:
                dossier.fichier_pre_depot.delete()
            dossier.is_pre_depot_fait = False
            dossier.save()
            messages.warning(request, f"Dépôt de {dossier.etudiant.nom} retiré.")
        elif 'fichier_pdf' in request.FILES:
            dossier.fichier_pre_depot = request.FILES['fichier_pdf']
            dossier.is_pre_depot_fait = True
            dossier.save()
            messages.success(request, f"Pré-dépôt enregistré pour {dossier.etudiant.nom}.")
    return redirect(request.META.get('HTTP_REFERER'))

# --- POST-DÉPÔT (APRÈS SOUTENANCE) ---
@login_required
@user_passes_test(is_surveillant_ou_de, login_url='app_auth:login')
def surveillant_post_depot_liste(request):
    dossiers_queryset = DossierMemoire.objects.filter(
        is_pre_depot_fait=True,
        is_soutenu=True
    ).select_related('etudiant', 'etudiant__classe', 'etudiant__annee', 'etudiant__classe__filiere')

    q_matricule = request.GET.get('matricule', '').strip()
    f_id = request.GET.get('filiere')
    c_id = request.GET.get('classe')
    a_id = request.GET.get('annee_scolaire')

    has_filter = any([q_matricule, f_id, c_id, a_id])

    if q_matricule:
        dossiers_queryset = dossiers_queryset.filter(etudiant__matricule__icontains=q_matricule)
    if f_id:
        dossiers_queryset = dossiers_queryset.filter(etudiant__classe__filiere_id=f_id)
    if c_id:
        dossiers_queryset = dossiers_queryset.filter(etudiant__classe_id=c_id)
    if a_id:
        dossiers_queryset = dossiers_queryset.filter(etudiant__annee_id=a_id)

    dossiers = dossiers_queryset.order_by('etudiant__nom') if has_filter else []

    context = {
        'dossiers': dossiers,
        'filieres': Filiere.objects.all(),
        'classes': Classe.objects.filter(filiere_id=f_id) if f_id else Classe.objects.all(),
        'annees': AnneeScolaire.objects.all().order_by('-id'),
        'q_matricule': q_matricule,
        'has_filter': has_filter,
    }

    if request.user.role == 'DE':
        return render(request, 'administration/supervision/surveillance_post.html', context)
    return render(request, 'surveillant/post_depot_liste.html', context)

@login_required
@user_passes_test(is_surveillant_ou_de, login_url='app_auth:login')
def action_save_post_pdf(request, dossier_id):
    dossier = get_object_or_404(DossierMemoire, id=dossier_id)
    if request.method == 'POST':
        if 'delete' in request.POST:
            if dossier.fichier_post_depot:
                dossier.fichier_post_depot.delete()
            dossier.is_post_depot_fait = False
            dossier.save()
            messages.warning(request, f"Archive finale de {dossier.etudiant.nom} retirée.")
        elif 'fichier_pdf' in request.FILES:
            dossier.fichier_post_depot = request.FILES['fichier_pdf']
            dossier.is_post_depot_fait = True
            dossier.save()
            messages.success(request, f"Mémoire final de {dossier.etudiant.nom} archivé.")
    return redirect(request.META.get('HTTP_REFERER'))
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Etudiant, DossierMemoire
from app_administration.models import Classe, AnneeScolaire, Filiere

# Test de sécurité pour le rôle Scolarité
def is_scolarite(user):
    return user.is_authenticated and user.role == 'SCOLARITE'
@login_required
@user_passes_test(is_scolarite)
def scolarite_dashboard(request):
    total_etudiants = Etudiant.objects.count()
    semestres_valides = DossierMemoire.objects.filter(is_semestres_valides=True).count()
    semestres_en_attente = total_etudiants - semestres_valides
    
    # Statistiques par Filière pour le graphique ou tableau
    stats_filieres = Filiere.objects.all().annotate(
        total=models.Count('classes__etudiant'),
        valides=models.Count(
            'classes__etudiant__dossier', 
            filter=models.Q(classes__etudiant__dossier__is_semestres_valides=True)
        )
    )

    context = {
        'total_etudiants': total_etudiants,
        'semestres_valides': semestres_valides,
        'semestres_en_attente': semestres_en_attente,
        'stats_filieres': stats_filieres,
    }
    return render(request, 'scolarite/dashboard.html', context)

def is_scolarite_ou_de(user):
    return user.is_authenticated and user.role in ['SCOLARITE', 'DE']

@login_required
@user_passes_test(is_scolarite_ou_de)
def liste_etudiants_scolarite(request):
    filiere_id = request.GET.get('filiere')
    classe_id = request.GET.get('classe')
    annee_id = request.GET.get('annee')
    etat = request.GET.get('etat')
    search_matricule = request.GET.get('matricule')

    # Liste vide par défaut
    etudiants = Etudiant.objects.none()

    if any([filiere_id, classe_id, annee_id, etat, search_matricule]):
        etudiants = Etudiant.objects.select_related('classe__filiere', 'annee', 'dossier').all()

        if search_matricule:
            etudiants = etudiants.filter(matricule__icontains=search_matricule)
        if filiere_id:
            etudiants = etudiants.filter(classe__filiere_id=filiere_id)
        if classe_id:
            etudiants = etudiants.filter(classe_id=classe_id)
        if annee_id:
            etudiants = etudiants.filter(annee_id=annee_id)
        
        if etat == 'valide':
            etudiants = etudiants.filter(dossier__is_semestres_valides=True)
        elif etat == 'non_valide':
            etudiants = etudiants.filter(Q(dossier__isnull=True) | Q(dossier__is_semestres_valides=False))

    context = {
        'etudiants': etudiants,
        'filieres': Filiere.objects.all(),
        'classes': Classe.objects.filter(filiere_id=filiere_id) if filiere_id else Classe.objects.all(),
        'annees': AnneeScolaire.objects.all(),
    }

    # SELECTION DU TEMPLATE SELON LE ROLE
    if request.user.role == 'DE':
        return render(request, 'administration/supervision/scolarite.html', context)
    return render(request, 'scolarite/liste_etudiants.html', context)

@login_required
def toggle_semestres(request, matricule):
    etudiant = get_object_or_404(Etudiant, matricule=matricule)
    dossier, created = DossierMemoire.objects.get_or_create(etudiant=etudiant)

    # Sécurité
    if dossier.is_soutenu:
        messages.error(request, f"Modification impossible : {etudiant.nom} a déjà soutenu.")
        return redirect(request.META.get('HTTP_REFERER', 'gestion_interne:scolarite_etudiants'))

    dossier.is_semestres_valides = not dossier.is_semestres_valides
    dossier.save()

    etat = "validés" if dossier.is_semestres_valides else "invalidés"
    messages.success(request, f"Semestres de {etudiant.nom} {etat} avec succès.")

    # Retour à l'envoyeur (DE ou Scolarité reste sur sa page)
    return redirect(request.META.get('HTTP_REFERER', 'gestion_interne:scolarite_etudiants'))


@login_required
@user_passes_test(is_scolarite)
def scolarite_detail_attestations(request):
    # On récupère uniquement ces 4 filtres
    f_id = request.GET.get('filiere')
    c_id = request.GET.get('classe')
    a_id = request.GET.get('annee_acad')
    search = request.GET.get('search', '').strip()

    # Si l'un de ces champs est rempli, on cherche
    has_filter = any([f_id, c_id, a_id, search])

    if has_filter:
        # On prend tous les étudiants qui ont soutenu (peu importe la vague)
        etudiants = Etudiant.objects.filter(dossier__is_soutenu=True).select_related('classe__filiere', 'annee')

        if f_id: etudiants = etudiants.filter(classe__filiere_id=f_id)
        if c_id: etudiants = etudiants.filter(classe_id=c_id)
        if a_id: etudiants = etudiants.filter(annee_id=a_id)
        if search:
            etudiants = etudiants.filter(Q(nom__icontains=search) | Q(matricule__icontains=search))

        etudiants = etudiants.order_by('nom')
    else:
        etudiants = []

    context = {
        'etudiants': etudiants,
        'has_filter': has_filter,
        'filieres': Filiere.objects.all(),
        'classes': Classe.objects.filter(filiere_id=f_id) if f_id else [],
        'annees_options': AnneeScolaire.objects.all(),
    }
    return render(request, 'scolarite/vague_detail_attestations.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Etudiant, DossierMemoire, Classe, AnneeScolaire
from datetime import datetime

from django.shortcuts import render
from django.db.models import Q
from datetime import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
@login_required
def liste_etudiants_comptabilite(request):
    f_id = request.GET.get('filiere')
    c_id = request.GET.get('classe')
    a_id = request.GET.get('annee')
    search = request.GET.get('search', '').strip()

    has_filter = any([f_id, c_id, a_id, search])

    if has_filter:
        etudiants = Etudiant.objects.select_related('classe__filiere', 'annee', 'dossier').all()
        if f_id: etudiants = etudiants.filter(classe__filiere_id=f_id)
        if c_id: etudiants = etudiants.filter(classe_id=c_id)
        if a_id: etudiants = etudiants.filter(annee_id=a_id)
        if search:
            etudiants = etudiants.filter(Q(nom__icontains=search) | Q(matricule__icontains=search))
    else:
        etudiants = Etudiant.objects.none()

    context = {
        'etudiants': etudiants,
        'has_filter': has_filter,
        'filieres': Filiere.objects.all(),
        'classes': Classe.objects.filter(filiere_id=f_id) if f_id else Classe.objects.all(),
        'annees': AnneeScolaire.objects.all(),
    }
    
    # Choix du template selon le rôle (DE ou Comptable)
    if request.user.role == 'DE':
        return render(request, 'administration/supervision/comptabilite.html', context)
    return render(request, 'comptabilite/liste_etudiants.html', context)

@login_required
def toggle_inscription(request, matricule):
    if request.method == "POST":
        etudiant = get_object_or_404(Etudiant, matricule=matricule)
        dossier, created = DossierMemoire.objects.get_or_create(etudiant=etudiant)

        dossier.is_inscription_validee = not dossier.is_inscription_validee
        dossier.save()

        if dossier.is_inscription_validee:
            messages.success(request, f"Inscription validée pour {etudiant.nom} {etudiant.prenom}.")
        else:
            messages.warning(request, f"Validation annulée pour {etudiant.nom} {etudiant.prenom}.")

        # Redirection intelligente : renvoie le DE ou le Comptable sur sa page d'origine
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
        return redirect(next_url if next_url else 'gestion_interne:liste_etudiants_comptabilite')

    return redirect('gestion_interne:liste_etudiants_comptabilite')