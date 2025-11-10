# TUTORIEL FLASK - Transformation du code voitures.py en API Web
# ============================================================

"""
ÉTAPE 1 : Installation de Flask
--------------------------------
Dans votre terminal, installez Flask :
    pip install flask

ÉTAPE 2 : Structure du projet
------------------------------
Créez un dossier avec ces fichiers :
    /mon_projet
        ├── voitures.py          (le code des classes)
        └── app.py               (ce fichier Flask)

ÉTAPE 3 : Comprendre Flask
---------------------------
Flask permet de créer des routes (URLs) qui déclenchent des fonctions Python.
Une route = une URL = une fonction

Exemple :
    @app.route('/hello')
    def hello():
        return "Bonjour!"
    
    Quand on visite http://localhost:5000/hello, la fonction hello() s'exécute.
"""

from flask import Flask, jsonify
from voitures import Voiture, Conducteur

# Création de l'application Flask
app = Flask(__name__)

# Variables globales pour stocker nos objets (en production, utiliser une base de données)
voiture = None
conducteur = None


# ROUTE 1 : Page d'accueil
# =========================
@app.route('/')
def home():
    """Route principale qui explique l'API"""
    return """
    <h1>API Voiture - Tutoriel Flask</h1>
    <h2>Routes disponibles :</h2>
    <ul>
        <li><a href="/creer-voiture">/creer-voiture</a> - Créer une voiture</li>
        <li><a href="/creer-conducteur">/creer-conducteur</a> - Créer un conducteur</li>
        <li><a href="/associer-conducteur">/associer-conducteur</a> - Associer le conducteur à la voiture</li>
        <li><a href="/demarrer">/demarrer</a> - Démarrer la voiture</li>
        <li><a href="/accelerer">/accelerer</a> - Accélérer</li>
        <li><a href="/freiner">/freiner</a> - Freiner</li>
        <li><a href="/arreter">/arreter</a> - Arrêter la voiture</li>
        <li><a href="/retirer-conducteur">/retirer-conducteur</a> - Retirer le conducteur</li>
        <li><a href="/status">/status</a> - Voir l'état actuel</li>
    </ul>
    """


# ROUTE 2 : Créer une voiture (Composition)
# ==========================================
@app.route('/creer-voiture')
def creer_voiture():
    """
    Cette route crée une nouvelle voiture.
    Le moteur et les roues sont créés automatiquement (composition).
    """
    global voiture
    voiture = Voiture(marque="Renault", modele="Clio", annee=2023, couleur="Bleu")
    
    return jsonify({
        "message": "Voiture créée avec succès",
        "details": "Une Renault Clio 2023 bleue (avec moteur et 4 roues)"
    })


# ROUTE 3 : Créer un conducteur (Agrégation)
# ===========================================
@app.route('/creer-conducteur')
def creer_conducteur():
    """
    Cette route crée un conducteur indépendant.
    Il existe séparément de la voiture (agrégation).
    """
    global conducteur
    conducteur = Conducteur(nom="Marie", permis="B")
    
    return jsonify({
        "message": "Conducteur créé avec succès",
        "details": "Marie avec permis B"
    })


# ROUTE 4 : Associer le conducteur à la voiture
# ==============================================
@app.route('/associer-conducteur')
def associer_conducteur():
    """
    Cette route associe le conducteur à la voiture.
    Démontre l'agrégation : on lie deux objets indépendants.
    """
    if not voiture:
        return jsonify({"erreur": "Créez d'abord une voiture avec /creer-voiture"}), 400
    
    if not conducteur:
        return jsonify({"erreur": "Créez d'abord un conducteur avec /creer-conducteur"}), 400
    
    voiture.set_conducteur(conducteur)
    
    return jsonify({
        "message": "Conducteur associé à la voiture",
        "details": "Marie est maintenant dans la Renault Clio"
    })


# ROUTE 5 : Démarrer la voiture
# ==============================
@app.route('/demarrer')
def demarrer():
    """
    Cette route démarre la voiture.
    Nécessite un conducteur (validation métier).
    """
    if not voiture:
        return jsonify({"erreur": "Pas de voiture"}), 400
    
    try:
        voiture.demarrer()
        return jsonify({"message": "Voiture démarrée"})
    except:
        return jsonify({"erreur": "Impossible de démarrer (pas de conducteur?)"}), 400


# ROUTE 6 : Accélérer
# ====================
@app.route('/accelerer')
def accelerer():
    """Route pour accélérer la voiture"""
    if not voiture:
        return jsonify({"erreur": "Pas de voiture"}), 400
    
    voiture.accelerer()
    return jsonify({"message": "Voiture accélère"})


# ROUTE 7 : Freiner
# ==================
@app.route('/freiner')
def freiner():
    """Route pour freiner la voiture"""
    if not voiture:
        return jsonify({"erreur": "Pas de voiture"}), 400
    
    voiture.freiner()
    return jsonify({"message": "Voiture freine"})


# ROUTE 8 : Arrêter la voiture
# =============================
@app.route('/arreter')
def arreter():
    """Route pour arrêter la voiture"""
    if not voiture:
        return jsonify({"erreur": "Pas de voiture"}), 400
    
    voiture.arreter()
    return jsonify({"message": "Voiture arrêtée"})


# ROUTE 9 : Retirer le conducteur
# ================================
@app.route('/retirer-conducteur')
def retirer_conducteur():
    """
    Cette route retire le conducteur de la voiture.
    Démontre l'agrégation : le conducteur continue d'exister.
    """
    if not voiture:
        return jsonify({"erreur": "Pas de voiture"}), 400
    
    voiture.remove_conducteur()
    
    return jsonify({
        "message": "Conducteur retiré de la voiture",
        "details": "Le conducteur existe toujours mais n'est plus dans la voiture"
    })


# ROUTE 10 : Voir le statut
# ==========================
@app.route('/status')
def status():
    """Route pour voir l'état actuel du système"""
    return jsonify({
        "voiture_existe": voiture is not None,
        "conducteur_existe": conducteur is not None,
        "conducteur_dans_voiture": voiture._Voiture__conducteur is not None if voiture else False
    })


# POINT D'ENTRÉE DE L'APPLICATION
# ================================
if __name__ == '__main__':
    print("\n" + "="*60)
    print("TUTORIEL FLASK - API Voiture")
    print("="*60)
    print("\n📚 COMMENT UTILISER :")
    print("   1. Lancez ce fichier : python app.py")
    print("   2. Ouvrez votre navigateur")
    print("   3. Visitez : http://localhost:5000")
    print("   4. Cliquez sur les liens pour tester les routes")
    print("\n💡 SCÉNARIO TYPIQUE :")
    print("   1. /creer-voiture")
    print("   2. /creer-conducteur")
    print("   3. /associer-conducteur")
    print("   4. /demarrer")
    print("   5. /accelerer")
    print("   6. /freiner")
    print("   7. /arreter")
    print("\n" + "="*60 + "\n")
    
    # Lancement du serveur Flask en mode debug
    app.run(debug=True, port=5000)
