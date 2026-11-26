# Chargement des données NovaMarket

| Fichier | Collection | Documents | Identifiant métier |
|---|---|---|---|
| `categories.json` | categories | 6 | `code` |
| `clients.json` | clients | 20 | `id_client` |
| `produits.json` | produits | 30 | `id_produit` |
| `commandes.json` | commandes | 50 | `id_commande` |

Les dates sont écrites au format JSON étendu de MongoDB (`{"$date": "2026-09-01T20:13:00Z"}`)
pour être chargées comme de vraies dates (type `Date`), et pas comme du texte.

## Méthode retenue : script Python
```powershell
cd ..\04_Python
python charger_donnees.py
```
Choix justifié : le script est reproductible (même résultat à chaque fois), il vide les
collections avant d'insérer (aucun doublon si on le relance) et il crée les index uniques.
Il sert aussi de remise à zéro.

## Méthode possible : Compass (à la main)
Pour chaque fichier : base `NovaMarket`, créer la collection, puis
**ADD DATA**, **Import JSON or CSV file** et choisir le fichier.
Compass reconnaît aussi le format `$date`. Attention : un second import ajoute
les documents une deuxième fois, il faut donc vider la collection avant.
