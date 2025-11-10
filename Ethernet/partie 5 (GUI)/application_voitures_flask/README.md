# Tutoriel Flask - De Python Orienté Objet à API Web

## 📋 Objectif
Transformer le code orienté objet `voitures.py` en une API web avec Flask.

## 🚀 Étapes d'installation

### 1. Installer Flask
```bash
pip install flask
```

### 2. Structure des fichiers
```
/mon_projet
    ├── voitures.py     # Les classes (déjà créé)
    ├── app.py          # L'application Flask
    └── README.md       # Ce fichier
```

### 3. Lancer l'application
```bash
python app.py
```

### 4. Tester dans le navigateur
Ouvrez : http://localhost:5000

## 🎯 Concepts clés du passage Python → Flask

### Avant (Python classique)
```python
# Code impératif
voiture = Voiture("Renault", "Clio", 2023, "Bleu")
conducteur = Conducteur("Marie", "B")
voiture.set_conducteur(conducteur)
voiture.demarrer()
```

### Après (Flask - API Web)
```python
# Routes web
GET /creer-voiture        → crée la voiture
GET /creer-conducteur     → crée le conducteur
GET /associer-conducteur  → lie les deux
GET /demarrer            → démarre la voiture
```

## 📖 Les routes expliquées

| Route | Action | Concept illustré |
|-------|--------|------------------|
| `/creer-voiture` | Crée une voiture | **Composition** : moteur et roues créés automatiquement |
| `/creer-conducteur` | Crée un conducteur | **Agrégation** : objet indépendant |
| `/associer-conducteur` | Lie conducteur et voiture | **Agrégation** : association d'objets existants |
| `/demarrer` | Démarre la voiture | Validation métier (nécessite un conducteur) |
| `/retirer-conducteur` | Retire le conducteur | **Agrégation** : le conducteur continue d'exister |

## 🧪 Scénario de test complet

1. **Créer une voiture** : http://localhost:5000/creer-voiture
2. **Créer un conducteur** : http://localhost:5000/creer-conducteur
3. **Associer le conducteur** : http://localhost:5000/associer-conducteur
4. **Démarrer** : http://localhost:5000/demarrer
5. **Accélérer** : http://localhost:5000/accelerer
6. **Freiner** : http://localhost:5000/freiner
7. **Arrêter** : http://localhost:5000/arreter
8. **Voir le statut** : http://localhost:5000/status

## 💡 Points importants

### 1. Décorateur @app.route()
```python
@app.route('/ma-route')
def ma_fonction():
    return "Résultat"
```
Transforme une fonction Python en endpoint web accessible via URL.

### 2. jsonify()
```python
return jsonify({"message": "OK"})
```
Convertit un dictionnaire Python en réponse JSON (format web standard).

### 3. Variables globales
```python
voiture = None
conducteur = None
```
Dans ce tutoriel simple, on utilise des variables globales. En production, on utiliserait une base de données.

### 4. Gestion d'erreurs
```python
if not voiture:
    return jsonify({"erreur": "Pas de voiture"}), 400
```
Renvoie un code HTTP 400 (Bad Request) en cas d'erreur.

## 🎓 Exercices suggérés

1. **Ajouter une route POST** : Créer `/creer-voiture-custom` qui accepte les paramètres (marque, modèle, etc.)
2. **Ajouter plusieurs voitures** : Utiliser un dictionnaire pour gérer plusieurs voitures
3. **Ajouter une page HTML** : Créer une interface graphique avec des boutons
4. **Ajouter la persistance** : Sauvegarder l'état dans un fichier JSON

## 🔍 Différences clés Python vs Flask

| Aspect | Python classique | Flask |
|--------|-----------------|-------|
| Exécution | Séquentielle | À la demande (via URL) |
| Interface | Console | Navigateur web |
| État | En mémoire locale | En mémoire serveur (partagée) |
| Résultat | print() | return / jsonify() |

## 📚 Pour aller plus loin

- Apprendre les méthodes HTTP (GET, POST, PUT, DELETE)
- Découvrir les templates Jinja2 pour générer du HTML
- Utiliser SQLAlchemy pour une vraie base de données
- Explorer Flask-RESTful pour des APIs plus robustes
