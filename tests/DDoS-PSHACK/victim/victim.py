import time
import threading
import psutil
import subprocess
import json
import os
from flask import Flask, jsonify, request

app = Flask(__name__)
baseline_rate = 0
TRAFFIC_THRESHOLD = 500
MAX_WAIT_SECONDS = 30  # tempo massimo di attesa prima di considerare la mitigazione fallita
LOG_FILE = "/app/logs/ddos_pshack_test.json"
iptables_active = False

#calcolo la media dei dati ricevuti in fase si "riposo" del container facendo la media tra due valori, uno due secondi dopo l'altro
def measure_baseline():
    global baseline_rate
    bytes_start = psutil.net_io_counters().bytes_recv
    time.sleep(2)
    bytes_end = psutil.net_io_counters().bytes_recv
    baseline_rate = (bytes_end - bytes_start) / 2
    print(f"Baseline: {baseline_rate} byte\n")
    
#Per la visualizzazione del traffico in tmepo reale
def traffic_monitor():
    while True:
        rate = get_current_rate()
        print(f"Traffico in ingresso: {rate} byte", flush=True)

def get_current_rate():
    if not iptables_active:
        bytes_start = psutil.net_io_counters().bytes_recv
        time.sleep(0.5)             
        bytes_end = psutil.net_io_counters().bytes_recv
        return bytes_end - bytes_start
    else:
        bytes_start = get_iptables_accepted_bytes()
        time.sleep(0.5)
        bytes_end = get_iptables_accepted_bytes()
        return bytes_end - bytes_start

def get_iptables_accepted_bytes():
    result = subprocess.run(                                                #legge i byte accettati dalla regola del ratelimit
        ["iptables", "-L", "INPUT", "-n", "-v", "--line-numbers"],
        capture_output=True, text=True
    )
    for line in result.stdout.splitlines():
        if "limit" in line and "ACCEPT" in line:
            parts = line.split()
            try:
                return int(parts[2])
            except:
                return 0
    return 0
    

#Funzione per la mitigaizone del traffico
def mitigate(data):
    
    subprocess.run([                                                        #Accetta massimo 10 pkt al secondo....
        "iptables", "-I", "INPUT", "1",
        "-m", "limit", "--limit", "10/sec", "--limit-burst", "20",
        "-j", "ACCEPT"
    ], capture_output=True)
    
    subprocess.run([                                                        #...Il resto li elimina
        "iptables", "-I", "INPUT","2", "-j", "DROP"
    ], capture_output=True)
    
    result = subprocess.run(
    ["iptables", "-L", "INPUT", "-n", "--line-numbers"],
    capture_output=True, text=True
    )
    print(f"Regole attive:\n{result.stdout}", flush=True)

    err_result = subprocess.run(
        ["iptables", "-I", "INPUT", "1", "-m", "limit", "--limit", "10/sec", "--limit-burst", "20", "-j", "ACCEPT"],
        capture_output=True, text=True
    )
    print(f"Errore iptables: {err_result.stderr}", flush=True)
    global iptables_active
    iptables_active = True
    
    start_wait = time.time()
    while True:
        rate = get_current_rate()
        if rate <= baseline_rate + TRAFFIC_THRESHOLD:      
            t3 = time.time()              
            print(f"Rate Limit applicato, t3= {t3}", flush=True)
            break
        
        if time.time() - start_wait > MAX_WAIT_SECONDS:
            print("Timeout, mitigazione non avvenuta con successo", flush=True)
            return
        time.sleep(1)
    
    saveOnLog(data, t3)
    
#Funzione salvataggio su log
def saveOnLog(data,t3):
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

        for entry in logs:
            if entry.get("attack_id") == data.get("attack_id"):
                entry["T1"] = float(data.get("T1", 0))
                entry["T2"] = float(data.get("T2", 0))
                entry["T3"] = t3
                entry["successo"] = True
                break
        
        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=4)
            print(f"Log aggiornato con successo", flush=True)
    else:
        print("ATTENZIONE: File di log non trovato", flush=True)
    
    
@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "ok", "baseline_rate": baseline_rate})

@app.route('/alert', methods=['POST'])
def alert():
    data = request.get_json()
    print(f"Alert ricevuto per attacco: {data.get('attack_id')}", flush=True)
    threading.Thread(target=mitigate, args=(data,), daemon=True).start()
    return jsonify({"status": "Alert ricevuto, mitigazione in corso"})

if __name__ == '__main__':
    measure_baseline()
    
    monitor_thread = threading.Thread(target=traffic_monitor, daemon=True)
    monitor_thread.start()
    
    app.run(host='0.0.0.0', port=5050)
    
    
    
#Avvio --> docker-compose up victim
#Avvio  con modifiche --> docker-compose up --build victim