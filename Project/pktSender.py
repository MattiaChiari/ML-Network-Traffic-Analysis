import requests
import json

# L'URL del webhook di test su n8n
URL = "http://localhost:5678/webhook-test/traffic"

payload = {"features": {"Header_Length": 27.2, "Time_To_Live": 209.2, "Rate": 142.51119552586692, "fin_flag_number": 0.0, "syn_flag_number": 0.0, "rst_flag_number": 0.0, "psh_flag_number": 0.0, "ack_flag_number": 0.8, "ece_flag_number": 0.0, "cwr_flag_number": 0.0, "ack_count": 8, "syn_count": 0, "fin_count": 0, "rst_count": 0, "HTTP": 0.0, "HTTPS": 0.8, "DNS": 0.2, "Telnet": 0.0, "SMTP": 0.0, "SSH": 0.0, "IRC": 0.0, "TCP": 0.8, "UDP": 0.2, "DHCP": 0.0, "ARP": 0.0, "ICMP": 0.0, "IGMP": 0.0, "IPv": 1.0, "Tot sum": 818.0, "Min": 66.0, "Max": 178.0, "AVG": 81.8, "Std": 36.76290400813177, "Tot size": 81.8, "IAT": 0.0070170879364013, "Number": 10.0}}

try:
    
    response = requests.post(URL, json=payload)
    
    print(f"Status Code: {response.status_code}")
    print(f"Risposta da n8n: {response.text}")

except Exception as e:
    print(f"Errore di connessione: {e}")