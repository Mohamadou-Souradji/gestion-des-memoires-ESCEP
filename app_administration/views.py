from django.contrib.auth.decorators import login_required
from .models import Filiere, Departement,Classe,AnneeScolaire,Vague,ClotureVagueDepartement
from app_gestion_interne.models import Etudiant, DossierMemoire
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from app_gestion_interne.models import DossierMemoire, Etudiant # Modèles qui sont dans auth
from django.core.exceptions import FieldError
from django.db.models import Q

@login_required
def dashboard_directeur(request):
    # ... (vos statistiques précédentes) ...
    nb_depts = Departement.objects.count()
    nb_etudiants = Etudiant.objects.count()
    nb_soutenances = DossierMemoire.objects.filter(is_soutenu=True).count()
    # On compte les dossiers où le jury n'est pas encore validé par le DE
    nb_attente_validation = Soutenance.objects.filter(status='PROPOSE').count()
    
    # 3 derniers étudiants inscrits
    derniers_etudiants = Etudiant.objects.select_related('classe').order_by('-matricule')[:3]
    
    # Répartition par département (méthode robuste)
    departements = Departement.objects.all()
    stats_depts = []
    for dept in departements:
        count = Etudiant.objects.filter(classe__filiere__departement=dept).count()
        stats_depts.append({'nom': dept.nom, 'total_etudiants': count})

    context = {
        'nb_depts': nb_depts,
        'nb_etudiants': nb_etudiants,
        'nb_soutenances': nb_soutenances,
        'nb_attente_validation': nb_attente_validation,
        'stats_depts': stats_depts,
        'derniers_etudiants': derniers_etudiants,
    }
    return render(request, 'administration/dashboard_de.html', context)

def liste_annees(request):
    annees = AnneeScolaire.objects.all().order_by('-libelle')
    
    if request.method == 'POST':
        libelle = request.POST.get('libelle').strip()
        
        # Verification de l'unicite du libelle
        if AnneeScolaire.objects.filter(libelle=libelle).exists():
            messages.error(request, f"L'annee {libelle} existe deja dans le systeme.")
        else:
            # On cree l'annee (par defaut inactive pour ne pas perturber l'actuelle)
            AnneeScolaire.objects.create(libelle=libelle, est_active=False)
            messages.success(request, f"Annee {libelle} creee avec succes.")
        
        return redirect('administration:liste_annees')

    return render(request, 'administration/liste_annees.html', {'annees': annees})

def activer_annee(request, pk):
    # On desactive toutes les annees d'abord
    AnneeScolaire.objects.update(est_active=False)
    # On active l'annee selectionnee
    annee = get_object_or_404(AnneeScolaire, pk=pk)
    annee.est_active = True
    annee.save()
    messages.success(request, f"L'annee {annee.libelle} est desormais l'annee en cours.")
    return redirect('administration:liste_annees')

def supprimer_annee(request, pk):
    annee = get_object_or_404(AnneeScolaire, pk=pk)
    if annee.est_active:
        messages.error(request, "Impossible de supprimer l'annee en cours.")
    else:
        annee.delete()
        messages.warning(request, "Annee supprimee.")
    return redirect('administration:liste_annees')

#gestion des departements
def liste_departements(request):
    departements = Departement.objects.all().order_by('nom')
    
    if request.method == 'POST':
        nom = request.POST.get('nom').strip()
        
        # Vérification de l'unicité du nom
        if Departement.objects.filter(nom__iexact=nom).exists():
            messages.error(request, f"Le département '{nom}' existe déjà.")
        else:
            Departement.objects.create(nom=nom)
            messages.success(request, f"Département '{nom}' ajouté avec succès.")
        
        return redirect('administration:liste_departements')

    return render(request, 'administration/liste_departements.html', {'departements': departements})

def supprimer_departement(request, pk):
    dept = get_object_or_404(Departement, pk=pk)
    # On peut ajouter une sécurité : ne pas supprimer si des filières y sont liées
    if dept.filieres.exists():
        messages.error(request, "Impossible de supprimer : ce département contient des filières.")
    else:
        dept.delete()
        messages.warning(request, "Département supprimé.")
    return redirect('administration:liste_departements')

def modifier_departement(request, pk):
    dept = get_object_or_404(Departement, pk=pk)
    if request.method == 'POST':
        nouveau_nom = request.POST.get('nom').strip()
        
        # On vérifie si le nom existe déjà sur UN AUTRE département
        if Departement.objects.filter(nom__iexact=nouveau_nom).exclude(pk=pk).exists():
            messages.error(request, f"Le département '{nouveau_nom}' existe déjà.")
        else:
            dept.nom = nouveau_nom
            dept.save()
            messages.success(request, "Département mis à jour avec succès.")
            
    return redirect('administration:liste_departements')

#filieres 


def liste_filieres(request):
    filieres = Filiere.objects.all().select_related('departement').order_by('nom')
    departements = Departement.objects.all().order_by('nom')
    
    if request.method == 'POST':
        nom = request.POST.get('nom').strip()
        code = request.POST.get('code').strip().upper()
        dept_id = request.POST.get('departement')
        
        # Verification de l'unicite (Nom ou Code)
        if Filiere.objects.filter(nom__iexact=nom).exists() or Filiere.objects.filter(code__iexact=code).exists():
            messages.error(request, "Une filiere avec ce nom ou ce code existe deja.")
        else:
            dept = get_object_or_404(Departement, id=dept_id)
            Filiere.objects.create(nom=nom, code=code, departement=dept)
            messages.success(request, f"Filiere {code} creee avec succes.")
        
        return redirect('administration:liste_filieres')

    context = {
        'filieres': filieres,
        'departements': departements
    }
    return render(request, 'administration/liste_filieres.html', context)

def supprimer_filiere(request, pk):
    filiere = get_object_or_404(Filiere, pk=pk)
    if filiere.classes.exists():
        messages.error(request, "Impossible de supprimer : des classes sont liees a cette filiere.")
    else:
        filiere.delete()
        messages.warning(request, "Filiere supprimee.")
    return redirect('administration:liste_filieres')

