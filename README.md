# GR2C — Application Django de gestion de stock et de cotations

Projet web Django basé sur le cahier des charges, l'architecture et le schéma relationnel GR2C/Festo fournis.

## Fonctionnalités
- Authentification et profils : Direction, Chargé d'affaires, Magasinier, Consultation
- Tableau de bord
- Catalogue articles/catégories
- Tiers et contacts
- Mouvements de stock et alertes
- Cotations, calcul prix/transport/douane/marge, statuts et immutabilité après émission
- Bons de livraison et décrément automatique du stock
- Factures, TVA 18 %, règlements et statuts
- Journalisation des actions sensibles
- Paramètres
- Génération locale de PDF
- Administration Django
- SQLite par défaut, facilement remplaçable par PostgreSQL

## Installation Windows
```powershell
cd gr2c_django
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
py manage.py migrate
py manage.py seed_gr2c
py manage.py runserver
```

Ouvrir http://127.0.0.1:8000/

Compte de démonstration :
- utilisateur : admin
- mot de passe : admin123

## Remarque
Le projet est une version Django serveur complète et fonctionnelle. Elle respecte le cycle métier des documents fournis et prépare une évolution vers PostgreSQL/hébergement partagé.
