

// Partie C 
//
// Exécution :
// Ouvrir le terminal et exécuter la commande : mongosh --file requetes.js  
// ou executer copier coller dans l'onglet _MONGOSH de Compass.
//
// Prérequis : charger les données dans une base NovaMarket et y avoir importé les collections.


db = db.getSiblingDB("NovaMarket");

  //7. Tous les produits, puis seulement nom, prix et catégorie
  print("\n7a. Tous les produits");
  // on met _id à 0 pour ne pas afficher l'identifiant interne de MongoDB
  db.produits.find({}, { _id: 0 }).forEach(printjson);

print("\n7b. Nom, prix et catégorie");
// on met _id à 0 pour ne pas afficher l'identifiant et on ne sélectionne que les champs libelle, prix et categorie
db.produits.find({}, { _id: 0, libelle: 1, prix: 1, categorie: 1 }).forEach(printjson);

//8. Rechercher les produits appartenant à une catégorie choisie : on choisit ici la catégorie TEL (téléphones)
print("\n8. Catégorie TEL");
// on ajoute l'argulent categorie: "TEL" pour ne sélectionner que les produits de cette catégorie
db.produits.find({ categorie: "TEL" }, { _id: 0, libelle: 1, prix: 1 }).forEach(printjson);

//9.Rechercher les produits dont le prix est supérieur à 500 €.
print("\n9. Prix > 500 €");
// on ajoute l'argulent prix: { $gt: 500 } pour ne sélectionner que les produits dont le prix est supérieur à 500 € ($gt = greater than)
db.produits.find({ prix: { $gt: 500 } }, { _id: 0, libelle: 1, prix: 1 }).forEach(printjson);

//10. Identifier les produits dont le stock est inférieur à 5 unités.
print("\n10. Stock < 5");
// on ajoute l'argulent stock: { $lt: 5 } pour ne sélectionner que les produits dont le stock est inférieur à 5 unités ($lt = less than)
db.produits.find({ stock: { $lt: 5 } }, { _id: 0, id_produit: 1, libelle: 1, stock: 1 })
  .forEach(printjson);

//11. Retrouver les clients appartenant à deux villes choisies (Lyon et Lille)
print("\n11. Clients de Lyon ou de Lille");
// on ajoute l'argulent ville: { $in: ["Lyon", "Lille"] } pour ne sélectionner que les clients dont la ville est soit Lyon soit Lille ($in = in array)
db.clients.find({ ville: { $in: ["Lyon", "Lille"] } },
  { _id: 0, id_client: 1, nom: 1, prenom: 1, ville: 1 }).forEach(printjson);

//12. Trier les produits par prix décroissant.
print("\n12. Tri par prix décroissant");
// on selectionne tout et avec la méthode sort() on trie par prix décroissant (prix: -1)
db.produits.find({}, { _id: 0, libelle: 1, prix: 1 }).sort({ prix: -1 }).forEach(printjson);

//13. Afficher les cinq produits les plus chers.
print("\n13. Top 5 des prix");
// meme concept que la 12 mais a l'inverse on ajoute la méthode limit(5) pour ne selectionner que les 5 premiers produits
db.produits.find({}, { _id: 0, libelle: 1, prix: 1 }).sort({ prix: -1 }).limit(5)
  .forEach(printjson);

//14. Compter le nombre total de clients.
// la méthode countDocuments() permet de compter le nombre de documents dans la collection clients
print("\n14. Nombre de clients : " + db.clients.countDocuments({}));

//15. Compter le nombre de commandes pour chaque statut.
print("\n15. Commandes par statut");
// on agrège les commandes par statut avec la méthode aggregate() et on compte le nombre de commandes pour chaque statut avec $sum: 1, puis on trie par nombre décroissant
db.commandes.aggregate([
  { $group: { _id: "$statut", nombre: { $sum: 1 } } },
  { $sort: { nombre: -1 } }
]).forEach(printjson);

// 16. Insérer un nouveau produit en respectant les règles de conception. 
print("\n16. Insertion de P031");
// on insère un nouveau produit avec la méthode insertOne() et on vérifie avec findOne() que le produit a bien été inséré
// il un id unique (P031), une catégorie existante (PERIPH), un prix > 0 (59.0) et un stock >= 0 (12)
db.produits.insertOne({
  id_produit: "P031", libelle: "Souris gaming Pro", categorie: "PERIPH", prix: 59.0, stock: 12
});
printjson(db.produits.findOne({ id_produit: "P031" }, { _id: 0 }));

// 17. Modifier le prix d’un produit identifié et vérifier la modification.
print("\n17. Nouveau prix de P031");
// on modifie avec updateOne pour une seul ligne et on le cherche par rapport à son id_produit, puis on vérifie avec findOne() que le prix a bien été modifié
db.produits.updateOne({ id_produit: "P031" }, { $set: { prix: 54.9 } });
printjson(db.produits.findOne({ id_produit: "P031" }, { _id: 0, libelle: 1, prix: 1 }));

// 18. augmenter de 10 % le prix des produits d’une catégorie ; vérifier le résultat.
print("\n18. AUDIO avant");
// vérifie le prix des produits de la catégorie AUDIO avant l'augmentation
db.produits.find({ categorie: "AUDIO" }, { _id: 0, libelle: 1, prix: 1 }).forEach(printjson);
// on utilise updateMany pour modifier tous les produits de la catégorie AUDIO et on multiplie le prix par 1.1 pour augmenter de 10 %
db.produits.updateMany({ categorie: "AUDIO" }, { $mul: { prix: 1.1 } });
print("18. AUDIO après (+10 %)");
// vérifie le prix des produits de la catégorie AUDIO après l'augmentation
db.produits.find({ categorie: "AUDIO" }, { _id: 0, libelle: 1, prix: 1 }).forEach(printjson);

// 19. Modifier le statut d’une commande et afficher son nouvel état.
print("\n19. CMD049 passe de en_attente à payee");
// on change le statut avec updateOne et on donne comme nouvelle valeur a la clé statut la valeur "payee", puis on vérifie avec findOne() que le statut a bien été modifié
db.commandes.updateOne({ id_commande: "CMD049" }, { $set: { statut: "payee" } });
printjson(db.commandes.findOne({ id_commande: "CMD049" },
  { _id: 0, id_commande: 1, statut: 1, total: 1 }));

// 20. Calculer le prix moyen des produits par catégorie
print("\n20. Prix moyen par catégorie");
// on agrège les produits par catégorie avec la méthode aggregate() et on calcule le prix moyen avec $avg: "$prix" et le nombre de produits avec $sum: 1
db.produits.aggregate([
  { $group: { _id: "$categorie", prixMoyen: { $avg: "$prix" }, nbProduits: { $sum: 1 } } }
]).forEach(printjson);

// 21. Afficher les catégories dont le prix moyen est supérieur à un seuil défini et justifié
// Seuil de 500 €
// on regroupe les produits par catégorie et on en fait un calcul du prix moyen avec $avg: "$prix"
// puis on filtre avec $match pour ne garder que les catégories dont le prix moyen est supérieur à 500 €,
print("\n21. Catégories dont le prix moyen > 500 €");
db.produits.aggregate([
  { $group: { _id: "$categorie", prixMoyen: { $avg: "$prix" } } },
  { $match: { prixMoyen: { $gt: 500 } } }
]).forEach(printjson);
