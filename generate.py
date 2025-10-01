import requests
import os
import json
from datetime import date
import time 

# --- Configurazione API ---
# Legge il token HuggingFace dai secrets GitHub
HF_TOKEN = os.getenv("HF_TOKEN")
# Ritorna a 'gpt2', che è garantito essere ospitato nell'API di Inference
MODEL = "gpt2" 
API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"

# Verifica del Token
if not HF_TOKEN:
    # Uscita immediata se il token non è impostato
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
    
    # Prompt ottimizzato
    prompt = (
        f"Scrivi un oroscopo giornaliero creativo e originale per il segno {segno} alla data {oggi}. "
        f"Includi solo amore, lavoro e fortuna, in tono poetico ma chiaro, massimo 80 parole."
    )

    # Parametri per la generazione del testo (forzano la generazione e la creatività)
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 120, 
            "do_sample": True,
            "temperature": 0.9, 
            "return_full_text": False 
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                testo_grezzo = data[0]["generated_text"].strip()
                
                # Pulizia del testo generato, nel caso il modello includa il prompt (tipico di gpt2)
                if testo_grezzo.startswith(prompt):
                    testo_pulito = testo_grezzo.replace(prompt, "", 1).strip()
                else:
                    testo_pulito = testo_grezzo.strip()
                    
                oroscopi[segno] = testo_pulito if testo_pulito else testo_grezzo
            else:
                oroscopi[segno] = f"Errore: Formato risposta API inatteso. Dati: {data}"
                
        # Gestione di errori API (es. 429 Rate Limit)
        else:
            oroscopi[segno] = f"Errore API: {response.status_code} - {response.text}"
            print(f"ATTENZIONE: Errore API per {segno}. Codice: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        oroscopi[segno] = f"Errore di connessione o timeout: {e}"
        print(f"ERRORE GRAVE: Errore di connessione per {segno}: {e}")

    # Breve ritardo per non saturare l'API di Hugging Face
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
