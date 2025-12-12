# 📍 Introduction

Le domaine du transport interurbain joue un rôle essentiel dans la mobilité des populations au Burundi et dans plusieurs pays africains. Cependant, la majorité des agences de transport fonctionnent encore avec des processus manuels et non digitalisés : vente des billets aux guichets, gestion des disponibilités sur papier, absence de notifications automatiques, paiements exclusivement en espèces, et procédures de remboursement complexes. Ce fonctionnement expose les agences à des risques d'erreurs, de fraudes, de pertes de données et limite considérablement leur efficacité opérationnelle.

Avec l'évolution du numérique, les systèmes e-business ont transformé les secteurs bancaires, hôteliers et commerciaux. Il est donc crucial que le secteur du transport adopte, lui aussi, des solutions modernes pour offrir une meilleure expérience client et optimiser ses opérations.

## Objectifs du Projet

Le présent projet vise la conception et le développement d'une application web complète permettant :
- La réservation automatique des billets
- L'affichage des itinéraires, des horaires et des tarifs
- La sélection des sièges disponibles en temps réel
- Le paiement sécurisé en ligne (Mobile Money & cartes)
- L'annulation et le remboursement automatique des billets
- Un système intelligent de récompenses (bonus de fidélité)

Cette solution permettra aux agences d'améliorer la qualité de service, de réduire leurs coûts, d'optimiser la gestion interne et de renforcer la confiance des clients grâce à un système automatisé, fiable et sécurisé.

# 1. Analyse des Besoins

## 1.1. Description du Besoin

### Problématiques du Système Actuel
Le système actuel de réservation de billets au Burundi s'appuie principalement sur :
- Les guichets physiques
- Les appels téléphoniques
- L'attribution manuelle des sièges
- Les paiements sur place
- L'impression manuelle des billets

### Limites du Système Actuel
- Risque de double attribution du même siège
- Perte ou falsification des billets papier
- Files d'attente importantes
- Absence de paiement en ligne
- Remboursements complexes
- Opérations non traçables
- Absence d'un système de fidélité
- Mauvaise gestion des horaires et trajets

### Besoins Identifiés

| Besoin | Description |
|--------|-------------|
| Automatisation | Réserver, payer, annuler sans intervention d'un agent |
| Sécurisation | Authentification, paiements sécurisés, HTTPS |
| Rapidité | Réservation en moins d'une minute |
| Transparence | Disponibilité en temps réel |
| Fidélité | Système de bonus intégré |
| Mobilité | Accessible sur PC, tablette et smartphone |

### Fonctionnalités Clés
1. Affichage des itinéraires, horaires, véhicules et tarifs
2. Réservation d'un siège précis
3. Paiement sécurisé (Stripe, Lumicash, Ecocash)
4. Annulation et remboursement automatique
5. Gestion d'un portefeuille de points bonus
6. Tableau de bord administrateur
7. Exports et statistiques
8. Notifications SMS/WhatsApp (optionnel)

# 2. Diagrammes UML

## 2.1. Diagramme de Cas d'Utilisation

```
+----------------------+
|        CLIENT        |
+----------------------+
        / |   \
       /  |    \
      V   V     V
[Consulter trajets] [Créer compte]
       |
       V
[Choisir un voyage]
       |
       V
[Sélectionner siège]
       |
       V
[Payer billet en ligne]
 /                   \
V                     V
[Recevoir e-billet]  [Annuler réservation]
       |
       V
[Demander remboursement]
       |
       V
[Accumuler/utiliser bonus]
```

## 2.2. Diagramme de Classes

```
+-----------------------+
|        Client         |
+-----------------------+
| - id_client           |
| - nom                 |
| - prenom              |
| - email               |
| - telephone           |
| - password_hash       |
| - points_bonus        |
+-----------------------+
          |
          | 1...*
          v
+-----------------------+
|      Réservation      |
+-----------------------+
| - id_reservation      |
| - date_reservation    |
| - statut              |
| - montant             |
| - mode_paiement       |
| - reference_ticket    |
+-----------------------+
          |
          v
+-----------------------+
|       Paiement        |
+-----------------------+
| - id_paiement         |
| - montant             |
| - statut              |
| - transaction_id      |
| - date_paiement       |
+-----------------------+

+-----------------------+
|        Trajet         |
+-----------------------+
| - id_trajet           |
| - depart              |
| - arrivee             |
| - tarif_base          |
+-----------------------+

+-----------------------+
|        Voyage         |
+-----------------------+
| - id_voyage           |
| - date_depart         |
| - date_arrivee        |
| - vehicle_id          |
+-----------------------+

+-----------------------+
|         Siège         |
+-----------------------+
| - id_siege            |
| - voyage_id           |
| - numero_siege        |
| - statut              |
+-----------------------+
```

# 3. Architecture Technique

## 3.1. Architecture en Trois Couches

a) **Couche Présentation (Frontend)**
- HTML5 / CSS3 / JavaScript
- Framework : Bootstrap 5
- Bibliothèques : jQuery, Axios
- Compatible mobile (responsive design)

b) **Couche Métier (Backend)**
- Framework : Django 4.2
- API REST avec Django REST Framework
- Authentification JWT
- Gestion des paiements (Stripe, Mobile Money)
- Génération de PDF pour les billets
- Envoi d'emails et notifications

c) **Couche Données**
- Base de données : PostgreSQL
- Modèles principaux :
  - Utilisateur
  - Trajet
  - Voyage
  - Réservation
  - Paiement
  - Siège

## 3.2. Services Externes
- **Paiement** : Stripe, Lumicash, Ecocash
- **Notifications** : Twilio (SMS), SendGrid (Email)
- **Carte** : Google Maps API (optionnel)
- **Hébergement** : AWS/Heroku

# 4. Plan de Développement

## 4.1. Phases de Développement (3 semaines)

| Phase | Durée | Livrables |
|-------|-------|-----------|
| Analyse | 3 jours | Cahier des charges |
| Conception | 3 jours | Diagrammes UML |
| Architecture | 2 jours | Design technique |
| Backend | 1 semaine | API + Base de données |
| Frontend | 4 jours | Interfaces utilisateur |
| Paiement | 2 jours | Intégration des passerelles |
| Tests | 3 jours | Rapports de test |
| Déploiement | 1 jour | Version de production |

## 4.2. Tableau de Gantt

```
Semaine :     1            2            3
Jour :     1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21

Analyse          ███
Conception            ███
Architecture               ██
Backend                       ████████
Frontend                                    ████
Paiement                                           ██
Tests                                                ███
Déploiement                                              █
```

# 5. Conclusion

Le présent projet propose une solution complète pour moderniser le secteur du transport interurbain au Burundi. En digitalisant le processus de réservation, nous permettons :
- Une meilleure expérience utilisateur
- Une réduction des erreurs humaines
- Une traçabilité complète des opérations
- Des paiements sécurisés
- Une gestion optimisée des places

# 6. Recommandations

## Pour les Agences de Transport
- Former le personnel à l'utilisation de la plateforme
- Mettre en place une connexion internet fiable
- Digitaliser les autres processus métiers

## Pour l'Équipe de Développement
- Développer une application mobile complémentaire
- Implémenter un système de suivi en temps réel
- Ajouter des fonctionnalités d'analyse prédictive

## Pour la Sécurité
- Mettre en place un système de sauvegarde automatique
- Effectuer des audits de sécurité réguliers
- Maintenir les dépendances à jour

---

📅 **Dernière mise à jour** : Décembre 2025  
👥 **Équipe de développement** : [Votre équipe]  
📧 **Contact** : [votre@email.com]  
🌐 **Site web** : [URL du site]
