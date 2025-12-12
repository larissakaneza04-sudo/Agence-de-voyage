# Documentation - Plateforme de Réservation de Billets de Bus

## 1. Description du besoin

### Contexte
Le secteur du transport interurbain au Burundi nécessite une solution numérique pour moderniser la gestion des réservations et améliorer l'expérience utilisateur.

### Problématiques actuelles
- Gestion manuelle des réservations
- Paiements limités aux espèces
- Absence de suivi en temps réel
- Processus de remboursement complexe

### Objectifs
- Automatisation des réservations
- Paiement en ligne sécurisé
- Gestion en temps réel
- Système de notification
- Tableau de bord d'administration

## 2. Diagrammes UML

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
| 1.4 Payer en ligne   |
| 2.1 Gérer trajets    |
| 2.2 Gérer utilisateurs|
| 3.1 Envoyer notifs   |
+----------------------+
```

### 2.2. Diagramme de Classes
```
+---------------------+
|      Utilisateur   |
+---------------------+
| - id: UUID         |
| - username: str    |
| - email: str       |
| - telephone: str   |
+---------------------+
          ^
          |
+---------------------+
|      Client        |
+---------------------+
| - points_fidelite  |
+---------------------+
          |
          v
+---------------------+
|   Réservation      |
+---------------------+
| - id: UUID         |
| - statut: str      |
| - montant: Decimal |
+---------------------+
```

## 3. Architecture technique

### 3.1. Technologies utilisées
- **Frontend** : HTML5, CSS3, JavaScript, Bootstrap 5
- **Backend** : Django 4.2, Django REST Framework
- **Base de données** : PostgreSQL
- **Authentification** : JWT
- **Paiement** : Stripe, Mobile Money
- **Hébergement** : A définir

### 3.2. Structure du projet
```
agence_transport/
├── agence_transport/  # Configuration
├── reservations/      # Application principale
├── static/           # Fichiers statiques
└── templates/        # Templates HTML
```

## 4. Lien GitHub pour le code source

## 5. Plan de développement et tableau Gantt

### 5.1. Phases de développement
1. Analyse et conception (2 semaines)
2. Développement Frontend (3 semaines)
3. Développement Backend (4 semaines)
4. Tests et corrections (2 semaines)
5. Déploiement (1 semaine)

### 5.2. Tableau Gantt
```
Semaine : 1  2  3  4  5  6  7  8  9 10 11 12
Analyse    ██████████
Frontend         ████████████
Backend             ████████████████
Tests                         ████████
Déploiement                        ███
```

## 6. Prototype fonctionnel

### 6.1. Maquettes

**Page d'accueil**
```
+---------------------+
|  RECHERCHER UN     |
|  TRAJET            |
|                    |
| Départ: [Bujumbura]|
| Arrivée: [Gitega]  |
| Date: [12/12/2025] |
| [Rechercher]       |
+---------------------+
```

**Réservation**
```
+---------------------+
|  RÉSERVATION       |
|                    |
| Siège: [1A] [2A]   |
|        [1B] [2B]   |
|                    |
| Prix: 5 000 FBU    |
| [Payer] [Annuler]  |
+---------------------+
```

### 6.2. Fonctionnalités implémentées
- Recherche de trajets
- Réservation en ligne
- Paiement sécurisé
- Gestion des utilisateurs
- Tableau de bord admin

---

📅 **Dernière mise à jour** :  
👥 **Équipe de développement** :  
📧 **Contact** :  
🌐 **Site web** : 
