from datetime import datetime, timezone

import donnees

#regles métier : constantes et transitions autorisées
SEUIL_ALERTE_STOCK = 5          # en dessous de 5 unités : réapprovisionner
STATUTS = ["en_attente", "payee", "expediee", "livree", "annulee"] # les statuts possibles d'une commande
STATUTS_CA = ["payee", "expediee", "livree"]   # commandes comptées dans le chiffre d'affaires
TRANSITIONS = {                 # statut actuel : statuts autorisés ensuite pas de retour possible (exemple:annulee -> livree) 
    "en_attente": ["payee", "annulee"],
    "payee": ["expediee", "annulee"],
    "expediee": ["livree"],
    "livree": [],
    "annulee": [],
}


class ErreurMetier(Exception):
    """Exception levée par les fonctions métier en cas de problème."""
    pass


# produits
def valider_produit(db, produit):
    requis = ["id_produit", "libelle", "categorie", "prix", "stock"]
    manquants = [champ for champ in requis if produit.get(champ) in (None, "")]
    if manquants:
        raise ErreurMetier("Champs manquants : " + ", ".join(manquants))
    try:
        # on arrondit le prix à 2 décimales car on est en train de faire des calculs financiers pour éviter les problèmes d'affichage (ex. 1.1999999999999999) 
        prix = round(float(produit["prix"]), 2)
        stock = int(produit["stock"])
    except (TypeError, ValueError):
        raise ErreurMetier("Le prix doit être un nombre et le stock un entier.")

    # on vérifie que le prix est strictement positif et que le stock est un entier non négatif
    if prix <= 0:
        raise ErreurMetier("Le prix doit être strictement positif.")
    if stock < 0:
        raise ErreurMetier("Le stock ne peut pas être négatif.")

    # on vérifie que l'identifiant du produit est unique
    id_produit = str(produit["id_produit"]).strip().upper()
    if donnees.trouver_produit(db, id_produit):
        raise ErreurMetier(f"L'identifiant {id_produit} existe déjà.")

    # on vérifie que la catégorie du produit existe
    categorie = str(produit["categorie"]).strip().upper()
    if not donnees.categorie_existe(db, categorie):
        raise ErreurMetier(f"La catégorie {categorie} n'existe pas.")

    # on renvoie un dictionnaire "propre" avec les types corrects et les chaînes de caractères nettoyées
    return {"id_produit": id_produit, "libelle": str(produit["libelle"]).strip(),
            "categorie": categorie, "prix": prix, "stock": stock}


def ajouter_produit(db, produit):
    propre = valider_produit(db, produit)
    if not propre:
        raise ErreurMetier("Produit invalide.")
    donnees.inserer_produit(db, propre)
    return propre


def modifier_stock(db, id_produit, nouveau_stock):
    #check si le stock est un entier positif ou nul
    if not isinstance(nouveau_stock, int) or nouveau_stock < 0:
        raise ErreurMetier("Le stock doit être un entier positif ou nul.")
    if not donnees.changer_stock(db, id_produit, nouveau_stock):
        raise ErreurMetier(f"Produit {id_produit} introuvable.")


# commandes
def prochain_id_commande(db):
    # génère un identifiant de commande unique en incrémentant le dernier identifiant existant comme auto-incrément (ex. CMD045 -> CMD046)
    dernier = donnees.dernier_id_commande(db)
    numero = int(dernier[3:]) + 1 if dernier else 1
    # on renvoie l'identifiant formaté avec 3 chiffres et le préfixe "CMD"
    return f"CMD{numero:03d}"


def creer_commande(db, id_client, demandes):
    # vérifie que le client existe et que la commande contient au moins une ligne
    if not donnees.trouver_client(db, id_client):
        raise ErreurMetier(f"Client {id_client} inexistant.")
    if not demandes:
        raise ErreurMetier("Une commande doit contenir au moins une ligne.")

    # Regrouper les quantités d'un même produit saisi deux fois
    quantites = {}
    for id_produit, quantite in demandes:
        if not isinstance(quantite, int) or quantite <= 0:
            raise ErreurMetier("Chaque quantité doit être un entier strictement positif.")
        quantites[id_produit] = quantites.get(id_produit, 0) + quantite

    # vérification règle métier : stock suffisant pour chaque produit
    lignes = []
    for id_produit, quantite in quantites.items():
        produit = donnees.trouver_produit(db, id_produit)
        if not produit:
            raise ErreurMetier(f"Produit {id_produit} inexistant.")
        if produit["stock"] < quantite:
            raise ErreurMetier(f"Stock insuffisant pour {id_produit} : "
                               f"{produit['stock']} disponible(s), {quantite} demandé(s).")
        lignes.append({"id_produit": id_produit, "libelle": produit["libelle"],
                       "categorie": produit["categorie"], "quantite": quantite,
                       "prix_unitaire": produit["prix"]})  # prix figé au moment de l'achat

    # on retire le stock des produits commandés (on ne peut pas faire de commande si le stock est insuffisant)
    for ligne in lignes:
        donnees.retirer_stock(db, ligne["id_produit"], ligne["quantite"])

    # sauvegarde de la commande dans la base de données avec un identifiant unique, le statut initial "en_attente" et la date actuelle
    commande = {
        "id_commande": prochain_id_commande(db),
        "id_client": id_client,
        "date_commande": datetime.now(timezone.utc),
        "statut": "en_attente",
        "lignes": lignes,
        "total": calculer_total(lignes),
    }
    donnees.inserer_commande(db, commande)
    return commande


def calculer_total(lignes):
    # calcule le total d'une commande en multipliant la quantité par le prix unitaire pour chaque ligne et en arrondissant à 2 décimales
    return round(sum(l["quantite"] * l["prix_unitaire"] for l in lignes), 2)


def changer_statut(db, id_commande, nouveau_statut):
    # find la commandes 
    commande = donnees.trouver_commande(db, id_commande)
    if not commande:
        raise ErreurMetier(f"Commande {id_commande} inexistante.")
    # définition du nouveau statut et vérification des transitions autorisées
    if nouveau_statut not in STATUTS:
        raise ErreurMetier(f"Statut inconnu. Statuts autorisés : {', '.join(STATUTS)}.")
    actuel = commande["statut"]
    if nouveau_statut not in TRANSITIONS[actuel]:
        raise ErreurMetier(f"Passage de {actuel} à {nouveau_statut} interdit.")
    if nouveau_statut == "annulee":
        for ligne in commande["lignes"]:
            donnees.remettre_stock(db, ligne["id_produit"], ligne["quantite"])
    donnees.changer_statut(db, id_commande, nouveau_statut)
