import json

LOG_FILE = "logs/ddos_pshack_test.json"

with open(LOG_FILE, "r") as f:
    data = json.load(f)

totali = len(data)
successi = [t for t in data if t["successo"]]
n = len(successi)

print(f"=== ANALISI TEST DDOS-PSHACK_FLOOD ===\n")
print(f"Test totali   : {totali}")
print(f"Test riusciti : {n}")
print(f"Test falliti  : {totali - n}")
print(f"Successo      : {n/totali*100:.1f}%\n")

if n == 0:
    print("Nessun test riuscito, analisi impossibile.")
    exit()

# calcola i delta per ogni test
d_t1_t0 = [t["T1"] - t["T0"] for t in successi]
d_t2_t1 = [t["T2"] - t["T1"] for t in successi]
d_t3_t2 = [t["T3"] - t["T2"] for t in successi]
d_totale = [t["T3"] - t["T0"] for t in successi]

def stats(label, valori):
    media = sum(valori) / len(valori)
    minimo = min(valori)
    massimo = max(valori)
    print(f"{label}")
    print(f"  Media   : {media*1000:.1f} ms")
    print(f"  Minimo  : {minimo*1000:.1f} ms")
    print(f"  Massimo : {massimo*1000:.1f} ms\n")

print("=== TEMPI MEDI ===\n")
stats("T0 → T1  (rilevamento binario)", d_t1_t0)
stats("T1 → T2  (classificazione attacco)", d_t2_t1)
stats("T2 → T3  (risposta alla vittima)", d_t3_t2)
stats("T0 → T3  (tempo totale)", d_totale)