# Système de Gestion des Mémoires

## Installation Rapide
1. **Cloner le projet** : `git clone [https://github.com/Mohamadou-Souradji/gestion-des-memoires-ESCEP]`
2. **Lancer l'environnement** : `docker-compose up --build`
3. **Appliquer les tables** : `docker-compose exec web python manage.py migrate`
4. **Créer un compte** : `docker-compose exec web python manage.py createsuperuser`

## Répartition des tâches
- **Souradji** : `app_administration` (DE & Chef Dept)
- **Ousseini** : `app_gestion_interne` (Scolarité & Compta)
- **Doch** : `app_depots` (Surveillant)
- **Khalid** : `app_bibliotheque` (Biblio)
