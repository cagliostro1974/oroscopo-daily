import json, datetime, os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

oggi = datetime.date.today().isoformat()
segni = ["Ariete","Toro","Gemelli","Cancro","Leone","Vergine",
         "Bilancia","Scorpione","Sagittario","Capricorno","Acquario","Pesci"]

data = {}
for segno in segni:
    prompt = f"Scrivi un oroscopo di massimo 80 parole per il segno {segno} del giorno {oggi}. Deve includere amore, lavoro e un consiglio."
    risposta = client.chat.completions.create(
        model="gpt-4o-mini",  # modello veloce/economico
        messages=[{"role":"user","content":prompt}]
    )
    testo = risposta.choices[0].message.content.strip()
    data[segno] = testo

# Salva nel file JSON, aggiungendo la data corrente
try:
    with open("oroscopo.json","r",encoding="utf-8") as f:
        storico = json.load(f)
except:
    storico = {}

storico[oggi] = data

with open("oroscopo.json","w",encoding="utf-8") as f:
    json.dump(storico, f, ensure_ascii=False, indent=2)
