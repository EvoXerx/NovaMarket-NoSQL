"""Chargement (et remise à zéro) du jeu de données NovaMarket.

Chaque exécution vide les 4 collections puis réinsère les fichiers JSON :
relancer le script ne crée donc jamais de doublons.

Lancement : python charger_donnees.py
"""
from pathlib import Path

from bson import json_util  # installé avec pymongo, lit les dates {"$date": ...}
from pymongo import ASCENDING

from connexion import connecter

DOSSIER_DONNEES = Path(__file__).resolve().parent.parent / "02_Donnees"

# collection : champ identifiant métier (unique)
COLLECTIONS = {
    "categories": "code",
    "clients": "id_client",
    "produits": "id_produit",
    "commandes": "id_commande",
}


def lire_json(nom):
    texte = (DOSSIER_DONNEES / f"{nom}.json").read_text(encoding="utf-8")
    return json_util.loads(texte)


def charger(db):
    """Vide puis remplit les collections, crée les index uniques. Renvoie les comptes."""
    comptes = {}
    for nom, champ_id in COLLECTIONS.items():
        documents = lire_json(nom)
        db[nom].delete_many({})  # remise à zéro, comme l'étape 2 du TP
        db[nom].insert_many(documents)
        # Index unique : MongoDB refuse un second document avec le même identifiant métier
        db[nom].create_index([(champ_id, ASCENDING)], unique=True)
        comptes[nom] = db[nom].count_documents({})
    return comptes


if __name__ == "__main__":
    client, db = connecter()
    if db is None:
        raise SystemExit(1)
    for nom, nombre in charger(db).items():
        print(f"{nom:<11}: {nombre} documents")
    print("Base :", db.name, "| Collections :", sorted(db.list_collection_names()))
    client.close()
