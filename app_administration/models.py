from django.db import models
from django.utils import timezone


class Departement(models.Model):
    nom = models.CharField(max_length=100)
    def __str__(self): return self.nom

class Filiere(models.Model):
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE, related_name='filieres')
    def __str__(self): return f"{self.code} - {self.nom}"

class Classe(models.Model):
    nom = models.CharField(max_length=50)
    code = models.CharField(max_length=20, unique=True)
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name='classes')
    def __str__(self): return self.code

class AnneeScolaire(models.Model):
    libelle = models.CharField(max_length=20) # Ex: 2023-2024
    est_active = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Année Scolaire"
        ordering = ['-libelle']
        
    def __str__(self): return self.libelle

class Vague(models.Model):
    libelle = models.CharField(max_length=100)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_ouverture = models.DateTimeField()
    date_fermeture = models.DateTimeField()
    annees_concernees = models.ManyToManyField('AnneeScolaire', related_name='vagues')
    est_cloturee = models.BooleanField(default=False) # Clôture générale (DE)

    def __str__(self):
        return f"{self.libelle} ({self.date_creation.year})"

    @property
    def est_active_generale(self):
        now = timezone.now()
        return self.date_ouverture <= now <= self.date_fermeture and not self.est_cloturee

# NOUVEAU : Pour que chaque Chef clôture son département individuellement
class ClotureVagueDepartement(models.Model):
    vague = models.ForeignKey(Vague, on_delete=models.CASCADE)
    departement = models.ForeignKey('Departement', on_delete=models.CASCADE)
    is_cloturee = models.BooleanField(default=False)

    class Meta:
        unique_together = ('vague', 'departement')