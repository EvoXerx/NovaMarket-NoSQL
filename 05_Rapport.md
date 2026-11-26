# NovaMarket : rapport

## 1. Installation (captures)
- **Capture 1** : `python -m pip show pymongo` (version installée).
- **Capture 2** : `Get-Service MongoDB` (service `Running`) et Compass connecté à `localhost:27017`.

## 2. Chargement des données
Méthode : script `04_Python/charger_donnees.py` (voir `02_Donnees/CHARGEMENT.md`).
- **Capture 3** : sortie du script (6 catégories, 20 clients, 30 produits, 50 commandes).
- **Capture 4** : Compass, base `NovaMarket` avec ses 4 collections et leur nombre de documents.
- **Capture 5** : Compass, un document de `commandes` déplié (tableau `lignes`).

## 3. Requêtes mongosh
Fichier `03_Mongosh/requetes.js`, exécuté en entier avec `mongosh --file requetes.js`
(sans erreur). Exemples de résultats : 20 clients (requête 14) ; catégories au prix moyen
supérieur à 500 € : ORDI (1 145 €) et TEL (869 €) (requête 21) ; CMD049 passée de
`en_attente` à `payee` (requête 19). Le jeu a ensuite été rechargé.
- **Captures 6 à 8** : requêtes 9, 15 et 21, puis 17 et 19 avec leur vérification.

## 4. Application Python
- **Capture 9** : menu de `app.py`.
- **Capture 10** : création d'une commande valide (total affiché).
- **Capture 11** : commande refusée pour stock insuffisant.
- **Capture 12** : Compass, la nouvelle commande dans `commandes` et le stock diminué dans `produits`.

## 5. Les huit indicateurs (`python analyses.py`)
Règle commune : le chiffre d'affaires (CA, en euros) ne compte que les commandes `payee`,
`expediee` et `livree`. On distingue le **CA** (euros), le **nombre de commandes** et les
**quantités vendues** (unités).

| N° | Indicateur | Définition et données | Filtre |
|---|---|---|---|
| 31 | CA total | somme des `total` des commandes | statuts du CA |
| 32 | CA par catégorie | somme `quantite x prix_unitaire` des lignes, groupée par `lignes.categorie` | statuts du CA |
| 33 | Commandes par client | nombre de commandes par `id_client`, clients sans commande affichés à 0 | aucun |
| 34 | Panier moyen | moyenne des `total` | statuts du CA |
| 35 | Top 5 en quantité | somme des `lignes.quantite` par produit | statuts du CA |
| 36 | Stock critique | produits dont `stock` < 5 | aucun |
| 37 | Répartition par statut | nombre de commandes par `statut` | aucun |
| 38 | CA mensuel | somme des `total` groupée par mois de `date_commande` | statuts du CA |

**Capture 13** : sortie complète de `python analyses.py`.

Résultats obtenus le 26/11/2026 sur le jeu initial (sortie de `python analyses.py`) :

| N° | Résultat |
|---|---|
| 31 | CA total : **55 108,00 €** sur 40 commandes |
| 32 | ORDI 28 739,00 € ; ECRAN 10 858,00 € ; TEL 6 793,00 € ; AUDIO 3 930,00 € ; PERIPH 3 269,00 € ; STOCK 1 519,00 € |
| 33 | C004 : 9 ; C002 : 7 ; C010 : 6 ; C011 : 4 ; C007, C009, C013, C014, C015 : 3 ; C003, C006, C008, C012 : 2 ; C016 : 1 ; C001, C005, C017 à C020 : 0 |
| 34 | Panier moyen : **1 377,70 €** |
| 35 | P014 Écran incurvé 34 pouces : 11 unités ; P004 Portable Gamer Titan 17 : 9 ; P023 Webcam Full HD : 7 ; P001 Portable Nova 14 pouces : 6 ; P019 Barre de son TV : 6 |
| 36 | 9 produits : P009 et P030 (0, rupture), P014 (1), P004 et P025 (2), P010 et P019 (3), P002 et P023 (4) |
| 37 | livree 33 ; en_attente 6 ; annulee 4 ; payee 4 ; expediee 3 (total 50) |
| 38 | 2026-09 : 19 757,00 € (13 commandes) ; 2026-10 : 25 948,00 € (19) ; 2026-11 : 9 403,00 € (8) |

