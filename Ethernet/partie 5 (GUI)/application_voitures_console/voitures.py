class Moteur:
    def __init__(self, puissance: int, type_carburant: str):
        self.__puissance = puissance
        self.__type_carburant = type_carburant
    
    def allumer(self):
        print(f"Moteur de {self.__puissance} CV allumé")
    
    def eteindre(self):
        print("Moteur éteint")


class Roue:
    def __init__(self, taille: int, type_roue: str):
        self.__taille = taille
        self.__type = type_roue
    
    def tourner(self):
        print(f"Roue de {self.__taille} pouces tourne")


class Conducteur:
    def __init__(self, nom: str, permis: str):
        self.__nom = nom
        self.__permis = permis
    
    def conduire(self):
        print(f"{self.__nom} conduit")
    
    def monter(self):
        print(f"{self.__nom} monte dans la voiture")
    
    def descendre(self):
        print(f"{self.__nom} descend de la voiture")


class Voiture:
    def __init__(self, marque: str, modele: str, annee: int, couleur: str):
        self.__marque = marque
        self.__modele = modele
        self.__annee = annee
        self.__couleur = couleur
        
        # Composition : le Moteur et les Roues sont créés avec la Voiture
        self.__moteur = Moteur(puissance=150, type_carburant="Essence")
        self.__roues = [Roue(taille=17, type_roue="Été") for _ in range(4)]
        
        # Agrégation : le Conducteur est optionnel et existe indépendamment
        self.__conducteur = None
    
    def set_conducteur(self, conducteur: Conducteur):
        """Agrégation : on associe un conducteur existant"""
        self.__conducteur = conducteur
        if conducteur:
            conducteur.monter()
    
    def remove_conducteur(self):
        """Le conducteur quitte la voiture mais continue d'exister"""
        if self.__conducteur:
            self.__conducteur.descendre()
            self.__conducteur = None
    
    def demarrer(self):
        if self.__conducteur:
            self.__moteur.allumer()
            print(f"{self.__marque} {self.__modele} démarre")
        else:
            print("Impossible de démarrer : pas de conducteur")
    
    def arreter(self):
        self.__moteur.eteindre()
        print(f"{self.__marque} {self.__modele} s'arrête")
    
    def accelerer(self):
        if self.__conducteur:
            for roue in self.__roues:
                roue.tourner()
            print("La voiture accélère")
    
    def freiner(self):
        print("La voiture freine")


# Exemple d'utilisation
if __name__ == "__main__":
    # Création d'une voiture (composition : moteur et roues créés automatiquement)
    ma_voiture = Voiture(marque="Renault", modele="Clio", annee=2023, couleur="Bleu")
    
    # Création d'un conducteur (existe indépendamment)
    conducteur = Conducteur(nom="Marie", permis="B")
    
    print("=== Sans conducteur ===")
    ma_voiture.demarrer()  # Ne peut pas démarrer
    
    print("\n=== Avec conducteur (agrégation) ===")
    ma_voiture.set_conducteur(conducteur)
    ma_voiture.demarrer()
    ma_voiture.accelerer()
    ma_voiture.freiner()
    ma_voiture.arreter()
    
    print("\n=== Le conducteur quitte la voiture ===")
    ma_voiture.remove_conducteur()
    conducteur.conduire()  # Le conducteur existe toujours
    
    print("\n=== Destruction de la voiture ===")
    del ma_voiture  # Le moteur et les roues sont détruits avec la voiture
    conducteur.conduire()  # Mais le conducteur existe toujours
