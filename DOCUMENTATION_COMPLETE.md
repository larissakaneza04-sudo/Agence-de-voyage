# Documentation du Projet - Plateforme de Réservation de Billets de Bus

## 1. Description du Besoin

### Contexte
Le secteur du transport interurbain au Burundi fait face à des défis majeurs liés à la gestion manuelle des réservations. Notre plateforme vise à digitaliser ce processus pour améliorer l'efficacité et l'expérience utilisateur.

### Problématiques Actuelles
- Gestion manuelle des réservations
- Système de paiement limité aux espèces
- Absence de suivi en temps réel
- Processus de remboursement complexe
- Manque de transparence dans la gestion des places

### Objectifs Principaux
- Automatisation complète du processus de réservation
- Paiement en ligne sécurisé
- Gestion en temps réel des disponibilités
- Système de notification automatique
- Tableau de bord d'administration complet

## 2. Modélisation UML

### 2.1. Diagramme de Cas d'Utilisation

```
+----------------------+
|        ACTEURS       |
+----------------------+
|    1. Client         |
|    2. Administrateur |
|    3. Système        |
+----------------------+
          |
          v
+----------------------+
|   CAS D'UTILISATION  |
+----------------------+
| 1.1 S'authentifier   |
| 1.2 Consulter trajets|
| 1.3 Réserver billet  |
| 1.4 Paiement en ligne|
| 1.5 Annuler réservation |
| 1.6 Gérer profil    |
| 2.1 Gérer trajets   |
| 2.2 Gérer utilisateurs |
| 2.3 Voir statistiques |
| 3.1 Envoyer notifications |
| 3.2 Générer rapports |
+----------------------+
```

### 2.2. Diagramme de Classes

```
+---------------------+       +---------------------+
|      Utilisateur   |       |      Trajet         |
+---------------------+       +---------------------+
| - id: UUID         |       | - id: UUID          |
| - username: str    |       | - depart: str       |
| - email: str       |       | - arrivee: str      |
| - telephone: str   |       | - distance: float   |
| - password: str    |       | - duree: time       |
| - date_joined: date|       | - prix: Decimal     |
+---------------------+       +---------------------+
          ^                              ^
          |                              |
+---------------------+       +---------------------+
|      Client        |       |      Voyage         |
+---------------------+       +---------------------+
| - points_fidelite  |       | - id: UUID          |
| - statut           |       | - trajet: ForeignKey|
+---------------------+       | - date_depart: datetime
          |                   | - date_arrivee: datetime
          |                   | - vehicule: ForeignKey
          |                   +---------------------+
          |                              ^
          |                              |
+---------------------+       +---------------------+
|   Réservation      |       |       Siège         |
+---------------------+       +---------------------+
| - id: UUID         |       | - id: UUID          |
| - client: ForeignKey|       | - numero: int       |
| - voyage: ForeignKey|       | - classe: str       |
| - siege: ForeignKey |       | - statut: str       |
| - date_reservation: |       +---------------------+
| - statut: str      |
| - montant: Decimal |
+---------------------+
          |
          v
+---------------------+
|      Paiement      |
+---------------------+
| - id: UUID         |
| - reservation: ForeignKey
| - montant: Decimal |
| - methode: str     |
| - statut: str      |
| - date_paiement:   |
+---------------------+
```

## 3. Architecture Technique

### 3.1. Stack Technique

**Frontend**
- HTML5, CSS3, JavaScript
- Bootstrap 5 pour le design responsive
- jQuery pour les interactions dynamiques
- Chart.js pour les graphiques du tableau de bord

**Backend**
- Framework : Django 4.2
- Base de données : PostgreSQL
- Authentification : Django Allauth
- API REST : Django REST Framework
- Gestion des tâches asynchrones : Celery

**Services Externes**
- Paiement : Stripe, Mobile Money
- Envoi d'emails : SendGrid
- Notifications SMS : Twilio
- Stockage : AWS S3 (pour les fichiers statiques et médias)

### 3.2. Structure du Projet

```
agence_transport/
├── agence_transport/          # Configuration du projet
│   ├── settings/             # Fichiers de configuration
│   ├── urls.py               # URLs principales
│   └── asgi.py/wsgi.py       # Configuration ASGI/WSGI
│
├── reservations/             # Application principale
│   ├── migrations/           # Migrations de la base de données
│   ├── templates/            # Templates HTML
│   ├── admin.py             # Configuration de l'admin
│   ├── models.py            # Modèles de données
│   ├── views.py             # Vues
│   ├── forms.py             # Formulaires
│   ├── serializers.py       # Sérialiseurs API
│   └── tasks.py             # Tâches asynchrones
│
├── static/                  # Fichiers statiques
│   ├── css/
│   ├── js/
│   └── images/
│
└── templates/               # Templates de base
    └── base/               # Templates communs
```

