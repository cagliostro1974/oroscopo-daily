import requests
import os
import json
from datetime import date

# Legge il token HuggingFace dai secrets GitHub
HF_TOKEN = os.getenv("HF_TOKEN")

# Modello più stabile su HuggingFace
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
    prompt = (
        f"Scrivi un oroscopo giornaliero originale, creativo e diverso per il segno {segno} "
        f"alla data {oggi}. Non usare frasi generiche uguali per tutti i segni, "
        f"non parlare della salute. Concentrati solo su amore, lavoro e fortuna, "
        f"con tono poetico ma conciso."
    )

    response = requests.post(
        f"https://api-inference.huggingface.co/models/{MODEL}",
        headers=headers,
        json={"inputs": prompt, "parameters": {"max_new_tokens": 180}}
    )

    if response.status_code == 200:
        try:
            data = response.json()
            testo = None

            # Vari formati possibili di risposta
            if isinstance(data, list) and "generated_text" in data[0]:
                testo = data[0]["generated_text"]
            elif "generated_text" in data:
                testo = data["generated_text"]
            elif "choices" in data and "text" in data["choices"][0]:
                testo = data["choices"][0]["text"]

            if testo:
                # Togli il prompt iniziale (a volte viene incluso)
                testo = testo.replace(prompt, "").strip()
                oroscopi[segno] = testo
            else:
                oroscopi[segno] = f"Formato sconosciuto: {data}"
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
