import os
import json
from datetime import date
from google import genai
from google.genai.errors import APIError
import time
import re # Usato per pulire l'intestazione e sostituire i doppi asterischi

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
        f"IMPORTANTE: NON INCLUDERE MAI IL NOME DEL SEGNO O LA DATA ALL'INIZIO DEL TESTO. NON USARE MAI GLI ASTERISCHI PER IL GRASSETTO, USA DIRETTAMENTE I TAG HTML <b> E </b>." # Istruzione extra rafforzata
    )

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[prompt],
            config={
                "temperature": 0.9,
            }
        )
        
        testo = response.text.strip()
        
        # --- LOGICA DI PULIZIA AGGIUNTA/MODIFICATA QUI ---
        
        # 1. Sostituisce i doppi asterischi (**) con i tag <b> e </b>
        # Questo cattura **parola** o **frase intera**
        # Nota: L'uso di `\*\*([^\*]+)\*\*` cerca il testo tra doppi asterischi
        testo_pulito = re.sub(r'\*\*([^\*]+)\*\*', r'<b>\1</b>', testo)

        # 2. Rimuove l'intestazione standard "Segno, Giorno Mese Anno." (come nell'ultima versione)
        pattern_data_segno = r"^[A-Z][a-z]+, \d{1,2} [A-Z][a-z]+ \d{4}\.?"
        testo_pulito = re.sub(pattern_data_segno, '', testo_pulito, 1).strip()
        
        # 3. Rimuove la prima riga se contiene solo il nome del segno
        if testo_pulito.lower().startswith(segno.lower()):
            testo_pulito = re.sub(r"^\w+\s*,?\s*", '', testo_pulito, 1).strip()
            
        # 4. Rimuove eventuali a capo residui
        testo_pulito = testo_pulito.lstrip('\n').strip()
        
        oroscopi[segno] = testo_pulito if testo_pulito else testo

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
