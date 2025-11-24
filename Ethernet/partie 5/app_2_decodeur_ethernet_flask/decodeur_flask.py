#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import numpy as np
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import traceback


# ============================================
#           LECTURE CSV OSCILLOSCOPE
# ============================================

class LecteurCSVOscillo(object):
    """Classe pour lire les fichiers CSV d'oscilloscope"""

    def __init__(self, chemin_fichier):
        self.chemin_fichier = chemin_fichier
        self.donnees = []
        self.intervalle_echantillon = None

    def charger_donnees(self, osc_type):
        """
        osc_type doit être 'rigol', 'mso' ou 'tds'.
        AUCUNE détection automatique.
        """
        if osc_type == "rigol":
            return self._charger_rigol()
        elif osc_type == "mso":
            return self._charger_tektronix_mso()
        elif osc_type == "tds":
            return self._charger_tektronix_tds()
        else:
            raise ValueError("Type d'oscilloscope invalide (rigol / mso / tds)")

    def _charger_rigol(self):
        # Rigol : données en col 0 après la 27e ligne
        return self._lire_csv('Sampling Period', 0, 27)

    def _charger_tektronix_mso(self):
        # Tektronix MSO : données en col 1 après la 18e ligne
        return self._lire_csv('Sample Interval', 1, 18)

    def _charger_tektronix_tds(self):
        # Tektronix TDS : données en col 4 à partir de la 0e ligne
        return self._lire_csv('Sample Interval', 4, 0)

    def _lire_csv(self, sample_field, data_col_index, start_row_index):
        data = []
        sample_interval = None

        with open(self.chemin_fichier, 'rt') as f:
            reader = csv.reader(f, delimiter=',')
            for index, row in enumerate(reader):
                if not row:
                    continue

                # Ligne avec l'intervalle d'échantillonnage
                if row[0] == sample_field:
                    sample_interval = float(row[1].replace(",", "."))

                # Lignes de données
                elif index >= start_row_index:
                    try:
                        val = float(row[data_col_index])
                        data.append(val)
                    except (ValueError, IndexError):
                        continue

        if sample_interval is None:
            raise ValueError("Intervalle d'échantillonnage non trouvé dans le CSV")
        if len(data) == 0:
            raise ValueError("Aucune donnée valide trouvée dans le CSV")

        self.donnees = data
        self.intervalle_echantillon = sample_interval
        return (np.array(data), sample_interval)


# ============================================
#        MISE EN FORME DU SIGNAL
# ============================================

class FormateurSignal(object):

    def __init__(self, donnees, intervalle_echantillon):
        self.donnees = donnees
        self.intervalle_echantillon = intervalle_echantillon

    def supprimer_composante_continue(self):
        self.donnees = self.donnees - np.mean(self.donnees)

    def normalisation(self):
        max_abs = np.max(np.abs(self.donnees))
        if max_abs != 0:
            self.donnees = self.donnees / max_abs

    def aligner_debut_signal(self):
        index = 0
        while index < len(self.donnees) and self.donnees[index] > -0.07:
            index += 1
        self.donnees = self.donnees[index:]

    def mettre_en_forme(self):
        self.supprimer_composante_continue()
        self.normalisation()
        self.aligner_debut_signal()
        return self.donnees


# ============================================
#           DÉCODAGE MANCHESTER
# ============================================

