from pymongo import MongoClient

# Étape 1 : installer et se connecter
client = MongoClient("mongodb://localhost:27017/")
client.admin.command("ping")
db = client["LibrairieTP"]
livres = db["livres"]
print("Connexion réussie !")

# La base sera effectivement créée lors de la première insertion.
documents = [
    {"isbn": "L001", "titre": "Python débutant", "auteur": "Martin", "prix": 24, "stock": 8, "categorie": "Informatique"},
    {"isbn": "L002", "titre": "MongoDB pratique", "auteur": "Sara", "prix": 32, "stock": 5, "categorie": "Informatique"},
    {"isbn": "L003", "titre": "Économie facile", "auteur": "Ali", "prix": 19, "stock": 12, "categorie": "Économie"},
    {"isbn": "L004", "titre": "Finance moderne", "auteur": "Lina", "prix": 38, "stock": 3, "categorie": "Finance"},
    {"isbn": "L005", "titre": "Statistiques", "auteur": "Martin", "prix": 27, "stock": 7, "categorie": "Économie"},
    {"isbn": "L006", "titre": "Data Science", "auteur": "Sara", "prix": 45, "stock": 4, "categorie": "Informatique"},
]
livres.delete_many({})  # Remise à zéro uniquement pour ce TP
livres.insert_many(documents)
print("Livres :", livres.count_documents({}))

# Étape 3 : lire, filtrer et trier
print("\n--- Tous les livres")
for livre in livres.find({}, {"_id": 0}):
    print(livre)
print("\n--- Livres à moins de 30 euros")
for livre in livres.find({"prix": {"$lt": 30}}, {"_id": 0, "titre": 1, "prix": 1}):
    print(livre)
print("\n--- Trois livres les plus chers")
for livre in livres.find({}, {"_id": 0, "titre": 1, "prix": 1}).sort("prix", -1).limit(3):
    print(livre)
print("\n--- À faire : livres de catégorie Informatique")
for livre in livres.find({"categorie": "Informatique"}, {"_id": 0, "titre": 1}):
    print(livre)

# Étape 4 : ajouter et modifier des livres
livres.insert_one({
    "isbn": "L007", "titre": "Analyse de données",
    "auteur": "Nora", "prix": 29, "stock": 6, "categorie": "Informatique"
})
livres.update_one({"isbn": "L002"}, {"$inc": {"stock": -1}})
livres.update_many({"categorie": "Finance"}, {"$inc": {"prix": 2}})
print("\n--- Vérification L002 :", livres.find_one({"isbn": "L002"}, {"_id": 0}))
livres.update_one({"isbn": "L004"}, {"$set": {"stock": 10}})  # À faire : stock de L004 à 10
print("--- Vérification L004 :", livres.find_one({"isbn": "L004"}, {"_id": 0}))

# Étape 5 : première agrégation
print("\n--- Nombre de livres et prix moyen par catégorie")
pipeline = [
    {"$group": {"_id": "$categorie", "nombreLivres": {"$sum": 1}, "prixMoyen": {"$avg": "$prix"}}},
    {"$sort": {"prixMoyen": -1}}
]
for resultat in livres.aggregate(pipeline):
    print(resultat)
print("\n--- À faire : prix maximal par catégorie")
pipeline = [{"$group": {"_id": "$categorie", "prixMax": {"$max": "$prix"}}}]
for resultat in livres.aggregate(pipeline):
    print(resultat)

# Étape 6 : exercices autonomes
print("\n--- 1. Stock inférieur à 6")
for livre in livres.find({"stock": {"$lt": 6}}, {"_id": 0}):
    print(livre)
print("\n--- 2. Titre et auteur, sans _id")
for livre in livres.find({}, {"_id": 0, "titre": 1, "auteur": 1}):
    print(livre)
print("\n--- 3. Prix entre 20 et 40 euros inclus")
filtre = {"prix": {"$gte": 20, "$lte": 40}}
for livre in livres.find(filtre, {"_id": 0, "titre": 1, "prix": 1}):
    print(livre)
print("\n--- 4. Livres Informatique :", livres.count_documents({"categorie": "Informatique"}))
print("\n--- 5. Stock croissant")
for livre in livres.find({}, {"_id": 0, "titre": 1, "stock": 1}).sort("stock", 1):
    print(livre)
print("\n--- 6. Deux livres les moins chers")
for livre in livres.find({}, {"_id": 0, "titre": 1, "prix": 1}).sort("prix", 1).limit(2):
    print(livre)
livres.update_one({"isbn": "L001"}, {"$inc": {"stock": 1}})
print("\n--- 7. L001 :", livres.find_one({"isbn": "L001"}, {"_id": 0}))
print("\n--- 8. Stock total par catégorie")
pipeline = [{"$group": {"_id": "$categorie", "stockTotal": {"$sum": "$stock"}}}, {"$sort": {"_id": 1}}]
for resultat in livres.aggregate(pipeline):
    print(resultat)
print("\n--- BONUS : valeur du stock > 150 euros")
pipeline = [
    {"$project": {"_id": 0, "titre": 1, "prix": 1, "stock": 1,
                  "valeurStock": {"$multiply": ["$prix", "$stock"]}}},
    {"$match": {"valeurStock": {"$gt": 150}}},
    {"$sort": {"valeurStock": -1}}
]
for resultat in livres.aggregate(pipeline):
    print(resultat)

# Étape 7 : vérification et conclusion
print("\nBase :", db.name)
print("Collections :", db.list_collection_names())
print("Documents :", livres.count_documents({}))
client.close()