def modifier_filiere(request, pk):
    filiere = get_object_or_404(Filiere, pk=pk)
    if request.method == 'POST':
        nouveau_nom = request.POST.get('nom').strip()
        nouveau_code = request.POST.get('code').strip().upper()
        nouveau_dept_id = request.POST.get('departement')
        
        # Vérification d'unicité (exclure la filière actuelle de la recherche)
        if Filiere.objects.filter(nom__iexact=nouveau_nom).exclude(pk=pk).exists() or \
           Filiere.objects.filter(code__iexact=nouveau_code).exclude(pk=pk).exists():
            messages.error(request, "Une autre filière possède déjà ce nom ou ce code.")
        else:
            nouveau_dept = get_object_or_404(Departement, id=nouveau_dept_id)
            filiere.nom = nouveau_nom
            filiere.code = nouveau_code
            filiere.departement = nouveau_dept
            filiere.save()
            messages.success(request, f"La filière {filiere.code} a été mise à jour.")
            
    return redirect('administration:liste_filieres')



def liste_classes(request):
    classes = Classe.objects.all().select_related('filiere').order_by('code')
    filieres = Filiere.objects.all().order_by('nom')
    
    if request.method == 'POST':
        nom = request.POST.get('nom').strip()
        code = request.POST.get('code').strip().upper()
        filiere_id = request.POST.get('filiere')
        
        if Classe.objects.filter(code__iexact=code).exists():
            messages.error(request, f"La classe avec le code {code} existe déjà.")
        else:
            filiere = get_object_or_404(Filiere, id=filiere_id)
            Classe.objects.create(nom=nom, code=code, filiere=filiere)
            messages.success(request, f"Classe {code} créée.")
        return redirect('administration:liste_classes')

    return render(request, 'administration/liste_classes.html', {'classes': classes, 'filieres': filieres})

def modifier_classe(request, pk):
    classe = get_object_or_404(Classe, pk=pk)
    if request.method == 'POST':
        classe.nom = request.POST.get('nom').strip()
        classe.code = request.POST.get('code').strip().upper()
        classe.filiere = get_object_or_404(Filiere, id=request.POST.get('filiere'))
        classe.save()
        messages.success(request, "Classe mise à jour.")
    return redirect('administration:liste_classes')
#vague
@login_required
def liste_vagues(request):
    maintenant = timezone.now()
    
    # --- LOGIQUE DE CLÔTURE AUTOMATIQUE ---
    # On clôture automatiquement les vagues dont la date est passée mais qui ne sont pas encore marquées 'est_cloturee'
    vagues_expirees = Vague.objects.filter(
        date_fermeture__lte=maintenant, 
        est_cloturee=False
    )
    if vagues_expirees.exists():
        vagues_expirees.update(est_cloturee=True)

    vagues = Vague.objects.all().prefetch_related('annees_concernees').order_by('-date_ouverture')
    toutes_les_annees = AnneeScolaire.objects.all().order_by('-libelle')

    # Vérification d'une vague active (non clôturée et dans la période)
    vague_en_cours = Vague.objects.filter(
        date_ouverture__lte=maintenant,
        date_fermeture__gt=maintenant,
        est_cloturee=False
    ).first()

    if request.method == 'POST':
        libelle = request.POST.get('libelle')
        ouverture = request.POST.get('date_ouverture')
        fermeture = request.POST.get('date_fermeture')
        annees_ids = request.POST.getlist('annees_concernees')

        # Validations
        if fermeture <= ouverture:
            messages.error(request, "Erreur : La date de fermeture doit être après l'ouverture.")
            return redirect('administration:liste_vagues')

        if vague_en_cours:
            messages.error(request, f"Impossible : La '{vague_en_cours.libelle}' est encore active.")
            return redirect('administration:liste_vagues')
            
        if not annees_ids:
            messages.error(request, "Erreur : Sélectionnez au moins une année scolaire.")
            return redirect('administration:liste_vagues')

        nouvelle_vague = Vague.objects.create(
            libelle=libelle, 
            date_ouverture=ouverture, 
            date_fermeture=fermeture
        )
        nouvelle_vague.annees_concernees.set(annees_ids)
        messages.success(request, f"La {libelle} a été lancée avec succès.")
        return redirect('administration:liste_vagues')

    return render(request, 'administration/liste_vagues.html', {
        'vagues': vagues, 
        'toutes_les_annees': toutes_les_annees,
        'vague_en_cours': vague_en_cours,
        'maintenant': maintenant
    })
@login_required
def cloturer_vague(request, pk):
    vague = get_object_or_404(Vague, pk=pk)
    if request.method == 'POST':
        vague.est_cloturee = True
        vague.save()
        messages.warning(request, f"La session '{vague.libelle}' a été clôturée manuellement.")
    return redirect('administration:liste_vagues')

def modifier_vague(request, pk):
    vague = get_object_or_404(Vague, pk=pk)
    maintenant = timezone.now()
    
    if request.method == 'POST':
        libelle = request.POST.get('libelle')
        ouverture = request.POST.get('date_ouverture')
        fermeture = request.POST.get('date_fermeture')
        annees_ids = request.POST.getlist('annees_concernees')
        
        # 1. VALIDATION DES DATES
        if fermeture <= ouverture:
            messages.error(request, "Erreur : La fermeture doit être après l'ouverture.")
            return redirect('administration:liste_vagues')

        # 2. VÉRIFICATION DU CHEVAUCHEMENT (VAGUE UNIQUE)
        # On cherche s'il existe UNE AUTRE vague (exclude pk) qui est en cours
        vague_conflit = Vague.objects.filter(
            date_fermeture__gt=maintenant,
            est_cloturee=False
        ).exclude(pk=vague.pk).first()

        # Si l'utilisateur essaie de rendre cette vague "active" alors qu'une autre l'est déjà
        if vague_conflit and fermeture > maintenant.strftime('%Y-%m-%dT%H:%M'):
            messages.error(request, f"Impossible : La '{vague_conflit.libelle}' est déjà en cours d'utilisation.")
            return redirect('administration:liste_vagues')
        
        # 3. MISE À JOUR
        vague.libelle = libelle
        vague.date_ouverture = ouverture
        vague.date_fermeture = fermeture
        vague.save()
        
        if annees_ids:
            vague.annees_concernees.set(annees_ids)
        else:
            messages.error(request, "Erreur : Une vague doit concerner au moins une année.")
            return redirect('administration:liste_vagues')
        
        messages.success(request, f"La {vague.libelle} a été mise à jour.")
        return redirect('administration:liste_vagues') 

    return redirect('administration:liste_vagues')

