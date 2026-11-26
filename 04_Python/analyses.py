from metier import SEUIL_ALERTE_STOCK, STATUTS_CA

# STATUTS_CA contient les statuts payee, expediee et livree.
FILTRE_CA = {"$match": {"statut": {"$in": STATUTS_CA}}}


# 31. Chiffre d'affaires total, en euros
def ca_total(db):
    pipeline = [
        FILTRE_CA,
        # On additionne le total de chaque commande retenue et on les compte.
        {"$group": {"_id": None, "ca": {"$sum": "$total"}, "nb": {"$sum": 1}}},
    ]
    resultat = list(db.commandes.aggregate(pipeline))

    # Si aucune commande ne correspond au filtre, le CA et le nombre de commandes valent 0.
    return resultat[0] if resultat else {"ca": 0, "nb": 0}


# 32. Chiffre d'affaires par catégorie, calculé à partir des lignes de commande
def ca_par_categorie(db):
    pipeline = [
        FILTRE_CA,
        # Une commande peut contenir plusieurs lignes : on traite chaque ligne séparément.
        {"$unwind": "$lignes"},
        # Le CA d'une ligne est sa quantité multipliée par son prix unitaire.
        {"$group": {
            "_id": "$lignes.categorie",
            "ca": {"$sum": {
                "$multiply": ["$lignes.quantite", "$lignes.prix_unitaire"]
            }},
        }},
        # On affiche d'abord les catégories qui ont le plus grand CA.
        {"$sort": {"ca": -1}},
    ]
    return list(db.commandes.aggregate(pipeline))


# 33. Nombre de commandes par client, y compris les clients sans commande
def commandes_par_client(db):
    # On compte d'abord les commandes de chaque client.
    pipeline = [
        {"$group": {"_id": "$id_client", "nb": {"$sum": 1}}},
    ]
    nb_par_client = {
        resultat["_id"]: resultat["nb"]
        for resultat in db.commandes.aggregate(pipeline)
    }

    # On parcourt tous les clients pour afficher aussi ceux qui ont zéro commande.
    resultat = []
    clients = db.clients.find(
        {},
        {"_id": 0, "id_client": 1, "nom": 1, "prenom": 1},
    ).sort("id_client", 1)

    for client in clients:
        # Si l'identifiant du client n'est pas dans le comptage, il a zéro commande.
        client["nb"] = nb_par_client.get(client["id_client"], 0)
        resultat.append(client)

    return resultat


# 34. Panier moyen des commandes retenues dans le calcul du chiffre d'affaires
def panier_moyen(db):
    pipeline = [
        FILTRE_CA,
        # La moyenne est calculée sur le total des commandes, pas sur les lignes.
        {"$group": {"_id": None, "moyen": {"$avg": "$total"}}},
    ]
    resultat = list(db.commandes.aggregate(pipeline))

    # Si aucune commande ne correspond au filtre, on renvoie 0.
    return resultat[0]["moyen"] if resultat else 0


# 35. Cinq produits les plus vendus en quantité
def top5_quantites(db):
    pipeline = [
        FILTRE_CA,
        # On sépare les lignes pour compter les quantités de chaque produit.
        {"$unwind": "$lignes"},
        {"$group": {
            "_id": "$lignes.id_produit",
            "libelle": {"$first": "$lignes.libelle"},
            "quantite": {"$sum": "$lignes.quantite"},
        }},
        # Le tri secondaire par identifiant rend le résultat stable en cas d'égalité.
        {"$sort": {"quantite": -1, "_id": 1}},
        {"$limit": 5},
    ]
    return list(db.commandes.aggregate(pipeline))


# 36. Produits dont le stock est inférieur au seuil critique
def stock_critique(db):
    # Une recherche suffit ici : il n'est pas nécessaire de faire une agrégation.
    return list(
        db.produits.find(
            {"stock": {"$lt": SEUIL_ALERTE_STOCK}},
            {"_id": 0, "id_produit": 1, "libelle": 1, "stock": 1},
        ).sort("stock", 1)
    )


# 37. Nombre de commandes pour chaque statut, sans exclure de statut
def repartition_statuts(db):
    pipeline = [
        # Contrairement aux indicateurs de CA, on compte ici toutes les commandes.
        {"$group": {"_id": "$statut", "nb": {"$sum": 1}}},
        {"$sort": {"nb": -1}},
    ]
    return list(db.commandes.aggregate(pipeline))


# 38. Évolution mensuelle du chiffre d'affaires
def ca_mensuel(db):
    pipeline = [
        FILTRE_CA,
        # On regroupe les commandes par mois au format année-mois.
        {"$group": {
            "_id": {
                "$dateToString": {
                    "format": "%Y-%m",
                    "date": "$date_commande",
                }
            },
            "ca": {"$sum": "$total"},
            "nb": {"$sum": 1},
        }},
        # Le tri chronologique est possible car la date est au format YYYY-MM.
        {"$sort": {"_id": 1}},
    ]
    return list(db.commandes.aggregate(pipeline))


# Formate un montant avec deux décimales et le symbole euro.
def euros(montant):
    return f"{montant:>12,.2f} €".replace(",", " ")


def afficher_tout(db):
    total = ca_total(db)
    print("\n31. Chiffre d'affaires total (payee + expediee + livree)")
    print(f"    {euros(total['ca'])} sur {total['nb']} commandes")

    print("\n32. Chiffre d'affaires par catégorie")
    for resultat in ca_par_categorie(db):
        print(f"    {resultat['_id']:<8}{euros(resultat['ca'])}")

    print("\n33. Nombre de commandes par client")
    for client in commandes_par_client(db):
        nom_complet = client["prenom"] + " " + client["nom"]
        print(f"    {client['id_client']} {nom_complet:<20} "
              f"{client['nb']} commande(s)")

    print("\n34. Panier moyen")
    print(f"    {euros(panier_moyen(db))} par commande")

    print("\n35. Top 5 des produits vendus (en unités)")
    for resultat in top5_quantites(db):
        print(f"    {resultat['_id']} {resultat['libelle']:<30} "
              f"{resultat['quantite']} unités")

    print(f"\n36. Produits sous le seuil critique "
          f"(stock < {SEUIL_ALERTE_STOCK} unités)")
    for produit in stock_critique(db):
        print(f"    {produit['id_produit']} {produit['libelle']:<30} "
              f"stock {produit['stock']}")

    print("\n37. Répartition des commandes par statut")
    for resultat in repartition_statuts(db):
        print(f"    {resultat['_id']:<11} {resultat['nb']} commande(s)")

    print("\n38. Chiffre d'affaires mensuel")
    for resultat in ca_mensuel(db):
        print(f"    {resultat['_id']} {euros(resultat['ca'])} "
              f"({resultat['nb']} commandes)")


if __name__ == "__main__":
    from connexion import connecter

    client, db = connecter()
    if db is not None:
        afficher_tout(db)
        client.close()