## 4. Lien GitHub du Code Source

🔗 [https://github.com/votre-utilisateur/agence-transport](https://github.com/votre-utilisateur/agence-transport)

## 5. Plan de Développement

### 5.1. Phases de Développement

| Phase | Durée | Tâches |
|-------|-------|---------|
| **1. Analyse** | 1 semaine | - Analyse des besoins<br>- Élaboration des spécifications<br>- Validation avec les parties prenantes |
| **2. Conception** | 1 semaine | - Modélisation UML<br>- Conception de la base de données<br>- Architecture technique |
| **3. Développement Frontend** | 2 semaines | - Maquettes<br>- Intégration HTML/CSS<br>- Développement des interfaces |
| **4. Développement Backend** | 3 semaines | - Configuration du projet<br>- Développement des modèles<br>- Mise en place de l'API |
| **5. Intégration Paiement** | 1 semaine | - Stripe<br>- Mobile Money<br>- Gestion des remboursements |
| **6. Tests** | 1 semaine | - Tests unitaires<br>- Tests d'intégration<br>- Tests de charge |
| **7. Déploiement** | 3 jours | - Mise en production<br>- Configuration du serveur<br>- Migration des données |

### 5.2. Tableau de Gantt

```
Semaine :     1    2    3    4    5    6    7    8    9   10   

Analyse       ███████
Conception         ███████
Frontend                ████████████████
Backend                      ███████████████████████
Paiement                                          ███████
Tests                                                  ███████
Déploiement                                                 ███
```

## 6. Prototype Fonctionnel

### 6.1. Maquettes des Écrans Principaux

**Page d'Accueil**
```
+-----------------------------------------------------+
|                  AGENCE DE TRANSPORT                |
+-----------------------------------------------------+
| [Rechercher un trajet]                             |
|                                                    |
| Départ: [Bujumbura   ▼]  Arrivée: [Gitega   ▼]     |
| Date: [12/12/2025 ▼]  Passagers: [1 ▼] [Rechercher]|
+-----------------------------------------------------+
|                TRAJETS POPULAIRES                   |
| +----------------+  +----------------+             |
| | Bujumbura      |  | Gitega         |             |
| | → Gitega       |  | → Ngozi        |             |
| | 2h30 • 5 000 FBU|  | 3h15 • 7 000 FBU|            |
| +----------------+  +----------------+             |
+-----------------------------------------------------+
```

**Réservation**
```
+-----------------------------------------------------+
| RÉSERVATION - BUJUMBURA → GITEGA - 12/12/2025      |
+-----------------------------------------------------+
| Sélectionnez votre siège :                          |
| [1A] [2A] [3A] [4A] [5A]                           |
| [1B] [2B] [3B] [4B] [5B]                           |
| [1C] [2C] [3C] [4C] [5C]                           |
|                                                     |
| Détails :                                           |
| - Départ : 08:00 - Bujumbura                        |
| - Arrivée : 10:30 - Gitega                          |
| - Siège : 2A                                        |
| - Prix : 5 000 FBU                                  |
|                                                     |
| [Payer maintenant] [Annuler]                        |
+-----------------------------------------------------+
```

### 6.2. Fonctionnalités Implémentées

**Espace Client**
- Création et gestion de compte
- Historique des réservations
- Gestion des informations personnelles
- Suivi des points de fidélité

**Réservation**
- Recherche de trajets en temps réel
- Sélection de siège interactive
- Paiement sécurisé
- E-billets avec QR code

**Administration**
- Gestion des trajets et horaires
- Suivi des réservations
- Gestion des utilisateurs
- Tableaux de bord analytiques

## 7. Conclusion

Cette documentation présente une vue complète de notre solution de réservation de billets de bus. La plateforme est conçue pour être évolutive, sécurisée et facile à utiliser, répondant aux besoins des voyageurs et des gestionnaires de transport.

---

📅 **Dernière mise à jour** : Décembre 2025  
👥 **Équipe de développement** : [Votre équipe]  
📧 **Contact** : [votre@email.com]  
🌐 **Site web** : [URL du site]
