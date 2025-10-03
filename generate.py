import os
import json
import time
import re 
from datetime import datetime
import pytz 
from google import genai
from google.genai.errors import APIError

# --- Configurazione API ---
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("[ERRORE] La variabile d'ambiente 'GEMINI_API_KEY' non è impostata. Impossibile procedere.")
    exit(1)

try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    print(f"[ERRORE] Impossibile inizializzare il client Gemini: {e}")
    exit(1)

MODEL = "gemini-2.5-flash" 

# --- GESTIONE DEL FUSO ORARIO ---
# Calcola la data corretta in base al fuso orario di Roma (Italia)
fuso_orario_roma = pytz.timezone('Europe/Rome')
oggi_roma = datetime.now(fuso_orario_roma).date()
oggi = str(oggi_roma)
print(f"DEBUG: La data che verrà scritta nel JSON è: {oggi}")

# --- Dati di Base ---
segni = [
    "Ariete", "Toro", "Gemelli", "Cancro", "Leone", "Vergine",
    "Bilancia", "Scorpione", "Sagittario", "Capricorno", "Acquario", "Pesci"
]
oroscopi = {}

# --- Funzione per la Generazione ---
for segno in segni:
    print(f"Generazione oroscopo per: {segno}...")
    
    prompt = (
        f"Scrivi un oroscopo giornaliero per il segno {segno} per oggi. "
        f"Includi solo Amore, Lavoro e Fortuna, in tono poetico ma chiaro, massimo 80 parole."
        f"IMPORTANTE: INIZIA IL TESTO IMMEIDATAMENTE SENZA MAI INCLUDERE NOME DEL SEGNO O DATA. USA I TAG HTML <b> E </b> PER IL GRASSETTO, NON GLI ASTERISCHI."
    )

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[prompt],
            config={"temperature": 0.9}
        )
        
        testo = response.text.strip()
        
        # --- LOGICA DI PULIZIA ---
        
        # 1. Rimuove la riga di intestazione (Segno, Data)
        lines = testo.split('\n')
        if len(lines) > 1 and len(lines[0].split()) <= 7:
            testo_pulito = '\n'.join(lines[1:]).strip()
        else:
            testo_pulito = testo
            
        # 2. Sostituisce i doppi asterischi (**) con i tag <b> e </b>
        testo_pulito = re.sub(r'\*\*([^\*]+)\*\*', r'<b>\1</b>', testo_pulito)
        
        # 3. Rimuove eventuali residui di **
        testo_pulito = testo_pulito.replace('**', '').strip() 
        testo_pulito = testo_pulito.lstrip('\n').strip()
        
        oroscopi[segno] = testo_pulito if testo_pulito else testo
        
        # DEBUG per vedere il testo generato
        print(f"DEBUG: Oroscopo generato per {segno} inizia con: {oroscopi[segno][:50]}...")


    except APIError as e:
        print(f"ATTENZIONE: Errore API Gemini per {segno}: {e}")
        oroscopi[segno] = f"Errore API Gemini: {e}"
        
    except Exception as e:
        print(f"ERRORE GRAVE per {segno}: {e}")
        oroscopi[segno] = f"Errore Imprevisto: {e}"

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

