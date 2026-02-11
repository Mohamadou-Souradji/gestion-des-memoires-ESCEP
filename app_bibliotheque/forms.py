from django import forms
from .models import Livre, Categorie
import os

class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la catégorie'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Bref descriptif...'}),
        }


class LivreForm(forms.ModelForm):
    class Meta:
        model = Livre
        fields = ['titre', 'auteur', 'categorie', 'isbn', 'description', 'image_couverture', 'fichier_numerique',
                  'is_publie']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'auteur': forms.TextInput(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'fichier_numerique': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'image_couverture': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            # Ajout de la classe pour le Switch
            'is_publie': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fichier_numerique'].required = True  # PDF obligatoire

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # --- CHAMPS CRITIQUES OBLIGATOIRES ---
        self.fields['fichier_numerique'].required = True
        self.fields['categorie'].required = True
        self.fields['categorie'].empty_label = "Choisir une catégorie..."

    def clean_fichier_numerique(self):
        """Validation pour s'assurer que c'est bien un PDF"""
        fichier = self.cleaned_data.get('fichier_numerique')
        if fichier:
            extension = os.path.splitext(fichier.name)[1].lower()
            if extension != '.pdf':
                raise forms.ValidationError("Le fichier doit obligatoirement être au format PDF.")
        return fichier