#users
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from app_administration.models import Departement

User = get_user_model()
# app_administration/views.py
def liste_chefs(request):
    chefs = User.objects.filter(role='CHEF_DEPT').order_by('-date_joined')
    departements = Departement.objects.all()

    if request.method == 'POST':
        # --- ACTION : CRÉATION ---
        if 'creer_chef' in request.POST:
            password = request.POST.get('password')
            if len(password) < 8:
                messages.error(request, "Échec : Le mot de passe doit faire au moins 8 caractères.")
                return redirect('administration:liste_chefs')
            
            user = User.objects.create_user(
                username=request.POST.get('username'),
                email=request.POST.get('email'),
                password=password,
                role='CHEF_DEPT',
                departement_id=request.POST.get('departement')
            )
            messages.success(request, f"Compte de {user.username} créé.")

        # --- ACTION : MODIFIER INFOS (Login, Email, Dept) ---
        elif 'modifier_infos' in request.POST:
            u = get_object_or_404(User, id=request.POST.get('user_id'))
            u.username = request.POST.get('username')
            u.email = request.POST.get('email')
            u.departement_id = request.POST.get('departement')
            u.save()
            messages.success(request, "Informations mises à jour.")

        # --- ACTION : MODIFIER PASSWORD ---
        elif 'modifier_password' in request.POST:
            u = get_object_or_404(User, id=request.POST.get('user_id'))
            nouveau_pass = request.POST.get('nouveau_password')
            if len(nouveau_pass) < 8:
                messages.error(request, "Le nouveau mot de passe est trop court.")
            else:
                u.set_password(nouveau_pass)
                u.save()
                messages.success(request, "Mot de passe modifié.")

        return redirect('administration:liste_chefs')

    return render(request, 'administration/liste_chefs.html', {'chefs': chefs, 'departements': departements})

def supprimer_chef(request, pk):
    chef = get_object_or_404(User, pk=pk)
    nom = chef.username
    chef.delete()
    messages.success(request, f"Le compte de {nom} a été supprimé.")
    return redirect('administration:liste_chefs')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.utils import timezone

@login_required
def accueil_chef(request):
    # On s'assure de récupérer le département de l'utilisateur connecté
    chef_dept = request.user.departement
    maintenant = timezone.now()

    # 1. Base des dossiers liés au département du chef
    dossiers_dept = DossierMemoire.objects.filter(
        etudiant__classe__filiere__departement=chef_dept
    )

    # 2. Identifier la vague actuellement active
    vague_active = Vague.objects.filter(
        date_ouverture__lte=maintenant,
        date_fermeture__gte=maintenant,
        est_cloturee=False
    ).first()

    # 3. COMPTEURS DE TRAVAIL (LOGIQUE Q CORRIGÉE)
    # Jurys à proposer : Dossiers qui n'ont pas de soutenance OU dont la soutenance est rejetée
    attente_proposition = dossiers_dept.filter(
        Q(soutenance__isnull=True) | Q(soutenance__status='REJETE')
    ).count()

    # Programmations à faire : Soutenances validées par le DE mais pas encore programmées
    attente_programmation = dossiers_dept.filter(
        soutenance__status='VALIDE'
    ).count()

    # 4. Construction du contexte
    context = {
        'dossiers_count': dossiers_dept.count(),
        'dossiers_hors_vague': dossiers_dept.filter(vague__isnull=True).count(),
        'total_etudiants_dept': Etudiant.objects.filter(
            classe__filiere__departement=chef_dept
        ).count(),
        'vague_active': vague_active,
        'attente_proposition': attente_proposition,
        'attente_programmation': attente_programmation,
        'derniers_etudiants': dossiers_dept.order_by('-id')[:5],
    }

    return render(request, 'administration/chef/accueil.html', context)
from django.utils import timezone
from .models import AnneeScolaire
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import FieldError
from django.http import JsonResponse

from .models import Filiere, Classe, Vague, AnneeScolaire
from app_gestion_interne.models import Etudiant, DossierMemoire

@login_required
def liste_themes_etudiants(request):
    dept = request.user.departement
    
    # 1. Filtres
    f_id = request.GET.get('filiere')
    c_id = request.GET.get('classe')
    a_id = request.GET.get('annee')
    search = request.GET.get('search')

    # 2. Querybase : Dossiers du département
    dossiers = DossierMemoire.objects.filter(
        etudiant__classe__filiere__departement=dept
    ).select_related('etudiant', 'etudiant__classe', 'etudiant__annee')

    # Application des filtres
    if f_id: dossiers = dossiers.filter(etudiant__classe__filiere_id=f_id)
    if c_id: dossiers = dossiers.filter(etudiant__classe_id=c_id)
    if a_id: dossiers = dossiers.filter(etudiant__annee_id=a_id)
    if search:
        dossiers = dossiers.filter(
            Q(etudiant__nom__icontains=search) | Q(etudiant__prenom__icontains=search)
        )

    # 3. Données pour le Modal d'ajout (Ajax facilitera le choix dynamique)
    context = {
        'dossiers': dossiers,
        'filieres': Filiere.objects.filter(departement=dept),
        'annees_scolaires': AnneeScolaire.objects.all().order_by('-libelle'), # Changé ici        'classes': Classe.objects.filter(filiere_id=f_id) if f_id else [],
    }
    return render(request, 'administration/chef/themes_liste.html', context)
