import requests
import time

def is_token_safe(token_address, web3):
    print(f"🔎 Analyse réelle du token {token_address}...")

    try:
        # Vérification honeypot avec l'API honeypot.is
        response = requests.get(f"https://api.honeypot.is/v1/IsHoneypot?address={token_address}&chain=bsc")
        data = response.json()

        if "honeypotResult" in data and not data["honeypotResult"].get("isHoneypot", True):
            buy_tax = data["simulationResult"]["buyTax"]
            sell_tax = data["simulationResult"]["sellTax"]
            gas_used = data["simulationResult"]["gasUsed"]

            print(f"🧮 Taxes : Buy {buy_tax}% / Sell {sell_tax}% — Gas utilisé : {gas_used}")

            if buy_tax > 20 or sell_tax > 20:
                print("🚫 Taxes trop élevées. Token refusé.")
                return False

            # Vérification de liquidité
            liquidity = int(data["simulationResult"]["liquidity"])
            liquidity_bnb = web3.from_wei(liquidity, 'ether')
            print(f"💧 Liquidité détectée : {liquidity_bnb:.4f} BNB")

            if liquidity_bnb < 1:
                print("🚫 Liquidité insuffisante.")
                return False

            print("✅ Token validé ✅")
            return True
        else:
            print("❌ Token est un honeypot !")
            return False

    except Exception as e:
        print(f"⚠️ Erreur pendant l'analyse du token : {e}")
        return False
