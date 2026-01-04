from django.db import models

class Departement(models.Model):
    nom = models.CharField(max_length=100)
    def __str__(self): return self.nom

class Filiere(models.Model):
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True) # Ex: GL, RDS
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE, related_name='filieres')
    def __str__(self): return f"{self.code} - {self.nom}"

class Classe(models.Model):
    nom = models.CharField(max_length=50)
    code = models.CharField(max_length=20, unique=True) # Ex: L3GL, M2RDS
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name='classes')
    def __str__(self): return self.code

class AnneeScolaire(models.Model):
    libelle = models.CharField(max_length=10) # Ex: 2025-2026
    est_active = models.BooleanField(default=False)
    def __str__(self): return self.libelle

class Vague(models.Model):
    libelle = models.CharField(max_length=50) # Ex: Vague 1
    date_ouverture = models.DateTimeField()
    date_fermeture = models.DateTimeField()
    annee = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    def __str__(self): return f"{self.libelle} ({self.annee})"