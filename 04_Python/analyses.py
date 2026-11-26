"""Partie E : les 8 indicateurs commerciaux (pipelines d'agrégation).

Règle de statut : le chiffre d'affaires (CA) ne compte que les commandes
payee, expediee et livree. Une commande en_attente n'est pas encore payée,
une commande annulee ne rapporte rien.

Lancement seul : python analyses.py (affiche les 8 indicateurs)
"""
from metier import SEUIL_ALERTE_STOCK, STATUTS_CA

FILTRE_CA = {"$match": {"statut": {"$in": STATUTS_CA}}}


# 31. Chiffre d'affaires total (en euros)
def ca_total(db):
    pipeline = [FILTRE_CA,
                {"$group": {"_id": None, "ca": {"$sum": "$total"}, "nb": {"$sum": 1}}}]
    resultat = list(db.commandes.aggregate(pipeline))
    return resultat[0] if resultat else {"ca": 0, "nb": 0}


# 32. Chiffre d'affaires par catégorie (somme quantité x prix des lignes)
def ca_par_categorie(db):
    pipeline = [
        FILTRE_CA,
        {"$unwind": "$lignes"},
        {"$group": {"_id": "$lignes.categorie",
                    "ca": {"$sum": {"$multiply": ["$lignes.quantite", "$lignes.prix_unitaire"]}}}},
        {"$sort": {"ca": -1}},
    ]
    return list(db.commandes.aggregate(pipeline))


# 33. Nombre de commandes par client (toutes les commandes, clients sans commande compris)
def commandes_par_client(db):
    pipeline = [{"$group": {"_id": "$id_client", "nb": {"$sum": 1}}}]
    nb_par_client = {r["_id"]: r["nb"] for r in db.commandes.aggregate(pipeline)}
    resultat = []
    for client in db.clients.find({}, {"_id": 0, "id_client": 1, "nom": 1, "prenom": 1}).sort("id_client", 1):
        client["nb"] = nb_par_client.get(client["id_client"], 0)  # 0 si aucune commande
        resultat.append(client)
    return resultat


# 34. Panier moyen (montant moyen d'une commande prise en compte dans le CA)
def panier_moyen(db):
    pipeline = [FILTRE_CA, {"$group": {"_id": None, "moyen": {"$avg": "$total"}}}]
    resultat = list(db.commandes.aggregate(pipeline))
    return resultat[0]["moyen"] if resultat else 0


# 35. Cinq produits les plus vendus en quantité (unités, commandes du CA)
def top5_quantites(db):
    pipeline = [
        FILTRE_CA,
        {"$unwind": "$lignes"},
        {"$group": {"_id": "$lignes.id_produit", "libelle": {"$first": "$lignes.libelle"},
                    "quantite": {"$sum": "$lignes.quantite"}}},
        {"$sort": {"quantite": -1, "_id": 1}},
        {"$limit": 5},
    ]
    return list(db.commandes.aggregate(pipeline))


# 36. Produits sous le seuil de stock critique
def stock_critique(db):
    return list(db.produits.find({"stock": {"$lt": SEUIL_ALERTE_STOCK}},
                                 {"_id": 0, "id_produit": 1, "libelle": 1, "stock": 1})
                .sort("stock", 1))


# 37. Répartition des commandes par statut (toutes les commandes)
def repartition_statuts(db):
    pipeline = [{"$group": {"_id": "$statut", "nb": {"$sum": 1}}}, {"$sort": {"nb": -1}}]
    return list(db.commandes.aggregate(pipeline))


# 38. Évolution mensuelle du chiffre d'affaires
def ca_mensuel(db):
    pipeline = [
        FILTRE_CA,
        {"$group": {"_id": {"$dateToString": {"format": "%Y-%m", "date": "$date_commande"}},
                    "ca": {"$sum": "$total"}, "nb": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ]
    return list(db.commandes.aggregate(pipeline))


def euros(montant):
    return f"{montant:>12,.2f} €".replace(",", " ")


def afficher_tout(db):
    t = ca_total(db)
    print("\n31. Chiffre d'affaires total (payee + expediee + livree)")
    print(f"    {euros(t['ca'])} sur {t['nb']} commandes")

    print("\n32. Chiffre d'affaires par catégorie")
    for r in ca_par_categorie(db):
        print(f"    {r['_id']:<8}{euros(r['ca'])}")

    print("\n33. Nombre de commandes par client")
    for c in commandes_par_client(db):
        nom_complet = c['prenom'] + ' ' + c['nom']
        print(f"    {c['id_client']} {nom_complet:<20} {c['nb']} commande(s)")

    print("\n34. Panier moyen")
    print(f"    {euros(panier_moyen(db))} par commande")

    print("\n35. Top 5 des produits vendus (en unités)")
    for r in top5_quantites(db):
        print(f"    {r['_id']} {r['libelle']:<30} {r['quantite']} unités")

    print(f"\n36. Produits sous le seuil critique (stock < {SEUIL_ALERTE_STOCK} unités)")
    for p in stock_critique(db):
        print(f"    {p['id_produit']} {p['libelle']:<30} stock {p['stock']}")

    print("\n37. Répartition des commandes par statut")
    for r in repartition_statuts(db):
        print(f"    {r['_id']:<11} {r['nb']} commande(s)")

    print("\n38. Chiffre d'affaires mensuel")
    for r in ca_mensuel(db):
        print(f"    {r['_id']} {euros(r['ca'])} ({r['nb']} commandes)")


if __name__ == "__main__":
    from connexion import connecter
    client, db = connecter()
    if db is not None:
        afficher_tout(db)
        client.close()
