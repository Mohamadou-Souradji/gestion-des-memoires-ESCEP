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
CMD python manage.py migrate --noinput && \
    python create_admin.py && \
    gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