class DecodeurManchester(object):

    def __init__(self, donnees, intervalle_echantillon, debit=10e6):
        self.donnees = donnees
        self.intervalle_echantillon = intervalle_echantillon
        self.debit = debit
        self.nbr_ech_bin = None
        self.trame_binaire = ""

    def decoder_donnees(self):
        self.nbr_ech_bin = int(round(1.0 / (self.intervalle_echantillon * self.debit)))
        if self.nbr_ech_bin <= 0:
            raise ValueError("Nombre d'échantillons par bit invalide")

        decode = ""
        i = self.nbr_ech_bin // 4  # quart de bit

        while i < len(self.donnees) - self.nbr_ech_bin // 2:
            somme1 = self.donnees[i]
            somme2 = self.donnees[i + self.nbr_ech_bin // 2]

            if somme1 > 0 and somme2 < 0:
                decode += "0"
            elif somme1 < 0 and somme2 > 0:
                decode += "1"

            i += self.nbr_ech_bin

        self.trame_binaire = decode
        return decode

    def supprimer_preambule(self):
        decode = self.trame_binaire
        i = 0
        while i + 1 < len(decode) and decode[i] == '1' and decode[i + 1] == '0':
            i += 2
        if i + 2 <= len(decode):
            return decode[i + 2:]
        else:
            return ""


# ============================================
#             DÉCODAGE ETHERNET
# ============================================

class DecodeurEthernet(object):

    def __init__(self, trame_decodee_bin):
        self.trame_decodee = trame_decodee_bin
        self.mac_dest_bin = ""
        self.mac_src_bin = ""
        self.type_bin = ""
        self.trame_hex = ""

    def extraire_champs(self):
        decode = self.trame_decodee
        octets = []
        i = 0
        while i + 8 <= len(decode):
            byte = decode[i:i + 8][::-1]  # inversion bit order
            try:
                octets.append(hex(int(byte, 2))[2:].zfill(2))
            except ValueError:
                pass
            i += 8

        if len(octets) >= 14:
            self.mac_dest_bin = ' '.join(octets[0:6])
            self.mac_src_bin = ' '.join(octets[6:12])
            self.type_bin = ' '.join(octets[12:14])

        self.trame_hex = ' '.join(octets)

    def ether_type(self):
        ethertype = self.type_bin.lower()
        if ethertype == '08 00':
            return 'IPv4'
        elif ethertype == '08 06':
            return 'ARP'
        elif ethertype == '86 dd':
            return 'IPv6'
        else:
            return 'Inconnu'


# ============================================
#                 FLASK
# ============================================

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Récupération des champs du formulaire
            osc_type = request.form.get("osc_type", "").strip()
            csv_file = request.files.get("csv_file")

            if osc_type not in ("rigol", "mso", "tds"):
                return "<h1>Erreur</h1><p>Type d'oscilloscope invalide (rigol / mso / tds).</p>", 400

            if csv_file is None or csv_file.filename == "":
                return "<h1>Erreur</h1><p>Aucun fichier CSV fourni.</p>", 400

            # Sauvegarde du fichier
            filename = secure_filename(csv_file.filename)
            final_filename = osc_type.upper() + "_" + filename
            file_path = os.path.join(UPLOAD_FOLDER, final_filename)
            csv_file.save(file_path)

            # ===== Lecture CSV =====
            lecteur = LecteurCSVOscillo(file_path)
            donnees, intervalle = lecteur.charger_donnees(osc_type)

            # ===== Mise en forme =====
            formateur = FormateurSignal(donnees, intervalle)
            donnees_formatees = formateur.mettre_en_forme()

            # ===== Décodage Manchester =====
            decodeur_manch = DecodeurManchester(donnees_formatees, intervalle)
            trame_binaire = decodeur_manch.decoder_donnees()
            trame_sans_preambule = decodeur_manch.supprimer_preambule()

            # ===== Décodage Ethernet =====
            decodeur_eth = DecodeurEthernet(trame_sans_preambule)
            decodeur_eth.extraire_champs()

            trame_hex_complete = decodeur_eth.trame_hex
            mac_dest = decodeur_eth.mac_dest_bin
            mac_src = decodeur_eth.mac_src_bin
            ethertype_hex = decodeur_eth.type_bin
            ethertype_name = decodeur_eth.ether_type()

            # Payload après les 14 premiers octets
            octets = trame_hex_complete.split()
            if len(octets) > 14:
                payload_hex = " ".join(octets[14:])
            else:
                payload_hex = ""

            ech_par_bit = decodeur_manch.nbr_ech_bin

            # Affichage HTML avec result.html
            return render_template(
                "result.html",
                osc_type=osc_type,
                filename=filename,
                nb_ech=len(donnees),
                intervalle=intervalle,
                ech_par_bit=ech_par_bit,
                trame_binaire=trame_binaire,
                trame_sans_preambule=trame_sans_preambule,
                trame_hex_complete=trame_hex_complete,
                mac_dest=mac_dest,
                mac_src=mac_src,
                ethertype_hex=ethertype_hex,
                ethertype_name=ethertype_name,
                payload_hex=payload_hex,
            )

        except Exception:
            # RENVOIE LA TRACE DIRECTEMENT DANS LE NAVIGATEUR
            return "<h1>Erreur interne</h1><pre>%s</pre>" % traceback.format_exc(), 500

    # GET
    return render_template("index.html")


if __name__ == "__main__":
    # debug=True : auto-reload + erreurs détaillées en console
    app.run(debug=True)
