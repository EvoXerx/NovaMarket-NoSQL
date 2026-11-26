// =====================================================================
// NovaMarket, partie C : les 15 requêtes mongosh (numérotées 7 à 21 comme le sujet)
//
// Exécution :
//   mongosh --file requetes.js            (si mongosh est installé)
//   ou coller les blocs un par un dans l'onglet _MONGOSH de Compass.
// Prérequis : jeu chargé avec  python 04_Python/charger_donnees.py
// Les requêtes 16 à 19 modifient la base : relancer charger_donnees.py
// pour revenir au jeu initial.
// =====================================================================

db = db.getSiblingDB("NovaMarket");

// --- 7. Tous les produits, puis seulement nom, prix et catégorie -----
print("\n7a. Tous les produits");
db.produits.find({}, { _id: 0 }).forEach(printjson);

print("\n7b. Nom, prix et catégorie");
db.produits.find({}, { _id: 0, libelle: 1, prix: 1, categorie: 1 }).forEach(printjson);

// --- 8. Produits d'une catégorie choisie (Smartphones) ----------------
print("\n8. Catégorie TEL");
db.produits.find({ categorie: "TEL" }, { _id: 0, libelle: 1, prix: 1 }).forEach(printjson);

// --- 9. Produits à plus de 500 € --------------------------------------
print("\n9. Prix > 500 €");
db.produits.find({ prix: { $gt: 500 } }, { _id: 0, libelle: 1, prix: 1 }).forEach(printjson);

// --- 10. Stock inférieur à 5 unités (seuil d'alerte) ------------------
print("\n10. Stock < 5");
db.produits.find({ stock: { $lt: 5 } }, { _id: 0, id_produit: 1, libelle: 1, stock: 1 })
  .forEach(printjson);

// --- 11. Clients de deux villes choisies ------------------------------
print("\n11. Clients de Lyon ou de Lille");
db.clients.find({ ville: { $in: ["Lyon", "Lille"] } },
  { _id: 0, id_client: 1, nom: 1, prenom: 1, ville: 1 }).forEach(printjson);

// --- 12. Produits triés par prix décroissant --------------------------
print("\n12. Tri par prix décroissant");
db.produits.find({}, { _id: 0, libelle: 1, prix: 1 }).sort({ prix: -1 }).forEach(printjson);

// --- 13. Les cinq produits les plus chers -----------------------------
print("\n13. Top 5 des prix");
db.produits.find({}, { _id: 0, libelle: 1, prix: 1 }).sort({ prix: -1 }).limit(5)
  .forEach(printjson);

// --- 14. Nombre total de clients --------------------------------------
print("\n14. Nombre de clients : " + db.clients.countDocuments({}));

// --- 15. Nombre de commandes par statut -------------------------------
print("\n15. Commandes par statut");
db.commandes.aggregate([
  { $group: { _id: "$statut", nombre: { $sum: 1 } } },
  { $sort: { nombre: -1 } }
]).forEach(printjson);

// --- 16. Insérer un nouveau produit (règles : id unique, catégorie existante,
//         prix > 0, stock >= 0) puis vérifier ----------------------------
print("\n16. Insertion de P031");
db.produits.insertOne({
  id_produit: "P031", libelle: "Souris gaming Pro", categorie: "PERIPH", prix: 59.0, stock: 12
});
printjson(db.produits.findOne({ id_produit: "P031" }, { _id: 0 }));

// --- 17. Modifier le prix d'un produit identifié puis vérifier --------
print("\n17. Nouveau prix de P031");
db.produits.updateOne({ id_produit: "P031" }, { $set: { prix: 54.9 } });
printjson(db.produits.findOne({ id_produit: "P031" }, { _id: 0, libelle: 1, prix: 1 }));

// --- 18. +10 % sur les prix d'une catégorie (AUDIO) puis vérifier -----
print("\n18. AUDIO avant");
db.produits.find({ categorie: "AUDIO" }, { _id: 0, libelle: 1, prix: 1 }).forEach(printjson);
db.produits.updateMany({ categorie: "AUDIO" }, { $mul: { prix: 1.1 } });
print("18. AUDIO après (+10 %)");
db.produits.find({ categorie: "AUDIO" }, { _id: 0, libelle: 1, prix: 1 }).forEach(printjson);

// --- 19. Modifier le statut d'une commande et afficher son nouvel état
print("\n19. CMD049 passe de en_attente à payee");
db.commandes.updateOne({ id_commande: "CMD049" }, { $set: { statut: "payee" } });
printjson(db.commandes.findOne({ id_commande: "CMD049" },
  { _id: 0, id_commande: 1, statut: 1, total: 1 }));

// --- 20. Prix moyen des produits par catégorie ------------------------
print("\n20. Prix moyen par catégorie");
db.produits.aggregate([
  { $group: { _id: "$categorie", prixMoyen: { $avg: "$prix" }, nbProduits: { $sum: 1 } } },
  { $sort: { prixMoyen: -1 } }
]).forEach(printjson);

// --- 21. Catégories dont le prix moyen dépasse 500 € ------------------
// Seuil de 500 € : même limite que la requête 9 (produits « haut de gamme »).
// Il est proche du prix moyen de tout le catalogue (environ 478 €) : les
// catégories retenues sont celles nettement plus chères que la moyenne.
print("\n21. Catégories dont le prix moyen > 500 €");
db.produits.aggregate([
  { $group: { _id: "$categorie", prixMoyen: { $avg: "$prix" } } },
  { $match: { prixMoyen: { $gt: 500 } } },
  { $sort: { prixMoyen: -1 } }
]).forEach(printjson);