from django.http import JsonResponse

def get_classes_by_filiere(request, filiere_id):
    """Retourne les classes d'une filière donnée"""
    classes = Classe.objects.filter(filiere_id=filiere_id).values('id', 'nom')
    return JsonResponse(list(classes), safe=False)

def get_etudiants_par_classe_et_annee(request, classe_id):
    """Retourne les étudiants d'une classe qui n'ont PAS encore de dossier cette année"""
    # On récupère l'année en cours ou on laisse le filtrage global
    etudiants = Etudiant.objects.filter(classe_id=classe_id).values('matricule', 'nom', 'prenom')
    return JsonResponse(list(etudiants), safe=False)

@login_required
def enregistrer_theme_etudiant(request):
    if request.method == 'POST':
        dossier_id = request.POST.get('dossier_id')
        matricule = request.POST.get('etudiant_matricule')
        theme = request.POST.get('theme')
        encadreur = request.POST.get('encadreur')
        lieu = request.POST.get('lieu_stage')

        # 1. Récupération de l'étudiant
        etudiant = get_object_or_404(Etudiant, matricule=matricule)
        annee_scolaire = etudiant.annee 

        if dossier_id:
            # --- CAS : MODIFICATION ---
            dossier = get_object_or_404(DossierMemoire, id=dossier_id)
            dossier.theme = theme
            dossier.encadreur = encadreur
            dossier.lieu_stage = lieu
            # AUTOMATISATION : On valide le thème au moment de la modif
            dossier.is_theme_valide = True 
            dossier.save()
            messages.success(request, f"Le thème de {etudiant.nom} a été mis à jour et validé.")
        else:
            # --- CAS : CRÉATION AVEC SÉCURITÉ DOUBLON ---
            doublon = DossierMemoire.objects.filter(
                etudiant=etudiant, 
                etudiant__annee=annee_scolaire
            ).exists()

            if doublon:
                messages.error(
                    request, 
                    f"Impossible : l'étudiant {etudiant.nom} {etudiant.prenom} "
                    f"possède déjà un thème pour l'année {annee_scolaire.libelle}."
                )
            else:
                # AUTOMATISATION : Création avec validation automatique
                DossierMemoire.objects.create(
                    etudiant=etudiant,
                    theme=theme,
                    encadreur=encadreur,
                    lieu_stage=lieu,
                    is_theme_valide=True # Le champ passe à True directement
                )
                messages.success(request, f"Thème enregistré et validé avec succès pour {etudiant.nom}.")

    return redirect('administration:liste_themes_etudiants')
@login_required
def get_etudiants_par_classe_et_annee(request, classe_id, annee_id):
    # Cette fonction renvoie les étudiants filtrés par les deux critères
    etudiants = Etudiant.objects.filter(classe_id=classe_id, annee_id=annee_id)
    data = list(etudiants.values('matricule', 'nom', 'prenom'))
    return JsonResponse(data, safe=False)
@login_required
def get_classes(request, filiere_id):
    classes = Classe.objects.filter(filiere_id=filiere_id).values('id', 'nom')
    return JsonResponse(list(classes), safe=False)
@login_required
def supprimer_dossier_chef(request, pk):
    dossier = get_object_or_404(DossierMemoire, pk=pk)
    nom_etudiant = f"{dossier.etudiant.nom} {dossier.etudiant.prenom}"
    dossier.delete()
    messages.success(request, f"Le dossier de {nom_etudiant} a été supprimé avec succès.")
    return redirect('administration:liste_themes_etudiants')

@login_required
def inscrire_vague_unitaire(request, pk):
    """Permet au Chef d'inscrire un étudiant à la vague actuellement ouverte"""
    dossier = get_object_or_404(DossierMemoire, pk=pk)
    maintenant = timezone.now()
    
    # On cherche une vague dont les dates correspondent à aujourd'hui et non clôturée
    vague_ouverte = Vague.objects.filter(
        date_ouverture__lte=maintenant,
        date_fermeture__gte=maintenant,
        est_cloturee=False
    ).first()
    
    if vague_ouverte:
        dossier.vague = vague_ouverte
        dossier.save()
        messages.success(request, f"L'étudiant {dossier.etudiant.nom} a été inscrit avec succès à la {vague_ouverte.libelle}.")
    else:
        messages.error(request, "Action impossible : Aucune vague de soutenance n'est actuellement ouverte par la Direction.")
        
    return redirect('administration:liste_themes_etudiants')

@login_required
def chef_liste_vagues(request):
    """
    Liste toutes les vagues pour le Chef de département, 
    triées par date de création pour permettre le regroupement par année.
    """
    # On trie par date de création décroissante (plus récent d'abord)
    vagues = Vague.objects.all().order_by('-date_creation')
    
    context = {
        'vagues': vagues,
    }
    return render(request, 'administration/chef/vagues_liste.html', context)
