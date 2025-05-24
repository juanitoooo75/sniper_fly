import os
import time
import requests
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_KEY = os.getenv("PUBLIC_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

web3 = Web3(Web3.HTTPProvider(RPC_URL))

def check_rpc():
    if not web3.is_connected():
        print("❌ Connexion RPC échouée. Vérifie RPC_URL dans .env")
        return False
    print("✅ RPC connecté avec succès.")
    return True

def get_balance():
    try:
        balance_wei = web3.eth.get_balance(PUBLIC_KEY)
        return web3.from_wei(balance_wei, "ether")
    except Exception as e:
        print(f"❌ Erreur récupération solde : {e}")
        return None

def send_telegram_alert(new_balance):
    message = (
        f"🚨 <b>ALERTE SÉCURITÉ</b>\n"
        f"❌ <b>Retrait non autorisé détecté !</b>\n"
        f"💰 Nouveau solde : <b>{new_balance:.6f} BNB</b>"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"❌ Erreur envoi Telegram : {e}")

if __name__ == "__main__":
    print("🔐 Surveillance de sécurité activée...")

    if not check_rpc():
        exit()

    last_balance = get_balance()

    while True:
        time.sleep(10)
        current = get_balance()
        if current is None:
            continue
        if current < last_balance:
            print("❌ Retrait détecté — ALERTE !")
            send_telegram_alert(current)
        last_balance = current
