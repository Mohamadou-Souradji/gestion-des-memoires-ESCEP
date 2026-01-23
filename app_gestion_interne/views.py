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

@login_required
@user_passes_test(is_surveillant, login_url='app_auth:login')
def dashboard_surveillant(request):
    """Dash avec stats réelles par filière"""
    stats_filieres = []
    filieres = Filiere.objects.select_related('departement').all()

    for f in filieres:
        # Éligibles (Les 3 conditions : Inscription, Semestre, Thème)
        eligibles = DossierMemoire.objects.filter(
            etudiant__classe__filiere=f,
            is_inscription_validee=True,
            is_semestres_valides=True,
            is_theme_valide=True
        ).count()
        
        faits = DossierMemoire.objects.filter(
            etudiant__classe__filiere=f,
            is_pre_depot_fait=True
        ).count()

        stats_filieres.append({
            'filiere': f,
            'eligibles': eligibles,
            'faits': faits,
            'manquants': eligibles - faits,
            'progression': (faits * 100 / eligibles) if eligibles > 0 else 0
        })

    return render(request, 'surveillant/dashboard.html', {'stats': stats_filieres})

@login_required
@user_passes_test(is_surveillant, login_url='app_auth:login')
def surveillant_vagues(request):
    """Liste des vagues par année de création"""
    vagues = Vague.objects.all().order_by('-date_creation')
    return render(request, 'surveillant/vagues_liste.html', {'vagues': vagues})

@login_required
@user_passes_test(is_surveillant, login_url='app_auth:login')
def surveillant_pre_depot_liste(request, vague_id):
    vague = get_object_or_404(Vague, id=vague_id)
    
    # 1. On récupère les années scolaires concernées par la vague actuelle
    annees_ids = vague.annees_concernees.values_list('id', flat=True)

    # 2. FILTRAGE LOGIQUE ANTI-DOUBLON
    # On filtre les dossiers dont l'étudiant est dans une des années de la vague
    # ET dont les pré-requis (thème, inscription, semestres) sont validés
    dossiers = DossierMemoire.objects.filter(
        etudiant__annee_id__in=annees_ids,
        is_theme_valide=True,
        is_semestres_valides=True,
        is_inscription_validee=True
    ).filter(
        # CONDITION CRUCIALE :
        # L'étudiant apparaît s'il n'est rattaché à AUCUNE vague (vague__isnull=True)
        # OU s'il est rattaché spécifiquement à CETTE vague (vague=vague)
        Q(vague__isnull=True) | Q(vague=vague)
    ).select_related('etudiant', 'etudiant__classe', 'etudiant__annee')

    # 3. Filtres de l'interface (Promotion, Filière, Classe)
    f_id = request.GET.get('filiere')
    c_id = request.GET.get('classe')
    a_id = request.GET.get('annee_scolaire')

    if f_id: dossiers = dossiers.filter(etudiant__classe__filiere_id=f_id)
    if c_id: dossiers = dossiers.filter(etudiant__classe_id=c_id)
    if a_id: dossiers = dossiers.filter(etudiant__annee_id=a_id)

    context = {
        'vague': vague,
        'is_ouverte': vague.est_active_generale, 
        'dossiers': dossiers,
        'filieres': Filiere.objects.all(),
        'classes': Classe.objects.filter(filiere_id=f_id) if f_id else None,
        'annees_vague': vague.annees_concernees.all(),
    }
    return render(request, 'surveillant/pre_depot_liste.html', context)

# Ajoute Classe dans tes imports en haut
from app_administration.models import Vague, Departement, Filiere, AnneeScolaire, Classe

@login_required
@user_passes_test(is_surveillant, login_url='app_auth:login')
def action_save_pdf(request, dossier_id):
    dossier = get_object_or_404(DossierMemoire, id=dossier_id)
    
    # On récupère l'ID de la vague depuis le formulaire modal
    vague_id = request.POST.get('vague_id')

    if request.method == 'POST':
        # --- 1. CAS SUPPRESSION ---
        if 'delete' in request.POST:
            if dossier.fichier_pre_depot:
                dossier.fichier_pre_depot.delete()
            
            dossier.is_pre_depot_fait = False
            dossier.vague = None  # ON LIBÈRE L'ÉTUDIANT (plus rattaché à cette vague)
            dossier.save()
            
            messages.warning(request, f"Dépôt de {dossier.etudiant.nom} supprimé. L'étudiant est à nouveau disponible.")

        # --- 2. CAS UPLOAD ---
        elif 'fichier_pdf' in request.FILES:
            if not vague_id:
                messages.error(request, "Erreur : ID de la vague manquant.")
                return redirect(request.META.get('HTTP_REFERER'))

            # On vérifie si la vague est bien ouverte avant d'enregistrer
            vague_actuelle = get_object_or_404(Vague, id=vague_id)
            if not vague_actuelle.est_active_generale:
                messages.error(request, "Impossible : Cette vague est clôturée.")
                return redirect(request.META.get('HTTP_REFERER'))

            # Enregistrement du fichier et verrouillage de la vague
            dossier.fichier_pre_depot = request.FILES['fichier_pdf']
            dossier.is_pre_depot_fait = True
            dossier.vague = vague_actuelle  # ON VERROUILLE L'ÉTUDIANT À CETTE VAGUE
            dossier.save()
            
            messages.success(request, f"Pré-dépôt de {dossier.etudiant.nom} validé pour la vague {vague_actuelle.libelle}.")

    return redirect(request.META.get('HTTP_REFERER'))

