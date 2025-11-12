"""
Module contenant la classe Voiture
"""

class Voiture:
    def __init__(self, marque, modele, annee, couleur):
        self.marque = marque
        self.modele = modele
        self.annee = annee
        self.couleur = couleur
    
    def __repr__(self):
        return f"{self.marque} {self.modele} ({self.annee})"
    
    def age(self):
        """Calcule l'âge de la voiture"""
        from datetime import datetime
        return datetime.now().year - self.annee
