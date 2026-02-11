FROM python:3.11-slim

# Empêche Python de générer des fichiers .pyc
ENV PYTHONDONTWRITEBYTECODE 1
# Force l'affichage des logs en temps réel
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Installation des dépendances système pour Postgres
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Collecte des fichiers statiques pendant le build
RUN python manage.py collectstatic --noinput

# Commande de lancement : 
# 1. Applique les migrations
# 2. Exécute le script de création d'utilisateurs
# 3. Lance Gunicorn sur le port dynamique de Render
# ... (le reste de ton Dockerfile reste identique)

CMD python manage.py migrate --noinput && \
    python manage.py shell -c "from app_auth.models import User; \
if not User.objects.filter(username='admin').exists(): \
    User.objects.create_superuser('admin', 'admin@escep.com', 'admin', role='DE'); \
    print('Utilisateur DE créé avec succès.')" && \
    gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
