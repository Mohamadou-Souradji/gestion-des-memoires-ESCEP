
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from app_auth.models import User # Vérifie bien le chemin vers ton modèle User custom

def create_superuser():
    username = "admin"
    email = "admin@example.com"
    password = "1234" # Change-le ici !

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f"Superuser '{username}' créé avec succès.")
    else:
        print(f"L'utilisateur '{username}' existe déjà.")

if __name__ == "__main__":
    create_superuser()