Contrôles de cohérence : la somme des trois mois (19 757 + 25 948 + 9 403) et la somme des catégories
donnent bien 55 108 € ; 55 108 / 40 = 1 377,70 €. Novembre est plus faible car le mois n'est pas
terminé et ses commandes les plus récentes sont encore en attente (non comptées).

## 6. Tests (`python tests.py`)
Les tests tournent sur une base séparée `NovaMarketTest`, rechargée au début et supprimée
à la fin : le jeu principal n'est pas modifié.

| N° | Test | Résultat attendu |
|---|---|---|
| 39 | connexion au serveur local, puis à un port fermé | réussie, puis message d'erreur sans plantage |
| 40 | recherche de P012 puis de P999 | trouvé, puis introuvable |
| 41 | ajout de P900 valide puis prix -5 | ajouté, puis refusé |
| 42 | commande avec stock suffisant puis quantité trop grande | créée, puis refusée sans toucher au stock |
| 43 | commande pour le client C999 | refusée |
| 44 | total et stock après la commande valide | total = somme des lignes, stocks diminués |
| 45 | nombre de documents et identifiants distincts, doublon C001 | égaux aux fichiers, doublon refusé |
| 46 | CA total et répartition par statut recalculés en Python pur | identiques aux agrégations |

**Capture 14** : sortie de `python tests.py`.

Résultat de l'exécution : **19 vérifications sur 19 réussies**. Messages affichés lors des refus :
- prix négatif : « Le prix doit être strictement positif. »
- stock insuffisant : « Stock insuffisant pour P004 : 2 disponible(s), 3 demandé(s). »
- client inexistant : « Client C999 inexistant. »
- connexion impossible : « Connexion impossible au serveur MongoDB : ServerSelectionTimeoutError »

Test 44 : commande de 2 x P022 (49 €) et 3 x P029 (19,90 €), total enregistré 157,70 €
(2 x 49 + 3 x 19,90 = 157,70), stocks diminués de 2 et 3.

## 7. Limites
- **Pas de transaction.** La création d'une commande enchaîne plusieurs opérations
  (retrait du stock de chaque produit, puis insertion de la commande). Toutes les vérifications
  (client, produits, stock suffisant) sont faites avant la première modification : dans le scénario
  nominal, stock et total restent cohérents. Mais si le programme s'arrête brutalement entre deux
  opérations (coupure, plantage), le stock peut être retiré sans que la commande soit enregistrée.
  De même, deux utilisateurs qui commandent le dernier exemplaire au même instant pourraient
  passer tous les deux la vérification.
  La solution est une transaction MongoDB (`client.start_session()` et `with_transaction`),
  qui exige un serveur en replica set : non disponible sur l'installation locale standard.
- Numérotation des commandes par tri sur l'identifiant `CMDxxx` : valable jusqu'à CMD999.
- Le stock initial du jeu est fixé à la main : il n'est pas recalculé à partir des commandes historiques.
- La requête 18 (`$mul` de 1,1) peut produire des prix à plus de deux décimales.

## 8. Difficulté rencontrée
Les dates : chargées avec le module `json` standard, elles seraient restées du texte et le CA mensuel
aurait dû découper des chaînes. Les fichiers utilisent le format `{"$date": ...}` lu par
`bson.json_util` (fourni avec PyMongo) : les dates sont de vraies dates et `$dateToString` fonctionne.

## 9. Conclusion
La base NovaMarket couvre le périmètre demandé : 4 collections reliées par des identifiants métier
uniques, un jeu de données cohérent rechargeable sans doublon, les 15 requêtes mongosh, une
application console qui applique les règles de gestion (validation, stock, total, statuts) et les
8 indicateurs. Les tests obligatoires passent tous et deux indicateurs ont été recalculés
indépendamment en Python.

Améliorations possibles : transactions pour la création de commande (avec un replica set),
recherche par mot-clé insensible aux accents (aujourd'hui « ecran » ne trouve pas « Écran »),
arrondi au centime dans la hausse de prix de la requête 18, et index supplémentaires
(par exemple sur `commandes.id_client`) si le volume augmente.

## Ressources
Documentation officielle PyMongo et MongoDB ; corrigé du TP PyMongo Librairie (EFREI).