@login_required
@user_passes_test(is_surveillant, login_url='app_auth:login')
def surveillant_vagues_post(request):
    """Même principe que les vagues pré-dépôt mais pour le circuit final"""
    vagues = Vague.objects.all().order_by('-date_creation')
    return render(request, 'surveillant/vagues_post_liste.html', {'vagues': vagues})

# --- LISTE DES ÉTUDIANTS ÉLIGIBLES AU DÉPÔT FINAL ---
from django.db.models import Q

@login_required
@user_passes_test(is_surveillant, login_url='app_auth:login')
def surveillant_post_depot_liste(request, vague_id):
    vague = get_object_or_404(Vague, id=vague_id)
    annees_ids = vague.annees_concernees.values_list('id', flat=True)

    # LOGIQUE POST-DÉPÔT SÉCURISÉE : 
    # 1. L'étudiant doit appartenir aux années de la vague.
    # 2. Il doit impérativement être rattaché à CETTE vague précise (vague=vague).
    # 3. Il doit avoir fait son pré-dépôt ET avoir soutenu.
    dossiers = DossierMemoire.objects.filter(
        vague=vague, # Verrouillage strict sur la vague actuelle
        etudiant__annee_id__in=annees_ids,
        is_pre_depot_fait=True,
        is_soutenu=True
    ).select_related('etudiant', 'etudiant__classe', 'etudiant__annee')

    # Filtres de l'interface
    f_id = request.GET.get('filiere')
    c_id = request.GET.get('classe')
    a_id = request.GET.get('annee_scolaire')

    if f_id: dossiers = dossiers.filter(etudiant__classe__filiere_id=f_id)
    if c_id: dossiers = dossiers.filter(etudiant__classe_id=c_id)
    if a_id: dossiers = dossiers.filter(etudiant__annee_id=a_id)

    context = {
        'vague': vague,
        'is_ouverte': vague.est_active_generale, 
        'dossiers': dossiers,
        'filieres': Filiere.objects.all(),
        'classes': Classe.objects.filter(filiere_id=f_id) if f_id else None,
        'annees_vague': vague.annees_concernees.all(),
    }
    return render(request, 'surveillant/post_depot_liste.html', context)

@login_required
@user_passes_test(is_surveillant, login_url='app_auth:login')
def action_save_post_pdf(request, dossier_id):
    dossier = get_object_or_404(DossierMemoire, id=dossier_id)
    
    if request.method == 'POST':
        # CAS SUPPRESSION
        if 'delete' in request.POST:
            if dossier.fichier_post_depot:
                dossier.fichier_post_depot.delete()
            dossier.is_post_depot_fait = False
            dossier.save()
            messages.warning(request, f"Dépôt final de {dossier.etudiant.nom} supprimé.")
        
        # CAS UPLOAD FINAL
        elif 'fichier_pdf' in request.FILES:
            dossier.fichier_post_depot = request.FILES['fichier_pdf']
            dossier.is_post_depot_fait = True
            dossier.save()
            messages.success(request, f"Mémoire final de {dossier.etudiant.nom} archivé avec succès.")

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

@login_required
@user_passes_test(is_scolarite)
def liste_etudiants_scolarite(request):
    filiere_id = request.GET.get('filiere')
    classe_id = request.GET.get('classe')
    annee_id = request.GET.get('annee')
    etat = request.GET.get('etat') # Nouveau filtre d'état

    # Base des étudiants
    etudiants = Etudiant.objects.select_related('classe__filiere', 'annee', 'dossier').all()

    # Application des filtres
    if filiere_id:
        etudiants = etudiants.filter(classe__filiere_id=filiere_id)
    if classe_id:
        etudiants = etudiants.filter(classe_id=classe_id)
    if annee_id:
        etudiants = etudiants.filter(annee_id=annee_id)
    
    # Filtre par état du dossier (via la relation OneToOne)
    if etat == 'valide':
        etudiants = etudiants.filter(dossier__is_semestres_valides=True)
    elif etat == 'non_valide':
        # On prend ceux qui n'ont pas de dossier OU dont le dossier est à False
        etudiants = etudiants.filter(Q(dossier__isnull=True) | Q(dossier__is_semestres_valides=False))

    # Logique pour le sélecteur de classes dynamique
    if filiere_id:
        classes_filtrees = Classe.objects.filter(filiere_id=filiere_id)
    else:
        classes_filtrees = Classe.objects.all()

    context = {
        'etudiants': etudiants,
        'filieres': Filiere.objects.all(),
        'classes': classes_filtrees, # On ne passe que les classes utiles
        'annees': AnneeScolaire.objects.all(),
    }
    return render(request, 'scolarite/liste_etudiants.html', context)
