from bson import json_util

import analyses
import donnees
import metier
from charger_donnees import COLLECTIONS, DOSSIER_DONNEES, charger
from connexion import connecter
from metier import ErreurMetier

resultats = []


# Enregistre et affiche le résultat d'une vérification.
def verifier(numero, description, condition):
    resultats.append(condition)
    print(f"[{'OK' if condition else 'ECHEC'}] {numero}. {description}")


# Vérifie qu'une action est bien refusée avec une erreur métier.
def refuse(fonction, *args):
    try:
        fonction(*args)
    except ErreurMetier as erreur:
        print("       message :", erreur)
        return True
    return False


def main():
    # Les tests utilisent une base séparée pour ne pas modifier NovaMarket.
    client, db = connecter(nom_base="NovaMarketTest")
    verifier(39, "connexion au serveur local réussie", db is not None)
    if db is None:
        return

    # Vérifie aussi qu'une connexion impossible est détectée.
    _, db_ko = connecter(uri="mongodb://localhost:27999/", delai_ms=1000)
    verifier(39, "connexion impossible détectée sans plantage", db_ko is None)

    comptes = charger(db)

    # 40. Recherche d'un produit existant et d'un produit absent.
    verifier(40, "produit P012 trouvé", donnees.trouver_produit(db, "P012") is not None)
    verifier(40, "produit P999 introuvable", donnees.trouver_produit(db, "P999") is None)

    # 41. Ajout d'un produit valide, puis refus d'un prix négatif.
    valide = {"id_produit": "P900", "libelle": "Produit de test", "categorie": "AUDIO",
              "prix": "59.90", "stock": "10"}
    metier.ajouter_produit(db, valide)
    verifier(41, "produit valide ajouté", donnees.trouver_produit(db, "P900") is not None)

    negatif = dict(valide, id_produit="P901", prix="-5")
    verifier(41, "prix négatif refusé", refuse(metier.ajouter_produit, db, negatif))

    # 42 et 44. Crée une commande et vérifie son total et la mise à jour des stocks.
    avant_p022 = donnees.trouver_produit(db, "P022")
    avant_p029 = donnees.trouver_produit(db, "P029")
    commande = metier.creer_commande(db, "C003", [("P022", 2), ("P029", 3)])
    verifier(42, f"commande {commande['id_commande']} créée avec stock suffisant", True)

    attendu = round(2 * avant_p022["prix"] + 3 * avant_p029["prix"], 2)
    enregistree = donnees.trouver_commande(db, commande["id_commande"])
    verifier(44, f"total enregistré {enregistree['total']} = {attendu} attendu",
             enregistree["total"] == attendu)
    verifier(44, "stocks diminués de 2 et 3",
             donnees.trouver_produit(db, "P022")["stock"] == avant_p022["stock"] - 2
             and donnees.trouver_produit(db, "P029")["stock"] == avant_p029["stock"] - 3)

    # 42. Une quantité supérieure au stock doit être refusée sans modifier le stock.
    stock_p004 = donnees.trouver_produit(db, "P004")["stock"]
    verifier(42, "quantité supérieure au stock refusée",
             refuse(metier.creer_commande, db, "C003", [("P022", 1), ("P004", stock_p004 + 1)]))
    verifier(42, "aucun stock modifié après le refus",
             donnees.trouver_produit(db, "P022")["stock"] == avant_p022["stock"] - 2)

    # 43. Une commande pour un client inexistant doit être refusée.
    verifier(43, "commande pour le client C999 refusée",
             refuse(metier.creer_commande, db, "C999", [("P022", 1)]))

    # 45. Recharge les données initiales pour vérifier le contenu des collections.
    charger(db)
    for nom, champ in COLLECTIONS.items():
        dans_fichier = len(json_util.loads((DOSSIER_DONNEES / f"{nom}.json").read_text("utf-8")))
        distincts = len(db[nom].distinct(champ))
        verifier(45, f"{nom} : {comptes[nom]} documents, {distincts} identifiants distincts",
                 comptes[nom] == dans_fichier == distincts)

    # Vérifie que l'index unique empêche les identifiants clients en double.
    verifier(45, "doublon d'identifiant client refusé par l'index unique",
             doublon_refuse(db))

    # 46. Compare deux résultats MongoDB avec des calculs faits depuis les fichiers JSON.
    commandes = json_util.loads((DOSSIER_DONNEES / "commandes.json").read_text("utf-8"))
    ca_python = round(sum(c["total"] for c in commandes if c["statut"] in metier.STATUTS_CA), 2)
    ca_mongo = round(analyses.ca_total(db)["ca"], 2)
    verifier(46, f"CA total : {ca_mongo} (MongoDB) = {ca_python} (Python)", ca_mongo == ca_python)

    statuts_python = {}
    for c in commandes:
        statuts_python[c["statut"]] = statuts_python.get(c["statut"], 0) + 1

    statuts_mongo = {r["_id"]: r["nb"] for r in analyses.repartition_statuts(db)}
    verifier(46, f"répartition par statut identique {statuts_mongo}",
             statuts_mongo == statuts_python)

    # Supprime la base de test et ferme la connexion.
    db.client.drop_database("NovaMarketTest")
    client.close()
    print(f"\n{sum(resultats)}/{len(resultats)} vérifications réussies.")


# Tente d'insérer un client déjà présent : l'index unique doit refuser le doublon.
def doublon_refuse(db):
    from pymongo.errors import DuplicateKeyError

    try:
        db.clients.insert_one({"id_client": "C001", "nom": "Doublon"})
    except DuplicateKeyError:
        return True
    return False


if __name__ == "__main__":
    main()