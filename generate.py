import requests
import os
import json
from datetime import date
import time # Aggiunto per un breve ritardo tra le chiamate API

# --- Configurazione API ---
# Legge il token HuggingFace dai secrets GitHub
HF_TOKEN = os.getenv("HF_TOKEN")
# Sostituito con gpt2-large per una generazione potenzialmente migliore
MODEL = "gpt2-large" 
API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"

# Verifica del Token
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

    # Parametri per la generazione del testo (forzano la generazione)
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 120, # Genera fino a 120 token extra (circa 80 parole)
            "do_sample": True,
            "temperature": 0.9, # Rende il testo più creativo
            "return_full_text": False # I modelli "solo decoder" come gpt2 tendono a ripetere il prompt
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            # La risposta è sempre una lista, prendiamo il primo elemento
            if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                testo_grezzo = data[0]["generated_text"].strip()
                
                # Rimuove il prompt se il modello lo ha ripetuto (anche con return_full_text=False)
                if testo_grezzo.startswith(prompt):
                    testo_pulito = testo_grezzo.replace(prompt, "", 1).strip()
                else:
                    testo_pulito = testo_grezzo.strip()
                    
                # Aggiunge il risultato. Se la pulizia lascia la stringa vuota, usa il testo grezzo.
                oroscopi[segno] = testo_pulito if testo_pulito else testo_grezzo
            else:
                oroscopi[segno] = f"Errore: Formato risposta API inatteso. Dati: {data}"
                
        # Gestione di un potenziale errore di rate limit (codice 429) o altri errori
        else:
            oroscopi[segno] = f"Errore API: {response.status_code} - {response.text}"
            print(f"ATTENZIONE: Errore API per {segno}. Codice: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        oroscopi[segno] = f"Errore di connessione o timeout: {e}"
        print(f"ERRORE GRAVE: Errore di connessione per {segno}: {e}")

    # Introduce un piccolo ritardo per evitare problemi di Rate Limit con Hugging Face
    time.sleep(1) 

# --- Salvataggio in JSON ---
filename = "oroscopo.json"
try:
    # Tenta di leggere il file esistente per mantenere i dati precedenti
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    # Se il file non esiste, inizia con un dizionario vuoto
    data = {}
except json.JSONDecodeError:
    # Se il file esiste ma è corrotto/vuoto, inizia con un dizionario vuoto e avvisa
    print("[ATTENZIONE] Il file oroscopo.json è corrotto o vuoto. Creazione di un nuovo file.")
    data = {}

# Aggiorna il dizionario con gli oroscopi del giorno
data[oggi] = oroscopi

# Scrive il dizionario aggiornato nel file JSON
with open(filename, "w", encoding="utf-8") as f:
    # Utilizza ensure_ascii=False per gestire correttamente i caratteri accentati italiani
    json.dump(data, f, indent=2, ensure_ascii=False)

print("[OK] oroscopo.json aggiornato con successo.")
