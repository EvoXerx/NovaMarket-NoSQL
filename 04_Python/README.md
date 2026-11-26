# NovaMarket : application Python / PyMongo

## Prérequis
- MongoDB Community Server démarré sur `localhost:27017` (service Windows « MongoDB »).
- Python 3.10 ou plus récent.
- Facultatif : MongoDB Compass pour visualiser la base.

## Installation
Dans PowerShell, depuis le dossier `04_Python` :
```powershell
python -m pip install -r requirements.txt
```

## Base utilisée
- Base : `NovaMarket`
- Collections : `categories`, `clients`, `produits`, `commandes`
- Serveur : `mongodb://localhost:27017/` par défaut. Pour un autre serveur (avec mot de passe),
  définir la variable d'environnement au lieu de modifier le code :
  ```powershell
  $env:MONGO_URI = "mongodb://utilisateur:motdepasse@serveur:27017/"
  ```

## Chargement et remise à zéro du jeu de données
```powershell
python charger_donnees.py
```
Le script vide les quatre collections, réinsère les fichiers JSON de `../02_Donnees`
et crée un index unique sur chaque identifiant métier. On peut le relancer autant de fois
qu'on veut : il n'y a jamais de doublons. C'est aussi la procédure de remise à zéro
après les requêtes mongosh ou des essais dans l'application.

## Lancement
```powershell
python app.py        # application console (menu)
python analyses.py   # les 8 indicateurs de la partie E
python tests.py      # les tests obligatoires (base séparée NovaMarketTest)
```

## Organisation du code
| Fichier | Rôle |
|---|---|
| `connexion.py` | connexion au serveur et vérification par `ping` |
| `donnees.py` | accès aux données (appels PyMongo uniquement) |
| `metier.py` | règles de gestion : validations, commandes, stock, statuts |
| `analyses.py` | pipelines d'agrégation des indicateurs |
| `app.py` | menu console et saisies |
| `charger_donnees.py` | chargement et remise à zéro |
| `tests.py` | tests 39 à 46 du sujet |