@login_required
@user_passes_test(is_scolarite)
def toggle_semestres(request, matricule):
    """
    Une seule vue pour Valider/Invalider (Toggle) 
    C'est plus moderne et évite de multiplier les URLs.
    """
    etudiant = get_object_or_404(Etudiant, matricule=matricule)
    
    # get_or_create : Si le dossier n'existe pas (Dev 1 pas encore passé), on le crée
    dossier, created = DossierMemoire.objects.get_or_create(etudiant=etudiant)
    
    # Inversion de l'état
    dossier.is_semestres_valides = not dossier.is_semestres_valides
    dossier.save()
    
    etat = "validés" if dossier.is_semestres_valides else "invalidés"
    messages.success(request, f"Semestres de {etudiant.nom} {etat} avec succès.")
    
    return redirect(request.META.get('HTTP_REFERER', 'app_gestion_interne:scolarite_etudiants'))


@login_required
@user_passes_test(is_scolarite)
def scolarite_vagues_attestations(request):
    # On récupère toutes les vagues pour le regroupement par année
    vagues = Vague.objects.all().order_by('-date_creation')
    return render(request, 'scolarite/vagues_liste.html', {'vagues': vagues})


@login_required
@user_passes_test(is_scolarite)
def scolarite_detail_attestations(request, vague_id):
    """Consultation des étudiants par vague via la relation Dossier"""
    vague = get_object_or_404(Vague, id=vague_id)

    # Récupération des filtres
    f_id = request.GET.get('filiere')
    c_id = request.GET.get('classe')
    a_id = request.GET.get('annee_acad')

    # CORRECTION ICI : On filtre les étudiants dont le dossier appartient à cette vague
    # et qui ont soutenu.
    etudiants = Etudiant.objects.filter(
        dossier__vague=vague,
        dossier__is_soutenu=True
    )

    # Application des autres filtres
    if f_id:
        etudiants = etudiants.filter(classe__filiere_id=f_id)
    if c_id:
        etudiants = etudiants.filter(classe_id=c_id)
    if a_id:
        etudiants = etudiants.filter(annee_id=a_id)

    context = {
        'vague': vague,
        'etudiants': etudiants.select_related('classe__filiere', 'annee', 'dossier'),
        'filieres': Filiere.objects.all(),
        'classes': Classe.objects.filter(filiere_id=f_id) if f_id else Classe.objects.all(),
        'annees_options': AnneeScolaire.objects.all(),
    }
    return render(request, 'scolarite/vague_detail_attestations.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Etudiant, DossierMemoire, Classe, AnneeScolaire
from datetime import datetime


@login_required
def liste_etudiants_comptabilite(request):
    filiere_id = request.GET.get('filiere')
    classe_id = request.GET.get('classe')
    annee_id = request.GET.get('annee')
    search = request.GET.get('search')

    etudiants = Etudiant.objects.select_related('classe__filiere', 'annee').prefetch_related('dossier').all()

    # Filtre par Filière
    if filiere_id:
        etudiants = etudiants.filter(classe__filiere_id=filiere_id)

    # Filtre par Classe
    if classe_id:
        etudiants = etudiants.filter(classe_id=classe_id)

    # Filtre par Année
    if annee_id:
        etudiants = etudiants.filter(annee_id=annee_id)

    # Recherche Nom/Matricule
    if search:
        etudiants = etudiants.filter(nom__icontains=search) | etudiants.filter(matricule__icontains=search)

    context = {
        'etudiants': etudiants,
        'filieres': Filiere.objects.all(),
        # Si une filière est choisie, on ne montre que ses classes
        'classes': Classe.objects.filter(filiere_id=filiere_id) if filiere_id else Classe.objects.all(),
        'annees': AnneeScolaire.objects.all(),
        'current_year': datetime.now().year,
    }
    return render(request, 'comptabilite/liste_etudiants.html', context)


@login_required
def toggle_inscription(request, matricule):
    """Bouton unique pour Valider/Annuler avec sécurité soutenance"""
    etudiant = get_object_or_404(Etudiant, matricule=matricule)
    dossier, created = DossierMemoire.objects.get_or_create(etudiant=etudiant)

    # Sécurité : Si déjà soutenu, on ne change plus rien
    if not dossier.is_soutenu:
        dossier.is_inscription_validee = not dossier.is_inscription_validee
        dossier.save()

    return redirect('app_gestion_interne:liste_etudiants_comptabilite')