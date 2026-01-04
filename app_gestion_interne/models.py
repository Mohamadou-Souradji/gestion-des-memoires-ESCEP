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
    vague = models.ForeignKey(Vague, on_delete=models.CASCADE)

    # --- Dev 1 : Chef de Département ---
    theme = models.CharField(max_length=255, null=True, blank=True)
    encadreur = models.CharField(max_length=100, null=True, blank=True)
    lieu_stage = models.CharField(max_length=150, null=True, blank=True)  # Optionnel
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