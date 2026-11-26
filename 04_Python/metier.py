"""Règles métier : validations, création de commande, changement de statut.

Chaque fonction lève ErreurMetier avec un message clair quand une règle est violée.
"""
from datetime import datetime, timezone

import donnees

SEUIL_ALERTE_STOCK = 5          # en dessous de 5 unités : réapprovisionner
STATUTS = ["en_attente", "payee", "expediee", "livree", "annulee"]
STATUTS_CA = ["payee", "expediee", "livree"]   # commandes comptées dans le chiffre d'affaires
TRANSITIONS = {                 # statut actuel : statuts autorisés ensuite
    "en_attente": ["payee", "annulee"],
    "payee": ["expediee", "annulee"],
    "expediee": ["livree"],
    "livree": [],
    "annulee": [],
}


class ErreurMetier(Exception):
    """Règle de gestion non respectée (message destiné à l'utilisateur)."""


# ---------- Produits ----------
def valider_produit(db, produit):
    """Contrôle les champs requis d'un nouveau produit et renvoie le document propre."""
    requis = ["id_produit", "libelle", "categorie", "prix", "stock"]
    manquants = [champ for champ in requis if produit.get(champ) in (None, "")]
    if manquants:
        raise ErreurMetier("Champs manquants : " + ", ".join(manquants))
    try:
        prix = round(float(produit["prix"]), 2)
        stock = int(produit["stock"])
    except (TypeError, ValueError):
        raise ErreurMetier("Le prix doit être un nombre et le stock un entier.")
    if prix <= 0:
        raise ErreurMetier("Le prix doit être strictement positif.")
    if stock < 0:
        raise ErreurMetier("Le stock ne peut pas être négatif.")
    id_produit = str(produit["id_produit"]).strip().upper()
    if donnees.trouver_produit(db, id_produit):
        raise ErreurMetier(f"L'identifiant {id_produit} existe déjà.")
    categorie = str(produit["categorie"]).strip().upper()
    if not donnees.categorie_existe(db, categorie):
        raise ErreurMetier(f"La catégorie {categorie} n'existe pas.")
    return {"id_produit": id_produit, "libelle": str(produit["libelle"]).strip(),
            "categorie": categorie, "prix": prix, "stock": stock}


def ajouter_produit(db, produit):
    propre = valider_produit(db, produit)
    donnees.inserer_produit(db, propre)
    return propre


def modifier_stock(db, id_produit, nouveau_stock):
    if not isinstance(nouveau_stock, int) or nouveau_stock < 0:
        raise ErreurMetier("Le stock doit être un entier positif ou nul.")
    if not donnees.changer_stock(db, id_produit, nouveau_stock):
        raise ErreurMetier(f"Produit {id_produit} introuvable.")


# ---------- Commandes ----------
def prochain_id_commande(db):
    # shortcut: suppose des identifiants CMD sur 3 chiffres (tri alphabétique),
    # passer à un compteur dédié au-delà de CMD999.
    dernier = donnees.dernier_id_commande(db)
    numero = int(dernier[3:]) + 1 if dernier else 1
    return f"CMD{numero:03d}"


def creer_commande(db, id_client, demandes):
    """Crée une commande en_attente pour un client existant.

    demandes : liste de (id_produit, quantite).
    Règle de stock : le stock est retiré dès la création (réservation).
    """
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

    # 1) Tout vérifier avant de modifier quoi que ce soit
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

    # 2) Retirer le stock (tout a été vérifié à l'étape 1).
    # Limite : sans transaction, une coupure ici laisserait un stock retiré sans commande.
    for ligne in lignes:
        donnees.retirer_stock(db, ligne["id_produit"], ligne["quantite"])

    # 3) Enregistrer la commande avec un total calculé à partir des lignes
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
    return round(sum(l["quantite"] * l["prix_unitaire"] for l in lignes), 2)


def changer_statut(db, id_commande, nouveau_statut):
    """Applique une transition autorisée ; une annulation remet les produits en stock."""
    commande = donnees.trouver_commande(db, id_commande)
    if not commande:
        raise ErreurMetier(f"Commande {id_commande} inexistante.")
    if nouveau_statut not in STATUTS:
        raise ErreurMetier(f"Statut inconnu. Statuts autorisés : {', '.join(STATUTS)}.")
    actuel = commande["statut"]
    if nouveau_statut not in TRANSITIONS[actuel]:
        raise ErreurMetier(f"Passage de {actuel} à {nouveau_statut} interdit.")
    if nouveau_statut == "annulee":
        for ligne in commande["lignes"]:
            donnees.remettre_stock(db, ligne["id_produit"], ligne["quantite"])
    donnees.changer_statut(db, id_commande, nouveau_statut)
