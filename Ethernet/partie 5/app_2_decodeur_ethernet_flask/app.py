from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from io import StringIO

app = Flask(__name__, static_folder='static', template_folder='static')

def decode_manchester(signal, time, sample_rate=1e9, bit_rate=10e6):
    """
    Décode un signal Manchester encodé (10BASE-T Ethernet)
    
    Args:
        signal: Signal analogique
        time: Vecteur temps
        sample_rate: Taux d'échantillonnage (Hz)
        bit_rate: Débit en bits/seconde (10 Mbps pour 10BASE-T)
    
    Returns:
        dict avec les données décodées
    """
    # Paramètres
    bit_period = 1.0 / bit_rate  # 100 ns pour 10 Mbps
    half_bit_period = bit_period / 2  # 50 ns
    samples_per_bit = int(bit_period * sample_rate)
    samples_per_half_bit = int(half_bit_period * sample_rate)
    
    # Déterminer le seuil de décision
    threshold = np.median(signal)
    
    # Convertir en signal numérique
    digital = (signal > threshold).astype(int)
    
    # Détecter les transitions (fronts)
    transitions = np.diff(digital)
    rising_edges = np.where(transitions == 1)[0]
    falling_edges = np.where(transitions == -1)[0]
    all_edges = np.sort(np.concatenate([rising_edges, falling_edges]))
    
    # Décodage Manchester
    # Dans Manchester, une transition au milieu du bit encode la donnée:
    # Transition descendante (1→0) au milieu = bit 1
    # Transition montante (0→1) au milieu = bit 0
    
    bits = []
    bit_times = []
    bit_positions = []
    
    i = 0
    while i < len(all_edges) - 1:
        edge_pos = all_edges[i]
        next_edge_pos = all_edges[i + 1]
        
        # Intervalle entre deux transitions
        interval = next_edge_pos - edge_pos
        
        # Si l'intervalle est proche d'un demi-bit, c'est une transition de données
        if 0.4 * samples_per_half_bit < interval < 1.6 * samples_per_half_bit:
            # Déterminer le type de transition
            if digital[edge_pos] == 0 and digital[edge_pos + 1] == 1:
                # Transition montante = bit 0 (IEEE 802.3)
                bits.append(0)
            else:
                # Transition descendante = bit 1 (IEEE 802.3)
                bits.append(1)
            
            bit_times.append(time[edge_pos])
            bit_positions.append(edge_pos)
            i += 1
        else:
            # Transition de synchronisation ou bruit
            i += 1
    
    return {
        'bits': bits,
        'bit_times': bit_times,
        'bit_positions': bit_positions,
        'num_bits': len(bits),
        'digital_signal': digital.tolist()
    }

def bits_to_bytes(bits):
    """Convertit une liste de bits en bytes"""
    bytes_data = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_bits = bits[i:i+8]
            # LSB first pour Ethernet
            byte_value = sum(bit << idx for idx, bit in enumerate(byte_bits))
            bytes_data.append(byte_value)
    return bytes_data

