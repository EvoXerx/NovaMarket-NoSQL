# NovaMarket : gestion et analyse d'une plateforme e-commerce (MongoDB, PyMongo)

| Dossier | Contenu |
|---|---|
| `01_Conception.docx` / `.md` | analyse, dictionnaire de données, schéma, règles métier |
| `02_Donnees/` | fichiers JSON et procédure de chargement |
| `03_Mongosh/requetes.js` | les 15 requêtes mongosh |
| `04_Python/` | application console PyMongo, analyses, tests (voir son README) |
| `05_Rapport.docx` / `.md` | résultats, tests, limites, captures |
| `captures/` | captures d'écran et scripts qui les produisent |
| `tp_librairie.py` | TP PyMongo Librairie (exercice préparatoire) |

Démarrage rapide (PowerShell, MongoDB démarré sur `localhost:27017`) :
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r 04_Python\requirements.txt
cd 04_Python
..\.venv\Scripts\python.exe charger_donnees.py
..\.venv\Scripts\python.exe app.py
```
