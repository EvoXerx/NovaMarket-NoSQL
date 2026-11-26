import analyses
import donnees
import metier
from connexion import connecter
from metier import ErreurMetier


# Demande un entier à l'utilisateur et signale une erreur claire si la saisie est invalide.
def saisir_entier(message):
    texte = input(message).strip()
    try:
        return int(texte)
    except ValueError:
        raise ErreurMetier(f"« {texte} » n'est pas un nombre entier.")


# Affiche les informations principales d'un produit sur une seule ligne.
def afficher_produit(p):
    print(f"  {p['id_produit']}  {p['libelle']:<30} {p['categorie']:<7}"
          f"{p['prix']:>9.2f} €   stock : {p['stock']}")


# Récupère et affiche tous les produits.
def action_afficher_produits(db):
    print(f"\n  {'ID':<6}{'Libellé':<31}{'Cat.':<7}{'Prix':>10}")
    for p in donnees.lister_produits(db):
        afficher_produit(p)


# Cherche d'abord par identifiant, puis par mot-clé si aucun identifiant ne correspond.
def action_rechercher_produit(db):
    terme = input("Identifiant (ex. P012) ou mot-clé : ").strip()
    if not terme:
        raise ErreurMetier("Saisie vide.")

    produit = donnees.trouver_produit(db, terme.upper())
    resultats = [produit] if produit else donnees.chercher_produits_mot_cle(db, terme)

    if not resultats:
        print("Aucun produit trouvé.")
    for p in resultats:
        afficher_produit(p)


# Demande les informations du nouveau produit, puis délègue sa validation à la couche métier.
def action_ajouter_produit(db):
    codes = [c["code"] for c in donnees.lister_categories(db)]
    produit = {
        "id_produit": input("Identifiant (ex. P031) : "),
        "libelle": input("Libellé : "),
        "categorie": input(f"Catégorie ({', '.join(codes)}) : "),
        # Accepte une virgule comme séparateur décimal et la convertit en point.
        "prix": input("Prix unitaire en euros : ").replace(",", "."),
        "stock": input("Stock initial : "),
    }

    ajoute = metier.ajouter_produit(db, produit)
    print("Produit ajouté :")
    afficher_produit(ajoute)


# Modifie le stock du produit choisi, puis affiche sa nouvelle valeur.
def action_modifier_stock(db):
    id_produit = input("Identifiant du produit : ").strip().upper()
    metier.modifier_stock(db, id_produit, saisir_entier("Nouveau stock : "))
    afficher_produit(donnees.trouver_produit(db, id_produit))


# Recueille un client et les produits demandés, puis crée la commande.
def action_creer_commande(db):
    id_client = input("Identifiant du client (ex. C001) : ").strip().upper()
    demandes = []

    # Une saisie de produit vide termine la saisie des lignes de commande.
    print("Saisir les lignes ; identifiant produit vide pour terminer.")
    while True:
        id_produit = input("  Produit : ").strip().upper()
        if not id_produit:
            break
        demandes.append((id_produit, saisir_entier("  Quantité : ")))

    # La couche métier vérifie le client, les produits et les stocks avant l'enregistrement.
    commande = metier.creer_commande(db, id_client, demandes)
    print(f"Commande {commande['id_commande']} créée, total {commande['total']:.2f} €")
    for l in commande["lignes"]:
        print(f"  {l['quantite']} x {l['libelle']} à {l['prix_unitaire']:.2f} €")


# Vérifie le client, puis affiche ses commandes et leur résumé.
def action_commandes_client(db):
    id_client = input("Identifiant du client : ").strip().upper()
    client = donnees.trouver_client(db, id_client)
    if not client:
        raise ErreurMetier(f"Client {id_client} inexistant.")

    commandes = donnees.commandes_du_client(db, id_client)
    print(f"{client['prenom']} {client['nom']} ({client['ville']}) : "
          f"{len(commandes)} commande(s)")
    for c in commandes:
        print(f"  {c['id_commande']}  {c['date_commande']:%d/%m/%Y}  "
              f"{c['statut']:<11}{c['total']:>10.2f} €  "
              f"({len(c['lignes'])} ligne(s))")


# Demande un nouveau statut, le fait valider et afficher par la couche métier.
def action_changer_statut(db):
    id_commande = input("Identifiant de la commande (ex. CMD045) : ").strip().upper()
    statut = input(f"Nouveau statut ({', '.join(metier.STATUTS)}) : ").strip().lower()
    metier.changer_statut(db, id_commande, statut)
    c = donnees.trouver_commande(db, id_commande)
    print(f"Commande {c['id_commande']} : statut {c['statut']}")


def afficher_menu():
    print("\n===== NovaMarket =====")
    print("1. Afficher les produits")
    print("2. Rechercher un produit")
    print("3. Ajouter un produit")
    print("4. Modifier le stock d'un produit")
    print("5. Créer une commande")
    print("6. Afficher les commandes d'un client")
    print("7. Changer le statut d'une commande")
    print("8. Résumé statistique des ventes")
    print("0. Quitter")


def main():
    client, db = connecter()
    if db is None:
        print("Vérifiez que le service MongoDB est démarré, puis relancez.")
        return

    print(f"Connecté à la base {db.name}.")
    try:
        while True:
            afficher_menu()
            choix = input("Votre choix : ").strip()

            try:
                if choix == "0":
                    break
                elif choix == "1":
                    action_afficher_produits(db)
                elif choix == "2":
                    action_rechercher_produit(db)
                elif choix == "3":
                    action_ajouter_produit(db)
                elif choix == "4":
                    action_modifier_stock(db)
                elif choix == "5":
                    action_creer_commande(db)
                elif choix == "6":
                    action_commandes_client(db)
                elif choix == "7":
                    action_changer_statut(db)
                elif choix == "8":
                    analyses.afficher_tout(db)
                else:
                    print("Choix invalide.")
            except ErreurMetier as erreur:
                # Affiche les erreurs de saisie ou de règle métier sans arrêter le menu.
                print("Refusé :", erreur)
    except (KeyboardInterrupt, EOFError):
        print()
    finally:
        client.close()  # Ferme proprement la connexion, même en cas d'interruption.
        print("Connexion fermée. Au revoir.")


if __name__ == "__main__":
    main()