@login_required
def chef_detail_vague(request, pk):
    """
    Détail et inscription avec sécurité : 
    1. Isolation par Département
    2. Filtrage par Années Concernées (vague)
    3. Exclusion des doubles inscriptions (même année civile)
    4. CONDITION PRÉ-DÉPÔT : Seuls les dossiers avec pré-dépôt validé sont affichés
    """
    vague = get_object_or_404(Vague, pk=pk)
    chef_dept = request.user.departement
    maintenant = timezone.now()

    # 1. Gestion de la clôture spécifique
    cloture_dept, _ = ClotureVagueDepartement.objects.get_or_create(
        vague=vague, 
        departement=chef_dept
    )

    peut_modifier = vague.est_active_generale and not cloture_dept.is_cloturee
    peut_reouvrir = (vague.date_ouverture <= maintenant <= vague.date_fermeture) and \
                    cloture_dept.is_cloturee and not vague.est_cloturee

    # 2. Récupération des IDs des années autorisées pour CETTE vague
    annees_valides_ids = vague.annees_concernees.values_list('id', flat=True)

    # 3. Filtrage de base : Département + Année autorisée + PRÉ-DÉPÔT OBLIGATOIRE
    dossiers_base = DossierMemoire.objects.filter(
        etudiant__classe__filiere__departement=chef_dept,
        etudiant__annee_id__in=annees_valides_ids,
        is_pre_depot_fait=True # <--- AJOUT SÉCURITÉ : pré-dépôt doit être fait
    )

    if peut_modifier:
        # Sécurité : Exclure les étudiants déjà validés ailleurs cette année
        annee_creation_vague = vague.date_creation.year
        etudiants_deja_inscrits_ailleurs = DossierMemoire.objects.filter(
            vague__date_creation__year=annee_creation_vague
        ).exclude(vague=vague).values_list('etudiant_id', flat=True)

        dossiers = dossiers_base.filter(
            Q(vague=vague) | Q(vague__isnull=True)
        ).exclude(etudiant_id__in=etudiants_deja_inscrits_ailleurs)
    else:
        # Session close : on ne voit que les inscrits réels de cette vague
        dossiers = dossiers_base.filter(vague=vague)

    # 4. Application des Filtres GET (Recherche, Filière, Classe, Année Scolaire)
    f_id = request.GET.get('filiere')
    c_id = request.GET.get('classe')
    a_id = request.GET.get('annee') # Filtrage par année scolaire sélectionnée
    search = request.GET.get('search')

    if f_id:
        dossiers = dossiers.filter(etudiant__classe__filiere_id=f_id)
    if c_id:
        dossiers = dossiers.filter(etudiant__classe_id=c_id)
    if a_id:
        dossiers = dossiers.filter(etudiant__annee_id=a_id)
    if search:
        dossiers = dossiers.filter(
            Q(etudiant__nom__icontains=search) | 
            Q(etudiant__prenom__icontains=search) |
            Q(etudiant__matricule__icontains=search)
        )

    context = {
        'vague': vague,
        # On s'assure de récupérer l'année scolaire pour le template
        'dossiers': dossiers.select_related('etudiant', 'etudiant__classe', 'etudiant__annee', 'etudiant__classe__filiere').order_by('etudiant__nom'),
        'peut_modifier': peut_modifier,
        'peut_reouvrir': peut_reouvrir,
        'filieres': Filiere.objects.filter(departement=chef_dept),
        'classes_du_dept': Classe.objects.filter(filiere__departement=chef_dept),
        'annees_scolaires': vague.annees_concernees.all(),
    }
    return render(request, 'administration/chef/vague_detail.html', context)

@login_required
def chef_cloturer_vague(request, pk):
    """Permet au chef de fermer manuellement l'accès à cette vague"""
    vague = get_object_or_404(Vague, pk=pk)
    vague.est_cloturee = True
    vague.save()
    messages.success(request, f"La session {vague.libelle} est désormais clôturée.")
    return redirect('administration:chef_liste_vagues')


@login_required
def chef_inscrire_vague(request, pk_dossier, pk_vague):
    vague = get_object_or_404(Vague, pk=pk_vague)
    dossier = get_object_or_404(DossierMemoire, pk=pk_dossier)
    chef_dept = request.user.departement

    # 1. Vérifier la clôture spécifique du département
    cloture_dept, _ = ClotureVagueDepartement.objects.get_or_create(
        vague=vague, 
        departement=chef_dept
    )

    # 2. Utiliser VOTRE propriété 'est_active_generale' 
    # ET vérifier que le chef n'a pas clôturé son département
    if vague.est_active_generale and not cloture_dept.is_cloturee:
        dossier.vague = vague
        dossier.save()
        messages.success(request, f"{dossier.etudiant.nom} a été inscrit à la vague.")
    else:
        if cloture_dept.is_cloturee:
            messages.error(request, "Action impossible : Vous avez déjà clôturé la session pour votre département.")
        else:
            messages.error(request, "Impossible : cette vague est clôturée par la direction ou le délai est dépassé.")

    return redirect('administration:chef_detail_vague', pk=pk_vague)

@login_required
def chef_annuler_inscription(request, pk_dossier, pk_vague):
    vague = get_object_or_404(Vague, pk=pk_vague)
    dossier = get_object_or_404(DossierMemoire, pk=pk_dossier)
    chef_dept = request.user.departement

    cloture_dept, _ = ClotureVagueDepartement.objects.get_or_create(vague=vague, departement=chef_dept)

    # On ne peut annuler que si la session est encore ouverte
    if vague.est_active_generale and not cloture_dept.is_cloturee:
        dossier.vague = None
        dossier.save()
        messages.info(request, f"L'inscription de {dossier.etudiant.nom} a été annulée.")
    else:
        messages.error(request, "Modification impossible sur une session close.")

    return redirect('administration:chef_detail_vague', pk=pk_vague)
import openpyxl
from django.http import HttpResponse
from openpyxl.styles import Font, Alignment, PatternFill
@login_required
def chef_toggle_cloture(request, pk):
    vague = get_object_or_404(Vague, pk=pk)
    chef_dept = request.user.departement

    # Empêcher toute modification si la date limite générale est passée
    if timezone.now() > vague.date_fermeture:
        messages.error(request, "Le délai de cette vague est expiré. Impossible de modifier l'état.")
        return redirect('administration:chef_detail_vague', pk=vague.id)

    cloture_dept, _ = ClotureVagueDepartement.objects.get_or_create(
        vague=vague, 
        departement=chef_dept
    )
    
    # On inverse l'état (True devient False et vice-versa)
    cloture_dept.is_cloturee = not cloture_dept.is_cloturee
    cloture_dept.save()

    status = "clôturée" if cloture_dept.is_cloturee else "réouverte"
    messages.success(request, f"La session a été {status} avec succès pour votre département.")
    
    return redirect('administration:chef_detail_vague', pk=vague.id)
