# NovaMarket : dossier de conception

## 1. Acteurs, opérations et informations

| Acteur | Opérations métier |
|---|---|
| Gestionnaire du catalogue | ajouter un produit, consulter et rechercher, mettre à jour le stock, repérer les ruptures |
| Service commercial | enregistrer un client, créer une commande, consulter l'historique d'un client, faire évoluer le statut |
| Direction | consulter les indicateurs : chiffre d'affaires, panier moyen, meilleures ventes, évolution mensuelle |
| Client (indirect) | passe les commandes (saisies par le service commercial dans ce projet) |

Informations à conserver : les catégories, les clients (identité, contact, ville, date d'inscription),
les produits (libellé, catégorie, prix, stock) et les commandes (client, date, statut, lignes, total).

## 2. Dictionnaire de données

### Collection `categories`
| Champ | Signification | Type | Oblig. | Exemple |
|---|---|---|---|---|
| `code` | identifiant métier de la catégorie | string | oui, unique | `"ORDI"` |
| `libelle` | nom affiché | string | oui | `"Ordinateurs portables"` |
| `description` | précision sur le contenu | string | non | `"PC et Mac portables"` |

### Collection `clients`
| Champ | Signification | Type | Oblig. | Exemple |
|---|---|---|---|---|
| `id_client` | identifiant métier | string | oui, unique | `"C001"` |
| `nom` | nom de famille | string | oui | `"Martin"` |
| `prenom` | prénom | string | oui | `"Lucas"` |
| `email` | adresse électronique | string | oui | `"lucas.martin@exemple.fr"` |
| `ville` | ville de résidence | string | oui | `"Paris"` |
| `date_inscription` | date de création du compte | date | oui | `2025-01-23` |

### Collection `produits`
| Champ | Signification | Type | Oblig. | Exemple |
|---|---|---|---|---|
| `id_produit` | identifiant métier | string | oui, unique | `"P012"` |
| `libelle` | nom commercial | string | oui | `"Écran 27 pouces QHD"` |
| `categorie` | code de la catégorie (référence vers `categories.code`) | string | oui | `"ECRAN"` |
| `prix` | prix catalogue actuel en euros TTC | double | oui, > 0 | `299.0` |
| `stock` | unités disponibles | int | oui, >= 0 | `14` |

### Collection `commandes`
| Champ | Signification | Type | Oblig. | Exemple |
|---|---|---|---|---|
| `id_commande` | identifiant métier | string | oui, unique | `"CMD001"` |
| `id_client` | client qui commande (référence vers `clients.id_client`) | string | oui | `"C011"` |
| `date_commande` | date et heure de la commande | date | oui | `2026-09-01T20:13Z` |
| `statut` | état de la commande | string | oui | `"livree"` |
| `lignes` | produits commandés | tableau d'objets | oui, au moins 1 | voir ci-dessous |
| `lignes.id_produit` | produit commandé (référence vers `produits.id_produit`) | string | oui | `"P027"` |
| `lignes.libelle` | libellé au moment de l'achat (copie) | string | oui | `"SSD interne NVMe 2 To"` |
| `lignes.categorie` | catégorie au moment de l'achat (copie) | string | oui | `"STOCK"` |
| `lignes.quantite` | unités commandées | int | oui, > 0 | `1` |
| `lignes.prix_unitaire` | prix pratiqué au moment de l'achat | double | oui, > 0 | `179.0` |
| `total` | montant de la commande en euros | double | oui | `179.0` |

## 3. Schéma des collections

```
 categories                 produits                      commandes                    clients
+-------------+           +-------------+           +----------------------+     +------------------+
| code (PK)   |<----------| categorie   |           | id_commande (PK)     |     | id_client (PK)   |
| libelle     |   1    n  | id_produit  |<--------+ | id_client -----------+---->| nom, prenom      |
| description |           | libelle     |  n    1 | | date_commande        | n 1 | email, ville     |
+-------------+           | prix, stock |         | | statut, total        |     | date_inscription |
                          +-------------+         | | lignes: [            |     +------------------+
                                                  +-+---- id_produit       |
                                                    |     libelle, categorie
                                                    |     quantite, prix_unitaire ]
                                                    +----------------------+
```

Relations logiques :
- une catégorie regroupe plusieurs produits (référence par `code`) ;
- un client passe zéro, une ou plusieurs commandes (référence par `id_client`) ;
- une commande contient une ou plusieurs lignes **imbriquées** ; chaque ligne référence un produit.

Le périmètre est celui recommandé (4 collections), sans variante.

## 4. Imbrication ou référence ?

| Critère | Documents imbriqués | Références |
|---|---|---|
| Lecture | un seul `find` ramène tout | il faut une seconde requête ou un `$lookup` |
| Mise à jour | dupliquer une donnée oblige à la modifier partout | une seule copie à modifier |
| Taille | le document grossit avec le tableau (limite de 16 Mo) | documents petits et stables |
| Cycle de vie | la donnée n'existe pas sans son parent | la donnée vit seule |

Choix appliqués :
- **Lignes de commande : imbriquées** dans la commande. Une ligne n'a aucun sens hors de sa commande,
  elle est toujours lue avec elle (affichage, calcul du total), et une commande compte peu de lignes.
  C'est le cas typique de l'imbrication.
- **Produit dans la ligne : référence** (`id_produit`) **plus une copie** du libellé, de la catégorie
  et du prix. La référence permet de retrouver le produit et de gérer le stock ; la copie fige l'état
  au moment de l'achat (voir la question obligatoire) et évite un `$lookup` dans les statistiques.
- **Client dans la commande : référence** (`id_client`). Un client a de nombreuses commandes et
  ses coordonnées peuvent changer : on ne les copie pas.
- **Catégorie dans le produit : référence par code court** (`"ORDI"`). Le code est lisible,
  stable, et suffit pour filtrer et grouper. Le libellé complet reste dans `categories`
  et ne se modifie qu'à un seul endroit. Une catégorie imbriquée serait répétée dans 30 produits.

## 5. Règles de gestion

**Unicité.** `code`, `id_client`, `id_produit` et `id_commande` sont uniques : un index unique
(`create_index(..., unique=True)`) est créé au chargement ; MongoDB refuse alors un doublon.
L'application vérifie aussi avant l'insertion pour afficher un message clair.

**Validation (dans `metier.py`).**
- produit : tous les champs présents, prix strictement positif, stock entier positif ou nul,
  catégorie existante, identifiant libre ;
- commande : client existant, au moins une ligne, quantités entières strictement positives,
  produits existants, stock suffisant ;
- statut : une des cinq valeurs autorisées.

**Calcul du total.** `total` = somme de `quantite x prix_unitaire` des lignes, arrondie au centime.
Il est calculé par le programme à partir des lignes, jamais saisi.

**Stock.**
- seuil d'alerte : **5 unités**. En dessous, le produit est signalé (stock critique) ; à 0, il est
  en rupture. Le seuil est le même que dans la requête 10 du sujet ; dans ce jeu, une commande
  porte au plus 3 unités d'un produit, donc sous 5 unités deux commandes peuvent vider le stock ;
- à la création, le stock est retiré tout de suite (réservation), même si la commande est
  en attente de paiement, pour ne pas vendre deux fois la même unité ;
- la création est refusée si une quantité dépasse le stock disponible ;
- à l'annulation, les quantités des lignes sont remises en stock.

**Statuts et transitions.**
```
en_attente  vers  payee ou annulee
payee       vers  expediee ou annulee
expediee    vers  livree
livree, annulee : statuts finaux
```
Une commande expédiée ne peut plus être annulée (il faudrait gérer un retour, hors périmètre).

**Chiffre d'affaires.** Seules les commandes `payee`, `expediee` et `livree` comptent : une commande
en attente n'est pas encore payée et une commande annulée ne rapporte rien.

## 6. Exemples de documents

Produit :
```json
{
  "id_produit": "P013",
  "libelle": "Écran 32 pouces 4K",
  "categorie": "ECRAN",
  "prix": 549.0,
  "stock": 5
}
```

Commande avec un tableau d'objets imbriqués :
```json
{
  "id_commande": "CMD051",
  "id_client": "C004",
  "date_commande": { "$date": "2026-11-26T10:30:00Z" },
  "statut": "en_attente",
  "lignes": [
    { "id_produit": "P003", "libelle": "Ultrabook Zenith 13", "categorie": "ORDI",
      "quantite": 1, "prix_unitaire": 1099.0 },
    { "id_produit": "P022", "libelle": "Souris sans fil Ergo", "categorie": "PERIPH",
      "quantite": 2, "prix_unitaire": 49.0 }
  ],
  "total": 1197.0
}
```

## Question obligatoire : pourquoi conserver le prix au moment de l'achat ?

Parce qu'une commande est un fait passé : le client a payé un montant précis, qui figure sur sa facture.
Si la commande ne gardait que la référence du produit et relisait le prix du catalogue :
- une baisse ou une hausse de prix modifierait après coup le total des anciennes commandes ;
- le chiffre d'affaires passé changerait à chaque modification du catalogue, les indicateurs
  ne seraient plus fiables ;
- la facture ne correspondrait plus au paiement réel (problème comptable et juridique).

Le jeu de données l'illustre : l'écran 27 pouces QHD (P012) était à 329 € en septembre et est
passé à 299 € au 1er octobre. La commande CMD009 (23 septembre) garde 329 € dans sa ligne,
alors que CMD024 (17 octobre) a été payée 299 €.
