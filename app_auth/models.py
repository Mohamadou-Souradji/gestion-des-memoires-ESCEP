# app_auth/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('DE', 'Directeur des Etudes'),
        ('CHEF_DEPT', 'Chef de Departement'),
        ('SCOLARITE', 'Scolarite'),
        ('COMPTABLE', 'Comptable'),
        ('SURVEILLANT', 'Surveillant'),
        ('BIBLIO', 'Bibliothecaire'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    # Lien vers le département pour le Chef de Dept
    departement = models.ForeignKey(
        'app_administration.Departement', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='personnel'
    )

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"