import openpyxl
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from openpyxl.styles import Font, Alignment, PatternFill


from django.db.models import Q


@login_required
def exporter_rapport_complet(request):
    type_donnees = request.GET.get('type')  # 'planning' ou 'themes'
    format_type = request.GET.get('format', 'excel')
    filiere_id = request.GET.get('filiere')
    classe_id = request.GET.get('classe')
    annee_id = request.GET.get('annee')
    vague_id = request.GET.get('vague')

    # --- BASE DE RECHERCHE ---
    query = DossierMemoire.objects.all()

    # --- LOGIQUE FILTRAGE ---
    if type_donnees == 'themes':
        # Filtrage pour l'archivage administratif
        if annee_id:
            query = query.filter(vague__annees_concernees__id=annee_id)
        if filiere_id:
            query = query.filter(etudiant__classe__filiere_id=filiere_id)
        if classe_id:
            query = query.filter(etudiant__classe_id=classe_id)
        
        filename = "Liste_des_Themes"
        headers = ['MATRICULE', 'ÉTUDIANT', 'CLASSE', 'THÈME COMPLET', 'ENCADREUR']
    else:
        # Filtrage pour le planning public (Cour)
        if vague_id:
            query = query.filter(vague_id=vague_id)
        
        # Sécurité : Uniquement ce qui est réellement prêt (PROGRAMME)
        query = query.filter(soutenance__status='PROGRAMME')
        
        if filiere_id:
            query = query.filter(etudiant__classe__filiere_id=filiere_id)
            
        # Tri chronologique pour le planning
        query = query.order_by('soutenance__date', 'soutenance__heure', 'soutenance__salle')
        
        filename = "Planning_Soutenances"
        # JURY MASQUÉ pour les étudiants
        headers = ['DATE', 'HEURE', 'SALLE', 'ÉTUDIANT', 'CLASSE', 'THÈME COMPLET']

    dossiers = query.select_related('etudiant', 'etudiant__classe', 'soutenance').distinct()

    # --- OPTION A : GÉNÉRATION EXCEL ---
    if format_type == 'excel':
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Rapport"

        ws.append(headers)
        header_fill = PatternFill(start_color="003366", end_color="003366", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")

        for d in dossiers:
            if type_donnees == 'planning':
                s = d.soutenance
                ws.append([s.date.strftime('%d/%m/%Y'), s.heure.strftime('%H:%M'), s.salle, f"{d.etudiant.nom} {d.etudiant.prenom}", d.etudiant.classe.nom, d.theme])
            else:
                ws.append([d.etudiant.matricule, f"{d.etudiant.nom} {d.etudiant.prenom}", d.etudiant.classe.nom, d.theme, d.encadreur])

        # Ajustements colonnes
        ws.column_dimensions['B'].width = 30
        theme_col = 'F' if type_donnees == 'planning' else 'D'
        ws.column_dimensions[theme_col].width = 80 

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
        wb.save(response)
        return response

    # --- OPTION B : GÉNÉRATION WORD (OFFICIEL) ---
    else:
        doc = Document()
        
        # En-tête République
        section = doc.sections[0]
        header_table = doc.add_table(rows=1, cols=2)
        header_table.width = Inches(6.5)
        
        left_cell = header_table.rows[0].cells[0].paragraphs[0]
        left_cell.add_run("RÉPUBLIQUE DU NIGER\n").bold = True
        left_cell.add_run("Fraternité - Travail - Progrès\n-----------\nESCEP-NIGER").bold = True
        
        right_cell = header_table.rows[0].cells[1].paragraphs[0]
        right_cell.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        right_cell.add_run(f"Niamey, le {timezone.now().strftime('%d/%m/%Y')}")

        doc.add_paragraph("\n")
        
        titre_doc = "PLANNING DES SOUTENANCES" if type_donnees == 'planning' else "LISTE DES THÈMES"
        h = doc.add_heading(titre_doc, level=1)
        h.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph("\n")

        # Création du tableau Word
        table = doc.add_table(rows=1, cols=len(headers))
        table.style = 'Table Grid'
        
        # Remplissage En-têtes
        hdr_cells = table.rows[0].cells
        for i, text in enumerate(headers):
            hdr_cells[i].text = text
            hdr_cells[i].paragraphs[0].runs[0].bold = True

        # Remplissage Données
        for d in dossiers:
            row = table.add_row().cells
            if type_donnees == 'planning':
                s = d.soutenance
                row[0].text = s.date.strftime('%d/%m/%y')
                row[1].text = s.heure.strftime('%H:%M')
                row[2].text = s.salle or ""
                row[3].text = f"{d.etudiant.nom} {d.etudiant.prenom}"
                row[4].text = d.etudiant.classe.nom
                row[5].text = d.theme or ""
            else:
                row[0].text = d.etudiant.matricule
                row[1].text = f"{d.etudiant.nom} {d.etudiant.prenom}"
                row[2].text = d.etudiant.classe.nom
                row[3].text = d.theme or ""
                row[4].text = d.encadreur or ""

        doc.add_paragraph("\n\nLe Chef de Département")
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename="{filename}.docx"'
        doc.save(response)
        return response
    
@login_required
def page_rapport_chef(request):
    """
    Affiche la page de sélection des rapports pour le Chef de Département.
    """
    # On récupère le département du chef connecté
    dept = request.user.departement
    
    context = {
        # On ne propose que les filières de son département
        'filieres': Filiere.objects.filter(departement=dept),
        # On liste toutes les vagues pour le filtrage
        'vagues': Vague.objects.all().order_by('-id'),
    }
    
    return render(request, 'administration/chef/rapports.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from app_gestion_interne.models import Jury

@login_required
def liste_jurys_chef(request):
    """Affiche la liste des jurys filtrée par le département du chef connecté."""
    chef_dept = request.user.departement
    
    # 1. Récupération des filtres
    search = request.GET.get('search')
    statut = request.GET.get('statut')
    specialite = request.GET.get('specialite')

    # 2. Query de base (Isolation : uniquement les jurys de son département)
    jurys = Jury.objects.filter(departement=chef_dept).order_by('nom')

    # 3. Application des filtres
    if search:
        jurys = jurys.filter(
            Q(nom__icontains=search) | 
            Q(prenom__icontains=search)
        )
    if statut:
        jurys = jurys.filter(statut=statut)
    if specialite:
        jurys = jurys.filter(specialite__icontains=specialite)

    context = {
        'jurys': jurys,
        'search': search,
        'statut_select': statut,
        'specialite_search': specialite,
    }
    return render(request, 'administration/chef/liste_jurys.html', context)

@login_required
def enregistrer_jury_chef(request):
    """Gère la création et la modification avec fusion intelligente des spécialités."""
    if request.method == 'POST':
        chef_dept = request.user.departement
        jury_id = request.POST.get('jury_id')
        
        # Nettoyage des données
        nom = request.POST.get('nom').upper().strip()
        prenom = request.POST.get('prenom').strip()
        nouvelle_spec = request.POST.get('specialite').strip()
        statut = request.POST.get('statut')
        telephone = request.POST.get('telephone').strip()

        # --- CAS MODIFICATION ---
        if jury_id:
            jury = get_object_or_404(Jury, id=jury_id, departement=chef_dept)
            jury.nom = nom
            jury.prenom = prenom
            jury.specialite = nouvelle_spec
            jury.statut = statut
            jury.telephone = telephone
            jury.save()
            messages.success(request, f"Le profil de {prenom} {nom} a été mis à jour.")
        
        # --- CAS NOUVEL AJOUT (Avec vérification de doublon) ---
        else:
            # On cherche si cette personne existe déjà dans CE département
            jury_existant = Jury.objects.filter(
                departement=chef_dept,
                nom__iexact=nom,
                prenom__iexact=prenom
            ).first()

            if jury_existant:
                # Règle de fusion : si la spécialité est nouvelle, on l'ajoute à la liste
                specs_actuelles = [s.strip().lower() for s in jury_existant.specialite.split(',')]
                if nouvelle_spec.lower() not in specs_actuelles:
                    jury_existant.specialite += f", {nouvelle_spec}"
                    jury_existant.save()
                    messages.info(request, f"Spécialité ajoutée au profil existant de {prenom} {nom}.")
                else:
                    messages.warning(request, f"{prenom} {nom} est déjà enregistré avec cette spécialité.")
            else:
                # Création totale
                Jury.objects.create(
                    departement=chef_dept,
                    nom=nom,
                    prenom=prenom,
                    specialite=nouvelle_spec,
                    statut=statut,
                    telephone=telephone
                )
                messages.success(request, "Nouveau membre du jury ajouté avec succès.")
            
    return redirect('administration:liste_jurys_chef')

@login_required
def supprimer_jury_chef(request, pk):
    """Supprime un jury en s'assurant qu'il appartient bien au département du chef."""
    jury = get_object_or_404(Jury, pk=pk, departement=request.user.departement)
    nom_complet = f"{jury.prenom} {jury.nom}"
    jury.delete()
    messages.success(request, f"Le membre {nom_complet} a été supprimé de vos listes.")
    return redirect('administration:liste_jurys_chef')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app_gestion_interne.models import DossierMemoire, Soutenance, Jury
from app_administration.models import Filiere, Vague

# --- ESPACE CHEF DE DEPARTEMENT ---

@login_required
def planning_liste_vagues(request):
    """Affiche les vagues groupées par année pour choisir laquelle planifier"""
    vagues = Vague.objects.all().order_by('-date_creation')
    return render(request, 'administration/chef/planning_vagues_liste.html', {'vagues': vagues})
from django.utils import timezone
from datetime import datetime

@login_required
def planning_vague_detail(request, pk):
    vague = get_object_or_404(Vague, pk=pk)
    chef_dept = request.user.departement
    maintenant = timezone.now()
    
    dossiers = DossierMemoire.objects.filter(
        vague=vague,
        etudiant__classe__filiere__departement=chef_dept
    ).select_related('etudiant', 'etudiant__classe')

    # --- AUTOMATISATION : Mise à jour par l'heure ---
    for d in dossiers:
        # On utilise hasattr pour vérifier l'existence de la relation OneToOne sans crasher
        if hasattr(d, 'soutenance'):
            s = d.soutenance
            if s.status == 'PROGRAMME' and not d.is_soutenu:
                if s.date and s.heure:
                    # Conversion sécurisée pour la comparaison
                    dt_soutenance = timezone.make_aware(
                        datetime.combine(s.date, s.heure)
                    )
                    if maintenant >= dt_soutenance:
                        d.is_soutenu = True
                        d.save()

    # Filtres additionnels (inchangés)
    f_id = request.GET.get('filiere')
    c_id = request.GET.get('classe')
    if f_id: dossiers = dossiers.filter(etudiant__classe__filiere_id=f_id)
    if c_id: dossiers = dossiers.filter(etudiant__classe_id=c_id)

    context = {
        'vague': vague,
        'dossiers': dossiers,
        'filieres': Filiere.objects.filter(departement=chef_dept),
        'classes': Classe.objects.filter(filiere__departement=chef_dept),
        'jurys': Jury.objects.filter(departement=chef_dept),
    }
    return render(request, 'administration/chef/planning_vague_detail.html', context)

@login_required
def proposer_soutenance(request):
    if request.method == "POST":
        d_id = request.POST.get('dossier_id')
        dossier = get_object_or_404(DossierMemoire, id=d_id)
        
        # Vérification si la vague est encore active (selon votre propriété)
        if not dossier.vague.est_active_generale:
            messages.error(request, "Modification impossible : la vague est close.")
            return redirect('administration:planning_vague_detail', pk=dossier.vague.id)

        # Récupération des jurys
        pres = request.POST.get('president')
        rapp = request.POST.get('rapporteur')
        exam = request.POST.get('examinateur')

        # Sécurité : Au moins deux jurys différents
        membres = [m for m in [pres, rapp, exam] if m]
        if len(set(membres)) < 2:
            messages.error(request, "Sélectionnez au moins deux membres de jury différents.")
            return redirect('administration:planning_vague_detail', pk=dossier.vague.id)

        # Enregistrement de la proposition
        soutenance, _ = Soutenance.objects.get_or_create(dossier=dossier)
        soutenance.president_id = pres if pres else None
        soutenance.rapporteur_id = rapp if rapp else None
        soutenance.examinateur_id = exam if exam else None
        soutenance.status = 'PROPOSE'
        soutenance.motif_rejet = "" # Reset du motif si c'est une nouvelle proposition après rejet
        soutenance.save()
        
        messages.success(request, f"Jury proposé pour {dossier.etudiant.nom}.")
    return redirect('administration:planning_vague_detail', pk=dossier.vague.id)
@login_required
def enregistrer_planning(request):
    """
    Permet au Chef de département de fixer ou de MODIFIER 
    la date, l'heure et la salle d'une soutenance.
    """
    if request.method == "POST":
        s_id = request.POST.get('soutenance_id')
        soutenance = get_object_or_404(Soutenance, id=s_id)
        
        # Sécurité : On ne peut programmer que si c'est validé par le DE 
        # ou si c'est déjà programmé (pour modification)
        autorise = ['VALIDE', 'PROGRAMME']
        if soutenance.status not in autorise:
            messages.error(request, "Action impossible : le jury doit être validé par le DE.")
            return redirect('administration:planning_vague_detail', pk=soutenance.dossier.vague.id)

        # Récupération des données
        date_val = request.POST.get('date')
        heure_val = request.POST.get('heure')
        salle_val = request.POST.get('salle')

        if not date_val or not heure_val or not salle_val:
            messages.error(request, "Tous les champs (Date, Heure, Salle) sont obligatoires.")
            return redirect('administration:planning_vague_detail', pk=soutenance.dossier.vague.id)

        try:
            # Mise à jour des informations
            soutenance.date = date_val
            soutenance.heure = heure_val
            soutenance.salle = salle_val
            
            # Si c'était juste 'VALIDE', on passe à 'PROGRAMME'
            if soutenance.status == 'VALIDE':
                soutenance.status = 'PROGRAMME'
                msg = f"La soutenance de {soutenance.dossier.etudiant.nom} a été programmée."
            else:
                msg = f"Le planning de {soutenance.dossier.etudiant.nom} a été mis à jour."
            
            soutenance.save()
            messages.success(request, msg)
            
        except Exception as e:
            messages.error(request, f"Erreur technique : {e}")

    return redirect('administration:planning_vague_detail', pk=soutenance.dossier.vague.id)
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST


@login_required
@require_POST
def tout_cocher_soutenu(request, vague_id):
    """Marque tous les dossiers programmés de la vague comme soutenus"""
    chef_dept = request.user.departement
    DossierMemoire.objects.filter(
        vague_id=vague_id,
        etudiant__classe__filiere__departement=chef_dept,
        soutenance__status='PROGRAMME'
    ).update(is_soutenu=True)
    
    messages.success(request, "Tous les dossiers programmés ont été marqués comme soutenus.")
    return redirect('administration:planning_vague_detail', pk=vague_id)

@login_required
@require_POST
def modifier_etat_soutenu(request):
    """Gère le switch individuel en AJAX"""
    try:
        data = json.loads(request.body)
        dossier = get_object_or_404(DossierMemoire, id=data.get('dossier_id'))
        
        # Sécurité
        if dossier.etudiant.classe.filiere.departement == request.user.departement:
            dossier.is_soutenu = data.get('etat')
            dossier.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'Accès refusé'}, status=403)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