def decode_ethernet_frame(bytes_data):
    """
    Décode une trame Ethernet
    
    Structure trame Ethernet II:
    - Préambule: 7 octets (0x55) + SFD: 1 octet (0xD5)
    - MAC destination: 6 octets
    - MAC source: 6 octets
    - Type/Longueur: 2 octets
    - Données: 46-1500 octets
    - FCS (CRC): 4 octets
    """
    if len(bytes_data) < 14:
        return None
    
    frame = {}
    idx = 0
    
    # Chercher le Start Frame Delimiter (SFD = 0xD5 = 0b11010101)
    sfd_found = False
    for i, byte in enumerate(bytes_data):
        if byte == 0xD5 or byte == 0xAB:  # 0xAB = 0xD5 inversé
            idx = i + 1
            sfd_found = True
            frame['preamble_end'] = i
            break
    
    if not sfd_found and len(bytes_data) >= 8:
        # Pas de SFD trouvé, supposer qu'on commence après le préambule
        idx = 0
    
    if idx + 14 > len(bytes_data):
        return None
    
    # MAC destination (6 octets)
    frame['dest_mac'] = ':'.join([f'{b:02X}' for b in bytes_data[idx:idx+6]])
    idx += 6
    
    # MAC source (6 octets)
    frame['src_mac'] = ':'.join([f'{b:02X}' for b in bytes_data[idx:idx+6]])
    idx += 6
    
    # Type/Longueur (2 octets, big-endian)
    ethertype = (bytes_data[idx] << 8) | bytes_data[idx+1]
    frame['ethertype'] = ethertype
    frame['ethertype_hex'] = f'0x{ethertype:04X}'
    
    # Identifier le protocole
    if ethertype <= 1500:
        frame['protocol'] = f'IEEE 802.3 (longueur: {ethertype})'
    elif ethertype == 0x0800:
        frame['protocol'] = 'IPv4'
    elif ethertype == 0x0806:
        frame['protocol'] = 'ARP'
    elif ethertype == 0x86DD:
        frame['protocol'] = 'IPv6'
    else:
        frame['protocol'] = f'Inconnu (0x{ethertype:04X})'
    
    idx += 2
    
    # Données
    if idx < len(bytes_data) - 4:  # -4 pour le FCS
        frame['payload_length'] = len(bytes_data) - idx - 4
        frame['payload'] = ' '.join([f'{b:02X}' for b in bytes_data[idx:idx+min(32, len(bytes_data)-idx-4)]])
        if len(bytes_data) - idx - 4 > 32:
            frame['payload'] += '...'
    
    # FCS (4 derniers octets)
    if len(bytes_data) >= 4:
        fcs_bytes = bytes_data[-4:]
        frame['fcs'] = ' '.join([f'{b:02X}' for b in fcs_bytes])
    
    frame['total_length'] = len(bytes_data)
    
    return frame

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        if file and file.filename.endswith('.csv'):
            # Lire le fichier CSV
            content = file.read().decode('utf-8')
            lines = content.split('\n')
            
            # Trouver l'index de début des données
            data_start_idx = 0
            metadata = {}
            for i, line in enumerate(lines):
                if line.startswith('TIME,'):
                    data_start_idx = i + 1
                    break
                if ',' in line:
                    parts = line.split(',', 1)
                    if len(parts) == 2:
                        metadata[parts[0]] = parts[1]
            
            # Lire les données
            data_content = '\n'.join(lines[data_start_idx - 1:])
            df = pd.read_csv(StringIO(data_content))
            df.columns = df.columns.str.strip()
            
            time = df[df.columns[0]].values
            signal = df[df.columns[1]].values
            
            # Calculer le taux d'échantillonnage
            sample_interval = np.mean(np.diff(time))
            sample_rate = 1.0 / sample_interval
            
            # Décoder Manchester
            decoded = decode_manchester(signal, time, sample_rate)
            
            # Convertir en bytes
            bytes_data = bits_to_bytes(decoded['bits'])
            
            # Décoder la trame Ethernet
            ethernet_frame = decode_ethernet_frame(bytes_data)
            
            # Préparer les données pour le graphique (échantillonner)
            max_plot_points = 2000
            if len(signal) > max_plot_points:
                indices = np.linspace(0, len(signal) - 1, max_plot_points, dtype=int)
                plot_time = time[indices].tolist()
                plot_signal = signal[indices].tolist()
                plot_digital = [decoded['digital_signal'][i] for i in indices]
            else:
                plot_time = time.tolist()
                plot_signal = signal.tolist()
                plot_digital = decoded['digital_signal']
            
            # Marquer les positions des bits décodés
            bit_markers = {
                'times': decoded['bit_times'][:min(500, len(decoded['bit_times']))],
                'values': [signal[pos] for pos in decoded['bit_positions'][:min(500, len(decoded['bit_positions']))]]
            }
            
            # Formater les bits en chaîne hexadécimale
            hex_string = ' '.join([f'{b:02X}' for b in bytes_data[:64]])
            if len(bytes_data) > 64:
                hex_string += '...'
            
            binary_string = ''.join([str(b) for b in decoded['bits'][:128]])
            if len(decoded['bits']) > 128:
                binary_string += '...'
            
            return jsonify({
                'success': True,
                'metadata': metadata,
                'signal_info': {
                    'sample_rate': f'{sample_rate/1e9:.2f} GSa/s',
                    'total_samples': len(signal),
                    'duration': f'{(time[-1] - time[0])*1e6:.2f} µs',
                    'bits_decoded': decoded['num_bits'],
                    'bytes_decoded': len(bytes_data)
                },
                'plot_data': {
                    'time': plot_time,
                    'analog': plot_signal,
                    'digital': plot_digital,
                    'bit_markers': bit_markers
                },
                'decoded_data': {
                    'binary': binary_string,
                    'hex': hex_string,
                    'bytes': bytes_data[:128]
                },
                'ethernet_frame': ethernet_frame
            })
        
        return jsonify({'error': 'Format de fichier invalide'}), 400
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erreur: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)