from flask import Flask, render_template, send_file
import json
import os
import requests
from web3 import Web3
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import io
import csv

load_dotenv()

app = Flask(__name__)
web3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
wallet_address = os.getenv("PUBLIC_KEY")
TRACKER_FILE = "wallet_tracker.json"
MEMORY_FILE = "sniper_memory.json"

TOKEN_LIST = {
    "0xe9e7cea3dedca5984780bafc599bd69add087d56": "BUSD",
    "0x55d398326f99059ff775485246999027b3197955": "USDT",
    "0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82": "CAKE",
    "0x2170ed0880ac9a755fd29b2688956bd959f933f8": "ETH",
}

def get_token_balance(token_address):
    abi = [
        {"constant": True, "inputs": [{"name": "_owner", "type": "address"}],
         "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
        {"constant": True, "inputs": [], "name": "decimals",
         "outputs": [{"name": "", "type": "uint8"}], "type": "function"}
    ]
    try:
        contract = web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=abi)
        balance = contract.functions.balanceOf(wallet_address).call()
        decimals = contract.functions.decimals().call()
        return balance / (10 ** decimals)
    except:
        return 0

def get_bnb_price():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=binancecoin&vs_currencies=usd")
        return r.json()["binancecoin"]["usd"]
    except:
        return 500

def get_level_info(gain_usd):
    if gain_usd >= 1_000_000:
        return "👑 Dieu du marché – LEVEL 5"
    elif gain_usd >= 500_000:
        return "💀 Sniper d’élite – LEVEL 4"
    elif gain_usd >= 100_000:
        return "🪾 Tireur confirmé – LEVEL 3"
    elif gain_usd >= 10_000:
        return "🧒 Recrue sérieuse – LEVEL 2"
    elif gain_usd >= 1_000:
        return "👨‍🌾 Débutant sniper – LEVEL 1"
    else:
        return "😴 Débutant endormi – LEVEL 0"

@app.route("/")
def dashboard():
    bnb_price = get_bnb_price()
    bnb_balance = float(web3.from_wei(web3.eth.get_balance(wallet_address), 'ether'))

    try:
        with open(TRACKER_FILE, "r") as f:
            open_positions = json.load(f)
    except:
        open_positions = []

    try:
        with open(MEMORY_FILE, "r") as f:
            closed_trades = json.load(f)
    except:
        closed_trades = []

    total_gain_bnb = 0
    total_loss_bnb = 0
    for t in closed_trades:
        try:
            diff = float(t["sell_price"]) - float(t["buy_price"])
            if diff >= 0:
                total_gain_bnb += diff
            else:
                total_loss_bnb += abs(diff)
        except:
            continue

    gain_usd = total_gain_bnb * bnb_price
    loss_usd = total_loss_bnb * bnb_price
    progress = min(100, (gain_usd / 1_000_000) * 100)
    level = get_level_info(gain_usd)

    try:
        with open("last_level.json", "r", encoding="utf-8") as f:
            last_level = f.read().strip()
    except:
        last_level = ""

    play_sound = level != last_level
    with open("last_level.json", "w", encoding="utf-8") as f:
        f.write(level)

    token_holdings = []
    for addr, symbol in TOKEN_LIST.items():
        bal = get_token_balance(addr)
        if bal > 0:
            token_holdings.append({"symbol": symbol, "amount": bal})

    return render_template("index_matrix.html",
                       bnb_balance=bnb_balance,
                       bnb_price=bnb_price,
                       token_holdings=token_holdings,
                       open_positions=open_positions,
                       closed_trades=closed_trades,
                       total_gain_bnb=total_gain_bnb,
                       gain_usd=gain_usd,
                       total_loss_bnb=total_loss_bnb,
                       loss_usd=loss_usd,
                       progress=progress,
                       level=level,
                       play_sound=play_sound)

@app.route("/plot.png")
def plot_png():
    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []
    x = list(range(1, len(data)+1))
    y = [float(d["gain"]) * 100 for d in data]
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(x, y, marker='o', linestyle='-', linewidth=2, markersize=6, color='#00ffcc')
    ax.fill_between(x, y, 0, where=[v >= 0 for v in y], color='#00ffcc', alpha=0.1)
    ax.axhline(y=0, color='red', linestyle='--', linewidth=1)
    ax.set_title("Performance des trades", fontsize=14, color='white')
    ax.set_xlabel("Trade #", fontsize=10)
    ax.set_ylabel("Gain (%)", fontsize=10)
    ax.grid(True, linestyle=':', linewidth=0.5, alpha=0.5)
    plt.tight_layout()
    output = io.BytesIO()
    plt.savefig(output, format="png", dpi=100)
    output.seek(0)
    return send_file(output, mimetype='image/png')

@app.route("/export")
def export_csv():
    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []

    path = "export_trades.csv"
    with open(path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Token", "Gain (%)", "Buy Price", "Sell Price"])
        for row in data:
            writer.writerow([
                row["token"],
                round(float(row["gain"]) * 100, 2),
                row["buy_price"],
                row["sell_price"]
            ])
    return send_file(path, as_attachment=True)

@app.route("/victory.mp3")
def victory():
    return send_file("victory.mp3", mimetype='audio/mpeg')

if __name__ == "__main__":
    print("\u2705 Dashboard lanc\u00e9 avec succ\u00e8s")
    app.run(debug=True)