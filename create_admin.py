import os
import django
import random

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from app_administration.models import Classe, AnneeScolaire, Filiere, Departement
from app_gestion_interne.models import Etudiant, DossierMemoire

def populate_students():
    # --- 1. STRUCTURE ACADÉMIQUE (Basée sur tes images) ---
    # Départements
    dept_names = ["Economie Numerique", "Reseau telecom", "Reseau de Données et Securité", "Informatique"]
    depts = {name: Departement.objects.get_or_create(nom=name)[0] for name in dept_names}

    # Filières
    filieres_data = [
        {"code": "EN", "nom": "Economie Numerique", "dept": depts["Economie Numerique"]},
        {"code": "BG", "nom": "Big Data", "dept": depts["Informatique"]},
        {"code": "RDS", "nom": "Reseau de Données et Securité", "dept": depts["Reseau de Données et Securité"]},
        {"code": "GL", "nom": "Genie logiciel", "dept": depts["Informatique"]},
    ]
    f_objs = {f["code"]: Filiere.objects.get_or_create(code=f["code"], nom=f["nom"], departement=f["dept"])[0] for f in filieres_data}

    # Classes
    classes_data = [
        {"code": "L3EN", "nom": "Licence 3 Economie numerique", "f": f_objs["EN"]},
        {"code": "L3BD", "nom": "Licence 3 Big Data", "f": f_objs["BG"]},
        {"code": "M2RDS", "nom": "Master 2 Réseaux de Données et Sécurité", "f": f_objs["RDS"]},
        {"code": "M2GL", "nom": "Master 2 Genie logiciel", "f": f_objs["GL"]},
        {"code": "L3RDS", "nom": "Licence 3 Réseau de donnée et securite", "f": f_objs["RDS"]},
        {"code": "L3GL", "nom": "Licence 3 Génie logiciel", "f": f_objs["GL"]},
    ]
    c_objs = [Classe.objects.get_or_create(code=c["code"], nom=c["nom"], filiere=c["f"])[0] for c in classes_data]

    # Années Académiques
    annees_labels = ["2026-2027", "2025-2026", "2024-2025"]
    a_objs = [AnneeScolaire.objects.get_or_create(libelle=label)[0] for label in annees_labels]

    # --- 2. CRÉATION DES ÉTUDIANTS (10 par classe, Matricule 0010...) ---
    noms = ["Abdou", "Ibrahim", "Moussa", "Souleymane", "Oumarou", "Sani", "Mamane", "Issaka", "Yacouba", "Salifou"]
    prenoms = ["Mariam", "Fatouma", "Aissata", "Bachir", "Ousmane", "Nana", "Hadiza", "Hamissou", "Zalika", "Idrissa"]

    sequence = 1
    total_etudiants = 0

    print("Insertion des 10 étudiants par classe...")
    for classe in c_objs:
        for _ in range(10):
            # Formatage du matricule : 00101, 00102...
            matricule = f"0010{sequence}"
            
            etudiant, created = Etudiant.objects.get_or_create(
                matricule=matricule,
                defaults={
                    'nom': random.choice(noms),
                    'prenom': random.choice(prenoms),
                    'classe': classe,
                    'annee': random.choice(a_objs)
                }
            )
            
            if created:
                # IMPORTANT : Créer le dossier mémoire associé pour l'affichage comptable
                DossierMemoire.objects.get_or_create(etudiant=etudiant)
                total_etudiants += 1
            
            sequence += 1

    print(f"Opération terminée : {total_etudiants} étudiants ajoutés.")

if __name__ == "__main__":
    populate_students()
