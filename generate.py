import requests
import os
import json
from datetime import date

# Legge token HuggingFace dai secrets
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL = "tiiuae/falcon-7b-instruct"

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
    prompt = f"Scrivi un oroscopo giornaliero creativo e diverso per il segno {segno} per la data {oggi}. Non ripetere frasi generiche, non scrivere sulla salute, concentrati su amore, lavoro e fortuna."
    
    response = requests.post(
        f"https://api-inference.huggingface.co/models/{MODEL}",
        headers=headers,
        json={"inputs": prompt, "parameters": {"max_new_tokens": 180}}
    )
    
    if response.status_code == 200:
        testo = response.json()[0]["generated_text"]
        oroscopi[segno] = testo.strip()
    else:
        oroscopi[segno] = "Errore nel generare l'oroscopo."

# Salva in JSON
filename = "oroscopo.json"
try:
    with open(filename, "r") as f:
        data = json.load(f)
except FileNotFoundError:
    data = {}

data[oggi] = oroscopi

with open(filename, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
