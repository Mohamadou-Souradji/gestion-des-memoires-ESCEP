from django.db import models
from app_administration.models import Classe, AnneeScolaire, Vague


class Etudiant(models.Model):
    matricule = models.CharField(max_length=20, primary_key=True)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    annee = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)

    def __str__(self): return f"{self.matricule} - {self.nom} {self.prenom}"


class DossierMemoire(models.Model):
    etudiant = models.OneToOneField(Etudiant, on_delete=models.CASCADE, related_name='dossier')
    # MODIFICATION : null=True et blank=True pour permettre l'ajout du thème AVANT la vague
    vague = models.ForeignKey(Vague, on_delete=models.SET_NULL, null=True, blank=True)
    
    # --- Dev 1 : Chef de Département (Peut être rempli dès maintenant) ---
    theme = models.CharField(max_length=255, null=True, blank=True)
    encadreur = models.CharField(max_length=100, null=True, blank=True)
    lieu_stage = models.CharField(max_length=150, null=True, blank=True) # Optionnel
    is_theme_valide = models.BooleanField(default=False)
    is_soutenu = models.BooleanField(default=False)

    # --- Dev 2 : Scolarité & Comptabilité ---
    is_semestres_valides = models.BooleanField(default=False)
    is_inscription_validee = models.BooleanField(default=False)

    # --- Dev 3 : Surveillant (Dépôts) ---
    fichier_pre_depot = models.FileField(upload_to='depots/pre/', null=True, blank=True)
    is_pre_depot_fait = models.BooleanField(default=False)
    fichier_post_depot = models.FileField(upload_to='depots/post/', null=True, blank=True)
    is_post_depot_fait = models.BooleanField(default=False)

    # --- Dev 4 : État pour la Bibliothèque ---
    is_publie = models.BooleanField(default=False)

    def __str__(self): return f"Dossier de {self.etudiant.nom}"

class Jury(models.Model):
    STATUT_CHOICES = [('TITULAIRE', 'Titulaire'), ('VACATAIRE', 'Vacataire')]
    
    # Utilisez cette syntaxe pour éviter le NameError et les imports circulaires
    departement = models.ForeignKey(
        'app_administration.Departement', 
        on_delete=models.CASCADE, 
        related_name='jurys_set', 
        null=True
    )
    
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    specialite = models.CharField(max_length=255) 
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='TITULAIRE')
    telephone = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Jurys"

    def __str__(self):
        return f"{self.nom} {self.prenom}"


from django.db import models

class Soutenance(models.Model):
    STATUS_CHOICES = [
        ('PROPOSE', 'En attente de validation'),
        ('VALIDE', 'Validé par Direction'),
        ('REJETE', 'Rejeté'),
        ('PROGRAMME', 'Programmée'),
    ]

    dossier = models.OneToOneField('DossierMemoire', on_delete=models.CASCADE, related_name='soutenance')
    
    # Membres du jury (Optionnels pour permettre la flexibilité)
    president = models.ForeignKey('Jury', on_delete=models.SET_NULL, null=True, blank=True, related_name='presidences')
    rapporteur = models.ForeignKey('Jury', on_delete=models.SET_NULL, null=True, blank=True, related_name='rapports')
    examinateur = models.ForeignKey('Jury', on_delete=models.SET_NULL, null=True, blank=True, related_name='examens')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PROPOSE')
    motif_rejet = models.TextField(null=True, blank=True)
    
    # Infos Planning (remplies par le Chef après validation)
    date = models.DateField(null=True, blank=True)
    heure = models.TimeField(null=True, blank=True)
    salle = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Soutenance de {self.dossier.etudiant.nom}"