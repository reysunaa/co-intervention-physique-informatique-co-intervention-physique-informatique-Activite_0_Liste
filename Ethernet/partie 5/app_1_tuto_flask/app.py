from flask import Flask, render_template
import csv
from pathlib import Path                    # 1. Importez pathlib
from voiture import Voiture

app = Flask(__name__)
BASE_DIR = Path(__file__).parent            # 2. Définissez le répertoire de base
CHEMIN_DU_CSV = BASE_DIR / 'voitures.csv'   # 3. Construisez le chemin complet vers le fichier CSV

# Fonction pour charger les voitures depuis le CSV
def charger_voitures(fichier_csv):
    voitures = {}
    with open(fichier_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for index, row in enumerate(reader, start=1):
            voitures[index] = Voiture(
                marque=row['marque'],
                modele=row['modele'],
                annee=int(row['annee']),
                couleur=row['couleur']
            )
    return voitures

# Chargement des voitures depuis le fichier CSV
voitures = charger_voitures(CHEMIN_DU_CSV)

# Route 1: Page d'accueil
@app.route('/')
def accueil():
    return render_template('index.html')

# Route 2: Liste de toutes les voitures
@app.route('/voitures')
def liste_voitures():
    return render_template('liste.html', voitures=voitures)

# Route 3: Détail d'une voiture spécifique
@app.route('/voiture/<int:id>')
def detail_voiture(id):
    voiture = voitures.get(id)
    if voiture:
        return render_template('voiture.html', voiture=voiture, id=id)
    return "Voiture non trouvée", 404

# Route 4: Recherche par couleur
@app.route('/couleur/<couleur>')
def par_couleur(couleur):
    resultats = {id: v for id, v in voitures.items() if v.couleur == couleur}
    return render_template('liste.html', voitures=resultats)

if __name__ == '__main__':
    app.run(debug=True)
