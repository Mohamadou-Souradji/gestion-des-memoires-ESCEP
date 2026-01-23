FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installation des dépendances système pour PostgreSQL
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collecte des fichiers statiques (maintenant que STATIC_ROOT est configuré)
RUN python manage.py collectstatic --noinput

# On crée un script 'entrypoint.sh' pour lancer plusieurs commandes au démarrage
RUN echo '#!/bin/sh\n\
python manage.py migrate --noinput\n\
python create_admin.py\n\
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# On utilise le port dynamique de Render ($PORT)
CMD ["/app/entrypoint.sh"]
