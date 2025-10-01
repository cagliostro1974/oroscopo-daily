import requests
import os
import json
from datetime import date

# Legge token HuggingFace dai secrets
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL = "HuggingFaceH4/zephyr-7b-beta"

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
    try:
        data = response.json()
        # Alcuni modelli ritornano una lista di dict con 'generated_text'
        if isinstance(data, list) and "generated_text" in data[0]:
            testo = data[0]["generated_text"]
        # Altri ritornano 'generated_text' direttamente
        elif "generated_text" in data:
            testo = data["generated_text"]
        # Oppure 'generated_text' dentro 'choices' (come OpenAI)
        elif "choices" in data and "text" in data["choices"][0]:
            testo = data["choices"][0]["text"]
        else:
            testo = "Formato sconosciuto: " + str(data)
        oroscopi[segno] = testo.strip()
    except Exception as e:
        oroscopi[segno] = f"Errore parsing risposta: {e}"
else:
    oroscopi[segno] = f"Errore API HuggingFace: {response.status_code} {response.text}"

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

