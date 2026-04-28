# TP_INF_232
Développement d'application de collecte et d'analyse de données
# EnquêteNum — Application de collecte de données

Application Flask complète pour collecter et analyser des données sur l'usage numérique.

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

```bash
python app.py
```

L'application sera disponible sur : http://localhost:5000

## Pages disponibles

| URL | Description |
|-----|-------------|
| `/formulaire` | Formulaire de saisie des réponses |
| `/liste` | Liste des réponses avec filtres et tri |
| `/dashboard` | Tableau de bord avec graphiques |

## Fonctionnalités

- **Formulaire interactif** : champs conditionnels, validation côté client et serveur, barre de progression
- **Tableau de données** : recherche par nom, filtres par genre/niveau, tri par colonne, suppression
- **Tableau de bord** : KPIs, graphiques (genre, éducation, âge, réseaux sociaux)
- **Robustesse** : validation des données, gestion des erreurs, messages flash
- **Design moderne** : responsive, accessible, animations CSS

## Structure

```
enquete_app/
├── app.py              # Application Flask principale
├── database.db         # Base de données SQLite (créée automatiquement)
├── requirements.txt
└── templates/
    ├── base.html       # Template de base (navbar, footer)
    ├── formulaire.html # Formulaire de collecte
    ├── liste.html      # Liste des réponses
    ├── dashboard.html  # Tableau de bord statistique
    └── 404.html        # Page d'erreur
```
