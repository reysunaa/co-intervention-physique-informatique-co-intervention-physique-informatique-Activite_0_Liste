# Tutoriel Flask  : Routes GET et HTML

Tutoriel progressif pour comprendre les routes Flask et la syntaxe Jinja2, avec un exemple sur les voitures du fichier *voitures.csv*.


## Structure du projet

```
mon_projet/
├── app.py
├── voiture.py
├── voitures.csv
└── templates/
    ├── index.html
    ├── voiture.html
    └── liste.html
```


## Lancement de l'application (app.py)

```bash
# se rendre dans le dossier de l'application 
cd Ethernet/partie\ 5/tuto_flask/
python app.py
```

Accédez à `http://127.0.0.1:5000/`

## 🔄 Comment les données arrivent dans le HTML ?

### Exemple avec la route `/voiture/1`

**1. L'utilisateur visite l'URL**
```
http://127.0.0.1:5000/voiture/1
```

**2. Flask appelle la fonction correspondante (app.py)**
```python
@app.route('/voiture/<int:id>')
def detail_voiture(id):                    # id = 1
    voiture = voitures.get(id)             # Récupère l'objet Voiture
    return render_template('voiture.html', voiture=voiture)
```

**3. La variable est passée au template**
```python
render_template('voiture.html', voiture=voiture)
#                                 ↑         ↑
#                          nom dans HTML   objet Python
```

**4. Jinja2 traite le template (voiture.html)**
```html
<h1>{{ voiture.marque }}</h1>
```

**5. Le HTML final est généré et envoyé au navigateur**
```html
<h1>Renault</h1>
```

### Schéma du flux complet

```
URL : /voiture/1
       ↓
Flask trouve la route @app.route('/voiture/<int:id>')
       ↓
Fonction detail_voiture(id=1) s'exécute
       ↓
voiture = voitures.get(1)  →  Objet Voiture(marque="Renault", ...)
       ↓
render_template('voiture.html', voiture=voiture)
       ↓
Jinja2 remplace {{ voiture.marque }} par "Renault"
       ↓
HTML final envoyé au navigateur
```

### Passage de plusieurs variables

```python
@app.route('/voitures')
def liste_voitures():
    return render_template('liste.html', 
                         voitures=voitures,    # Dictionnaire de voitures
                         titre="Nos voitures")  # Une chaîne de texte
```

Dans le template `liste.html` :
```html
<h1>{{ titre }}</h1>  <!-- Affiche "Nos voitures" -->

{% for id, voiture in voitures.items() %}
    {{ voiture.marque }}
{% endfor %}
```

## Progression pédagogique

### Étape 1 : Afficher une variable simple
**Route :** `/voiture/1`  
**Template :** `voiture.html`

```html
<h1>{{ voiture.marque }}</h1>
```

La syntaxe `{{ }}` affiche une variable Python dans le HTML.

---

### Étape 2 : Afficher plusieurs attributs
**Route :** `/voiture/1`  
**Template :** `voiture.html`

```html
<li>Marque: {{ voiture.marque }}</li>
<li>Modèle: {{ voiture.modele }}</li>
<li>Année: {{ voiture.annee }}</li>
```

On accède aux attributs d'un objet avec la notation point.

---

### Étape 3 : Condition simple
**Route :** `/voiture/1`  
**Template :** `voiture.html`

```html
{% if voiture %}
    <p>Voiture trouvée</p>
{% else %}
    <p>Aucune voiture</p>
{% endif %}
```

La syntaxe `{% %}` permet d'écrire de la logique (conditions, boucles).

---

### Étape 4 : Boucle sur une liste
**Route :** `/voitures`  
**Template :** `liste.html`

```html
{% for id, voiture in voitures.items() %}
    <li>{{ voiture.marque }} {{ voiture.modele }}</li>
{% endfor %}
```

La boucle `for` parcourt un dictionnaire et affiche chaque voiture.

---

### Étape 5 : Liens dynamiques
**Route :** `/voitures`  
**Template :** `liste.html`

```html
{% for id, voiture in voitures.items() %}
    <li>
        {{ voiture.marque }} 
        <a href="/voiture/{{ id }}">Voir détails</a>
    </li>
{% endfor %}
```

On peut utiliser des variables dans les URLs pour créer des liens dynamiques.

---

### Étape 6 : Filtrer les données
**Route :** `/couleur/rouge`  
**Code Python :** `app.py`

```python
@app.route('/couleur/<couleur>')
def par_couleur(couleur):
    resultats = {id: v for id, v in voitures.items() if v.couleur == couleur}
    return render_template('liste.html', voitures=resultats)
```

Les routes dynamiques `<couleur>` capturent un paramètre de l'URL.

## Exercice pratique

Créez une route `/marque/<marque>` qui filtre par marque.

**A compléter :**
```python
@app.route('/marque/<marque>')
def par_marque(marque):
    #TODO
```

Testez avec : `http://127.0.0.1:5000/marque/Renault`
