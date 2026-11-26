"""Connexion au serveur MongoDB (fonction 22).

L'adresse du serveur n'est pas écrite en dur avec un mot de passe :
elle est lue dans la variable d'environnement MONGO_URI.
Sans variable, on utilise le serveur local sans authentification.
"""
import os

from pymongo import MongoClient
from pymongo.errors import PyMongoError

URI_PAR_DEFAUT = "mongodb://localhost:27017/"
BASE_PAR_DEFAUT = "NovaMarket"


def connecter(uri=None, nom_base=None, delai_ms=3000):
    uri = uri or os.environ.get("MONGO_URI", URI_PAR_DEFAUT)
    nom_base = nom_base or os.environ.get("NOVAMARKET_DB", BASE_PAR_DEFAUT)
    # connection a la base de données ajout d'un timeout au cas ou ne serveur ne répond pas
    client = MongoClient(uri, serverSelectionTimeoutMS=delai_ms)
    try:
        client.admin.command("ping")
    except PyMongoError as erreur:
        print("Connexion impossible au serveur MongoDB :", erreur.__class__.__name__)
        client.close()
        return None, None
    return client, client[nom_base]
