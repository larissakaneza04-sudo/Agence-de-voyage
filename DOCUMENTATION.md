# Documentation du Projet - Plateforme de Réservation de Billets de Bus

## 📌 Table des Matières
1. [Introduction](#-introduction)
2. [Analyse des Besoins](#-analyse-des-besoins)
   - [Problématiques actuelles](#problématiques-actuelles)
   - [Objectifs](#objectifs)
   - [Fonctionnalités clés](#fonctionnalités-clés)
3. [Architecture Technique](#-architecture-technique)
   - [Stack Technique](#stack-technique)
   - [Structure du Projet](#structure-du-projet)
   - [Base de Données](#base-de-données)
4. [Guide d'Installation](#-guide-dinstallation)
5. [Guide d'Utilisation](#-guide-dutilisation)
6. [Sécurité](#-sécurité)
7. [Déploiement](#-déploiement)
8. [Maintenance](#-maintenance)
9. [Perspectives d'Évolution](#-perspectives-dévolution)

## 🌟 Introduction

La plateforme de réservation de billets de bus est une solution complète développée avec Django pour moderniser et digitaliser la gestion des réservations dans le secteur du transport interurbain au Burundi. Cette application permet aux utilisateurs de réserver facilement des billets, de gérer leurs réservations et de payer en ligne de manière sécurisée.

## 🔍 Analyse des Besoins

### Problématiques actuelles
- Processus de réservation manuel et chronophage
- Gestion papier des billets et des disponibilités
- Absence de système de paiement en ligne
- Difficulté de suivi des réservations
- Manque de transparence dans la gestion des places

### Objectifs
- Automatiser le processus de réservation
- Offrir une expérience utilisateur fluide et intuitive
- Sécuriser les transactions financières
- Fournir des outils de gestion aux administrateurs
- Mettre en place un système de fidélisation

### Fonctionnalités clés
- **Espace Client**
  - Inscription et authentification sécurisée
  - Gestion du profil utilisateur
  - Historique des réservations
  - Système de points de fidélité

- **Réservation**
  - Recherche de trajets par ville et date
  - Sélection de siège en temps réel
  - Paiement en ligne sécurisé
  - Gestion des annulations et remboursements

- **Espace Administrateur**
  - Gestion des trajets et des horaires
  - Suivi des réservations et des paiements
  - Gestion des utilisateurs
  - Tableaux de bord analytiques

## 🏗️ Architecture Technique

### Stack Technique
- **Backend** : Django 4.2
- **Frontend** : HTML5, CSS3, JavaScript, Bootstrap 5
- **Base de données** : PostgreSQL
- **Authentification** : Django Allauth
- **Paiement** : Stripe, Mobile Money
- **Déploiement** : Docker, Nginx, Gunicorn

### Structure du Projet
```
agence_transport/
├── agence_transport/          # Configuration du projet
├── reservations/              # Application principale
│   ├── migrations/
│   ├── templates/
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   └── ...
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── templates/
    └── base/
```

### Base de Données
Le schéma de base de données principal comprend les modèles suivants :
- Utilisateur (User)
- Trajet (Trajet)
- Voyage (Voyage)
- Réservation (Reservation)
- Paiement (Paiement)
- Siège (Siege)
- Ville (Ville)
- Gare (Gare)

## 🚀 Guide d'Installation

### Prérequis
- Python 3.9+
- PostgreSQL
- pip
- virtualenv

### Étapes d'installation
1. Cloner le dépôt :
   ```bash
   git clone [URL_DU_REPO]
   cd Agence-App
   ```

2. Créer et activer l'environnement virtuel :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

4. Configurer les variables d'environnement :
   ```bash
   cp .env.example .env
   # Éditer le fichier .env avec vos configurations
   ```

5. Appliquer les migrations :
   ```bash
   python manage.py migrate
   ```

6. Créer un superutilisateur :
   ```bash
   python manage.py createsuperuser
   ```

7. Lancer le serveur de développement :
   ```bash
   python manage.py runserver
   ```

## 🖥️ Guide d'Utilisation

### Pour les Utilisateurs
1. Créez un compte ou connectez-vous
2. Recherchez un trajet
3. Sélectionnez votre siège
4. Passez au paiement
5. Recevez votre e-billet par email

### Pour les Administrateurs
1. Accédez au panneau d'administration : `/admin`
2. Gérez les trajets, les réservations et les utilisateurs
3. Consultez les rapports et statistiques

## 🔒 Sécurité

### Mesures de sécurité implémentées
- Authentification à deux facteurs (2FA)
- Protection CSRF
- Validation des entrées utilisateur
- Chiffrement des données sensibles
- Journalisation des activités

### Bonnes pratiques
- Mots de passe forts requis
- Sessions sécurisées
- Mises à jour de sécurité régulières
- Sauvegardes automatiques

## 🚀 Déploiement

### Préparation à la production
1. Configurer les paramètres de production dans `settings/production.py`
2. Configurer le serveur web (Nginx/Apache)
3. Configurer le serveur d'application (Gunicorn/uWSGI)
4. Configurer SSL/TLS

### Déploiement avec Docker (Recommandé)
```bash
docker-compose up --build
```

## 🛠️ Maintenance

### Tâches courantes
- Sauvegardes régulières de la base de données
- Mises à jour de sécurité
- Surveillance des performances
- Gestion des erreurs et logs

### Procédures de dépannage
1. Vérifier les logs d'erreur
2. Tester la connexion à la base de données
3. Vérifier les permissions des fichiers
4. Tester les services externes (paiement, email, etc.)

## 🚀 Perspectives d'Évolution

### Fonctionnalités futures
- Application mobile dédiée
- Système de géolocalisation en temps réel
- Chatbot d'assistance
- Intégration avec les réseaux sociaux
- Système de notation des trajets

### Améliorations techniques
- Mise en cache des requêtes fréquentes
- Optimisation des performances
- Microservices pour une meilleure évolutivité
- Intégration continue/déploiement continu (CI/CD)

---

📅 **Dernière mise à jour** : Décembre 2025  
👥 **Équipe de développement** : [Votre équipe]  
📧 **Contact** : [votre@email.com]  
🌐 **Site web** : [URL du site]
