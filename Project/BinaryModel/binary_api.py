import joblib
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)
model = joblib.load("model_binary.pkl")

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
        el_data = [data["features"].get(col, 0) for col in X_columns]
        el_data = np.array(el_data).reshape(1, -1)
        
        prob = model.predict_proba(el_data)[0]

        return jsonify({          
            "benign_probability": float(prob[0]),
            "malicious_probability": float(prob[1]),
            "features": data["features"] 
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)