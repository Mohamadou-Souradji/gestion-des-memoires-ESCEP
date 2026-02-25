FROM python:3.11-slim

# Empêche Python de générer des fichiers .pyc et force l'affichage des logs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Installation des dépendances système (Postgres + utilitaires)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Installation des bibliothèques Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copie du projet
COPY . /app/

# On lance les migrations et on démarre le serveur
# J'ai remplacé TON_PROJET par core
CMD python manage.py collectstatic --noinput && \
    python manage.py migrate && \
    gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
