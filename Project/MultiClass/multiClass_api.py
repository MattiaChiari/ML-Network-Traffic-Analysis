import joblib
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)
model = joblib.load("model_multi.pkl")

X_columns = [
        'Header_Length', 'Time_To_Live', 
        'Rate', 'fin_flag_number', 'syn_flag_number', 
        'rst_flag_number', 'psh_flag_number', 'ack_flag_number', 
        'ece_flag_number', 'cwr_flag_number', 'ack_count', 
        'syn_count', 'fin_count', 'rst_count', 'HTTP', 'HTTPS', 
        'DNS', 'Telnet', 'SMTP', 'SSH', 'IRC', 'TCP', 'UDP', 'DHCP',
        'ARP', 'ICMP', 'IGMP', 'IPv', 'Tot sum', 'Min', 'Max', 
        'AVG', 'Std', 'Tot size', 'IAT', 'Number'
    ]

mapp = {
    1: 'DDOS-PSHACK_FLOOD',
    2: 'MIRAI-GREIP_FLOOD',
    3: 'DOS-UDP_FLOOD',
    4: 'DNS_SPOOFING',
    5: 'DDOS-ICMP_FLOOD',
    6: 'DDOS-TCP_FLOOD',
    7: 'DDOS-SYN_FLOOD',
    8: 'DDOS-UDP_FLOOD',
    9: 'MITM-ARPSPOOFING',
    10: 'DDOS-SYNONYMOUSIP_FLOOD',
    11: 'DOS-TCP_FLOOD',
    12: 'VULNERABILITYSCAN',
    13: 'DOS-SYN_FLOOD',
    14: 'DDOS-RSTFINFLOOD',
    15: 'DDOS-SLOWLORIS',
    16: 'DDOS-ICMP_FRAGMENTATION',
    17: 'MIRAI-GREETH_FLOOD',
    18: 'RECON-HOSTDISCOVERY',
    19: 'MIRAI-UDPPLAIN',
    20: 'RECON-PORTSCAN',
    21: 'DDOS-ACK_FRAGMENTATION',
    22: 'DDOS-UDP_FRAGMENTATION',
    23: 'RECON-OSSCAN',
    24: 'BACKDOOR_MALWARE',
    25: 'DOS-HTTP_FLOOD',
    26: 'XSS',
    27: 'DDOS-HTTP_FLOOD',
    28: 'BROWSERHIJACKING',
    29: 'SQLINJECTION',
    30: 'DICTIONARYBRUTEFORCE',
    31: 'COMMANDINJECTION',
    32: 'RECON-PINGSWEEP',
    33: 'UPLOADING_ATTACK'
}

@app.route("/status", methods=["GET"])
def get_status():
    return jsonify({"status": "ok"})

@app.route("/predict", methods=["POST"])
def get_predict():
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "Error", "message": "No JSON payload provided"}), 400
    
    if "features" not in data:
        return jsonify({"status": "Error", "message": "Missing 'features' field in request"}), 400
    
    if not isinstance(data["features"], dict):
        return jsonify({"status": "error", "message": "'features' must be an array"}), 400
        
    try:
        el_data = [data["features"].get(col, np.nan) for col in X_columns]        
        el_data = np.array(el_data).reshape(1, -1)
        
        predicted_index = int(model.predict(el_data)[0])
        probabilities = model.predict_proba(el_data)[0]
        
        confidence = float(np.max(probabilities))
        attack_name = mapp.get(predicted_index, "SCONOSCIUTO")
        
        return jsonify({    
            "attack_name": attack_name,      
            "confidence": confidence,
            "features": data["features"] 
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)