# --- ESPACE DIRECTION ---
@login_required
def validation_jury_liste(request):
    # Récupérer les paramètres de filtrage
    annee_id = request.GET.get('annee')
    filiere_id = request.GET.get('filiere')
    classe_id = request.GET.get('classe')

    # Base de la requête : uniquement les jurys proposés
    propositions = Soutenance.objects.filter(status='PROPOSE').select_related(
        'dossier__etudiant__classe__filiere__departement', 
        'dossier__vague',
        'president', 'rapporteur'
    )

    # Application des filtres
    if annee_id and annee_id.isdigit():
        propositions = propositions.filter(dossier__vague__annees_concernees__id=annee_id)
    if filiere_id:
        propositions = propositions.filter(dossier__etudiant__classe__filiere_id=filiere_id)
    if classe_id:
        propositions = propositions.filter(dossier__etudiant__classe_id=classe_id)

    context = {
        'propositions': propositions,
        'annees': AnneeScolaire.objects.all().order_by('-libelle'),        'filieres': Filiere.objects.all(),
        # On passe les classes uniquement si une filière est choisie (pour le script JS)
        'classes': Classe.objects.filter(filiere_id=filiere_id) if filiere_id else None,
    }
    return render(request, 'administration/validation_jury_liste.html', context)

@login_required
def traiter_validation_jury(request, pk):
    """Action de valider ou rejeter une proposition"""
    soutenance = get_object_or_404(Soutenance, pk=pk)
    
    if request.method == "POST":
        action = request.POST.get('action') # 'valider' ou 'rejeter'
        motif = request.POST.get('motif_rejet')

        if action == 'valider':
            soutenance.status = 'VALIDE'
            soutenance.motif_rejet = ""
            messages.success(request, f"Jury validé pour {soutenance.dossier.etudiant.nom}.")
        
        elif action == 'rejeter':
            if not motif:
                messages.error(request, "Vous devez fournir un motif pour le rejet.")
                return redirect('administration:validation_jury_liste')
            
            soutenance.status = 'REJETE'
            soutenance.motif_rejet = motif
            messages.warning(request, f"Proposition rejetée pour {soutenance.dossier.etudiant.nom}.")
        
        soutenance.save()
        
    return redirect('administration:validation_jury_liste')

