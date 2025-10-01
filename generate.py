import requests
import os
import json
from datetime import date

# Legge il token HuggingFace dai secrets GitHub
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL = "gpt2"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

oggi = str(date.today())

segni = [
    "Ariete", "Toro", "Gemelli", "Cancro", "Leone", "Vergine",
    "Bilancia", "Scorpione", "Sagittario", "Capricorno", "Acquario", "Pesci"
]

oroscopi = {}

for segno in segni:
    prompt = (
        f"Scrivi un oroscopo giornaliero creativo e originale per il segno {segno} alla data {oggi}. "
        f"Non usare frasi identiche per tutti i segni, non parlare di salute. "
        f"Includi solo amore, lavoro e fortuna, in tono poetico ma chiaro, massimo 80 parole."
    )

    response = requests.post(
        f"https://api-inference.huggingface.co/models/{MODEL}",
        headers=headers,
        json={"inputs": prompt}
    )

    if response.status_code == 200:
        try:
            data = response.json()
            if isinstance(data, list) and "generated_text" in data[0]:
                testo = data[0]["generated_text"].strip()
            elif isinstance(data, dict) and "generated_text" in data:
                testo = data["generated_text"].strip()
            elif isinstance(data, list) and "summary_text" in data[0]:
                testo = data[0]["summary_text"].strip()
            else:
                testo = str(data)
            oroscopi[segno] = testo
        except Exception as e:
            oroscopi[segno] = f"Errore parsing risposta: {e}"
    else:
        oroscopi[segno] = f"Errore API: {response.status_code} - {response.text}"

# Salvataggio in JSON
filename = "oroscopo.json"
try:
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    data = {}

data[oggi] = oroscopi

with open(filename, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("[OK] oroscopo.json aggiornato.")


