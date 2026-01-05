# Système de Gestion des Mémoires

## Installation Rapide
1. **Cloner le projet** : `git clone [https://github.com/Mohamadou-Souradji/gestion-des-memoires-ESCEP]`
2. **Lancer l'environnement** : `docker-compose up --build`
3. **Appliquer les tables** : `docker-compose exec web python manage.py migrate`
4. **Créer un compte** : `docker-compose exec web python manage.py createsuperuser`

## Répartition des tâches
- **Souradji** : `app_administration` (gere les inteface Admin et le chef de dpartement)
- **Ousseini** : `app_gestion_interne` (gere la Scolarité et le Comptabilité)donc il y a deux role (scolarite et comptable )
- **Doch** : `app_depots` (gere les interface Surveillant) pret et post
- **Khalid** : `app_bibliotheque` (Biblio) gerer la pubilication des memoires et ajouter des livres
## Contrainte:
1.Ne toucher pas au model sans demander l avis sinon tu vas pertubré le code et les autres developpeur 
2.Travailler avec le modele 
3.IL y a Autres app a geré 
## Details:
1. Souradji : Administration & Direction
Rôle : Gérer les interfaces pour le Directeur des Études (DE) et le Chef de Département.

Interface DE : Création des années scolaires, des vagues et configuration des départements/filières/classes.

Interface Chef Dept : * Filtrage automatique pour ne voir que les étudiants de son département.

Saisie et validation du Thème, de l'Encadreur et du Lieu de stage.

Marquage de la Soutenance comme effectuée (is_soutenu).

**Ousseini** : Gestion Interne (Scolarité & Compta)
Rôle : Gérer la conformité administrative des étudiants.

Interface Scolarité : Tableau de bord pour valider que l'étudiant a validé tous ses semestres (is_semestres_valides).

Interface Comptabilité : Système de "quitus" pour confirmer que les frais d'inscription et de soutenance sont payés (is_inscription_validee).

Visibilité : Accès à l'ensemble des étudiants avec filtres par classe (ex: L3GL, M2RDS).

3. **Doch** : Dépôts & Surveillance
Rôle : Gérer la partie documentaire et les fichiers PDF (Pré et Post dépôt).

Interface Surveillant :

Autoriser l'upload du Pré-dépôt seulement si le thème, la scolarité et la compta sont validés.

Vérifier le fichier PDF et valider le dépôt (is_pre_depot_fait).

Gérer l'upload de la version finale corrigée après soutenance (Post-dépôt).

4. **Khalid** : Bibliothèque & Publication
Rôle : Gérer le catalogue physique et la mise en ligne des mémoires.

Interface Bibliothécaire :

Gestion du CRUD pour les Livres physiques.

Consultation des mémoires ayant terminé le cycle (Post-dépôt OK).

Bouton de Publication (is_publie) pour rendre le mémoire accessible en lecture aux autres étudiants.
