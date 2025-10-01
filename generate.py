import os
import json
from datetime import date
from google import genai
from google.genai.errors import APIError
import time

# --- Configurazione API ---
# La chiave viene letta automaticamente dalla variabile d'ambiente GEMINI_API_KEY
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("[ERRORE] La variabile d'ambiente 'GEMINI_API_KEY' non è impostata. Impossibile procedere.")
    exit(1)

# Inizializzazione del client Gemini
try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    # Cattura errori nell'inizializzazione del client
    print(f"[ERRORE] Impossibile inizializzare il client Gemini: {e}")
    exit(1)

# Modello consigliato: Gemini 2.5 Flash, veloce ed economico
MODEL = "gemini-2.5-flash" 

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
        f"Scrivi un oroscopo giornaliero creativo e originale per il segno {segno} per oggi, {oggi}. "
        f"Includi solo Amore, Lavoro e Fortuna, in tono poetico ma chiaro. Non usare più di 80 parole."
    )

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[prompt],
            config={
                "temperature": 0.9, # Aumenta la creatività del testo
            }
        )
        
        # Estrai il testo generato
        testo = response.text.strip()
        oroscopi[segno] = testo
        
    except APIError as e:
        # Gestisce errori API
        print(f"ATTENZIONE: Errore API Gemini per {segno}: {e}")
        oroscopi[segno] = f"Errore API Gemini: {e}"
        
    except Exception as e:
        # Gestisce altri errori imprevisti
        print(f"ERRORE GRAVE per {segno}: {e}")
        oroscopi[segno] = f"Errore Imprevisto: {e}"

    # Breve ritardo per evitare problemi di rate limit
    time.sleep(1) 

# --- Salvataggio in JSON ---
filename = "oroscopo.json"
try:
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    data = {}
except json.JSONDecodeError:
    # Se il file esiste ma è vuoto o corrotto
    print("[ATTENZIONE] Il file oroscopo.json è corrotto o vuoto. Creazione di un nuovo file.")
    data = {}

data[oggi] = oroscopi

with open(filename, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("[OK] oroscopo.json aggiornato con successo.")
