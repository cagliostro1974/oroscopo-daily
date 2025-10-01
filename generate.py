import requests
import os
import json
from datetime import date
import time 

# --- Configurazione API ---
# Utilizziamo un URL API più generico per la generazione di testo.
API_URL = "https://api-inference.huggingface.co/models"
MODEL = "HuggingFaceH4/starchat-alpha" # Riprova con il modello più performante

# Legge il token HuggingFace dai secrets GitHub
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    print("[ERRORE] La variabile d'ambiente 'HF_TOKEN' non è impostata. Impossibile procedere.")
    exit(1)

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

# --- Dati di Base ---
oggi = str(date.today())
segni = [
    "Ariete", "Toro", "Gemelli", "Cancro", "Leone", "Vergine",
    "Bilancia", "Scorpione", "Sagittario", "Capricorno", "Acquario", "Pesci"
]
oroscopi = {}

# --- Funzione per la Generazione ---
for segno in segni:
    print(f"Generazione oroscopo per: {segno}...")
    
    prompt = (
        f"Scrivi un oroscopo giornaliero creativo e originale per il segno {segno} alla data {oggi}. "
        f"Includi solo amore, lavoro e fortuna, in tono poetico ma chiaro, massimo 80 parole."
    )

    # Inseriamo il modello nel payload, non nell'URL
    payload = {
        "model": MODEL, 
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 120, 
            "do_sample": True,
            "temperature": 0.9, 
            "return_full_text": False 
        }
    }
    
    try:
        # Nota: l'URL non include più il nome del modello qui
        response = requests.post(API_URL, headers=headers, json=payload) 
        
        if response.status_code == 200:
            # ... (Logica di parsing e pulizia del testo rimane la stessa)
            data = response.json()
            if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                testo_grezzo = data[0]["generated_text"].strip()
                if testo_grezzo.startswith(prompt):
                    testo_pulito = testo_grezzo.replace(prompt, "", 1).strip()
                else:
                    testo_pulito = testo_grezzo.strip()
                oroscopi[segno] = testo_pulito if testo_pulito else testo_grezzo
            else:
                oroscopi[segno] = f"Errore: Formato risposta API inatteso. Dati: {data}"
                
        else:
            print(f"ATTENZIONE: Errore API per {segno}. Codice: {response.status_code}. Risposta: {response.text}")
            oroscopi[segno] = f"Errore API: {response.status_code} - {response.text}"
            
    except requests.exceptions.RequestException as e:
        oroscopi[segno] = f"Errore di connessione o timeout: {e}"
        print(f"ERRORE GRAVE: Errore di connessione per {segno}: {e}")

    time.sleep(1) 

# --- Salvataggio in JSON ---
filename = "oroscopo.json"
try:
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    data = {}
except json.JSONDecodeError:
    print("[ATTENZIONE] Il file oroscopo.json è corrotto o vuoto. Creazione di un nuovo file.")
    data = {}

data[oggi] = oroscopi

with open(filename, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("[OK] oroscopo.json aggiornato con successo.")
