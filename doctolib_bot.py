import discord
from discord.ext import tasks
import requests
import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))



# URL de disponibilité du Dr Zbranca pour les consultations de suivi
URL_DOCTOLIB = "https://www.doctolib.fr/availabilities.json?start_date=2024-01-01&visit_motive_ids=4167122&agenda_ids=566339&insurance_sector=public&practice_ids=150936&telehealth=false"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def check_disponibilite():
    print("🕒 Vérification en cours...")
    response = requests.get(URL_DOCTOLIB, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        print("❌ Erreur lors de la requête HTTP")
        return None

    data = response.json()
    for entry in data.get("availabilities", []):
        if entry.get("slots"):
            return True
    return False

@tasks.loop(hours=3)  # Vérifie toutes les 1 minute pour le test
async def verifier_doctolib():
    dispo = check_disponibilite()
    channel = client.get_channel(CHANNEL_ID)
    if dispo is True:
        await channel.send(f"🟢 **Créneau disponible chez Dr Zbranca-Toporas !**\n{URL_DOCTOLIB}")
    elif dispo is False:
        await channel.send("🔴 Aucun créneau dispo pour le moment.")
    else:
        await channel.send("⚠️ Erreur pendant la vérification.")

@client.event
async def on_ready():
    print(f"✅ Connecté en tant que {client.user}")
    verifier_doctolib.start()

client.run(DISCORD_TOKEN)
