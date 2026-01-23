import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

def create_users():
    # Liste des utilisateurs à créer (Username, Role, Password)
    users_to_create = [
        ('admin_escep', 'DE', '1234'),
        ('scolarite', 'SCOLARITE', '1234'),
        ('comptable', 'COMPTABLE', '1234'),
        ('surveillant', 'SURVEILLANT', '1234'),
        ('bibliothecaire', 'BIBLIO', '1234'),
    ]

    for username, role, password in users_to_create:
        if not User.objects.filter(username=username).exists():
            print(f"Création de l'utilisateur : {username} ({role})...")
            # Pour le premier (le DE), on en fait un superuser pour accéder à l'admin
            if role == 'DE':
                User.objects.create_superuser(
                    username=username, 
                    email=f"{username}@escep.com", 
                    password=password,
                    role=role
                )
            else:
                User.objects.create_user(
                    username=username, 
                    email=f"{username}@escep.com", 
                    password=password,
                    role=role,
                    is_staff=True # Permet de se connecter à l'interface admin si besoin
                )
            print(f"Utilisateur {username} créé.")
        else:
            print(f"L'utilisateur {username} existe déjà.")

if __name__ == "__main__":
    create_users()
