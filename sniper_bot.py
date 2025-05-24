from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv
import os
import json
import time
from sniper_buy import buy_token  # ✅ Script d'achat
from token_checker import is_token_safe  # ✅ Filtre anti-rug

# Chargement des variables d'environnement
load_dotenv()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
RPC_URL = os.getenv("RPC_URL")

# Connexion à la BSC
web3 = Web3(Web3.HTTPProvider(RPC_URL))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

if not web3.isConnected():  # ✅ Correction ici (majuscule !)
    print("❌ Connexion échouée à la blockchain.")
    exit()
else:
    print("✅ Connecté à la blockchain.")
    print(f"🔐 Wallet : {WALLET_ADDRESS}")

# Adresse WBNB (base)
base_token = Web3.toChecksumAddress("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")  # ✅ Corrigé ici

# Factory de PancakeSwap v2
factory_address = Web3.toChecksumAddress("0xCA143Ce32Fe78f1f7019d7d551a6402fC5350c73")  # ✅ Corrigé ici
factory_abi = json.loads("""[
  {
    "anonymous": false,
    "inputs": [
      {"indexed": true, "internalType": "address", "name": "token0", "type": "address"},
      {"indexed": true, "internalType": "address", "name": "token1", "type": "address"},
      {"indexed": false, "internalType": "address", "name": "pair", "type": "address"},
      {"indexed": false, "internalType": "uint256", "name": "", "type": "uint256"}
    ],
    "name": "PairCreated",
    "type": "event"
  }
]""")

factory_contract = web3.eth.contract(address=factory_address, abi=factory_abi)

def handle_event(event):
    token0 = event["args"]["token0"]
    token1 = event["args"]["token1"]
    pair_address = event["args"]["pair"]

    print(f"\n🔥 Nouvelle paire détectée !\nToken0: {token0}\nToken1: {token1}\nPair: {pair_address}")

    if token0 == base_token:
        new_token = token1
    elif token1 == base_token:
        new_token = token0
    else:
        print("❌ Aucun token WBNB détecté. Paire ignorée.")
        return

    if is_token_safe(new_token, web3):
        print("✅ Token validé. Achat en cours...")
        buy_token(new_token, pair_address, web3)
    else:
        print("🚫 Token dangereux détecté. Ignoré.")

def log_loop(poll_interval):
    print("👂 En attente de nouveaux tokens...")
    event_filter = factory_contract.events.PairCreated.create_filter(fromBlock='latest')
    while True:
        try:
            for event in event_filter.get_new_entries():
                handle_event(event)
        except Exception as e:
            print(f"⚠️ Erreur pendant l'écoute : {e}")
        time.sleep(poll_interval)

log_loop(2)