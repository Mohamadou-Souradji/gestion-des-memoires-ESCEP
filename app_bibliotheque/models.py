from django.db import models
from django.urls import reverse
from core import settings


from django.utils.text import slugify

class Categorie(models.Model):
    nom = models.CharField("Nom", max_length=100, unique=True)
    description = models.TextField("Description", blank=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True) # blank=True est important ici

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom


class Livre(models.Model):
    titre = models.CharField("Titre", max_length=255)
    auteur = models.CharField("Auteur", max_length=100)
    isbn = models.CharField("ISBN", max_length=20, unique=True, blank=True, null=True)

    # Relation avec la catégorie (un livre appartient à une catégorie)
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        related_name="livres",
        verbose_name="Catégorie"
    )

    description = models.TextField("Description", blank=True)
    fichier_numerique = models.FileField(
        "Fichier PDF (Optionnel)", upload_to="livres/fichiers/", blank=True, null=True
    )
    image_couverture = models.ImageField(
        "Image de couverture", upload_to="livres/couvertures/", blank=True, null=True
    )

    is_publie = models.BooleanField("Est publié ?", default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_creation"]
        verbose_name = "Livre"
        verbose_name_plural = "Livres"

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse("app_bibliotheque:detail_livre", args=[self.id])


class JournalOperation(models.Model):
    ACTIONS = [
        ("LIVRE_AJOUT", "Ajout de livre"),
        ("LIVRE_MODIF", "Modification de livre"),
        ("LIVRE_SUPP", "Suppression de livre"),
        ("CAT_AJOUT", "Ajout de catégorie"),  # Nouvelle action
        ("MEMOIRE_PUBLI", "Publication de mémoire"),
    ]

    action = models.CharField(max_length=30, choices=ACTIONS)
    date_action = models.DateTimeField(auto_now_add=True)
    details = models.TextField("Détails", blank=True)
    effectue_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="operations_biblio"
    )

    class Meta:
        ordering = ["-date_action"]