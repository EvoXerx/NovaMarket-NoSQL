import re

#ASCENDING et DESCENDING sont des constantes pour trier les résultats d'une requête
from pymongo import ASCENDING, DESCENDING

# evite de devoir écrire {"_id": 0}
SANS_ID = {"_id": 0}

# pas grand chose a expliquer ici juste les fonctions attendent la connexion à la base de données (db) et font des requêtes sur les collections

# categorie CRUD
def categorie_existe(db, code):
    return db.categories.count_documents({"code": code}) == 1


def lister_categories(db):
    return list(db.categories.find({}, SANS_ID).sort("code", ASCENDING))


def trouver_client(db, id_client):
    return db.clients.find_one({"id_client": id_client}, SANS_ID)


def lister_clients(db):
    return list(db.clients.find({}, SANS_ID).sort("id_client", ASCENDING))


# produit CRUD
def lister_produits(db):
    return list(db.produits.find({}, SANS_ID).sort("id_produit", ASCENDING))


def trouver_produit(db, id_produit):
    return db.produits.find_one({"id_produit": id_produit}, SANS_ID)


def chercher_produits_mot_cle(db, mot_cle):
    # re.escape : un caractère spécial saisi (ex. "+") est cherché tel quel
    filtre = {"libelle": {"$regex": re.escape(mot_cle), "$options": "i"}}
    return list(db.produits.find(filtre, SANS_ID).sort("id_produit", ASCENDING))


def inserer_produit(db, produit):
    db.produits.insert_one(dict(produit))


# commandes CRUD
def changer_stock(db, id_produit, nouveau_stock):
    resultat = db.produits.update_one({"id_produit": id_produit},
                                      {"$set": {"stock": nouveau_stock}})
    return resultat.matched_count == 1


def retirer_stock(db, id_produit, quantite):
    db.produits.update_one({"id_produit": id_produit}, {"$inc": {"stock": -quantite}})


def remettre_stock(db, id_produit, quantite):
    db.produits.update_one({"id_produit": id_produit}, {"$inc": {"stock": quantite}})


def produits_sous_seuil(db, seuil):
    return list(db.produits.find({"stock": {"$lt": seuil}}, SANS_ID).sort("stock", ASCENDING))


def commandes_du_client(db, id_client):
    return list(db.commandes.find({"id_client": id_client}, SANS_ID)
                .sort("date_commande", DESCENDING))

#commande CRUD

def trouver_commande(db, id_commande):
    return db.commandes.find_one({"id_commande": id_commande}, SANS_ID)


def dernier_id_commande(db):
    for commande in db.commandes.find({}, {"_id": 0, "id_commande": 1}).sort("id_commande", -1).limit(1):
        return commande["id_commande"]
    return None  

def inserer_commande(db, commande):
    db.commandes.insert_one(dict(commande))


def changer_statut(db, id_commande, statut):
    db.commandes.update_one({"id_commande": id_commande}, {"$set": {"statut": statut}})
