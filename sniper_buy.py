from web3 import Web3
import os
import json
from dotenv import load_dotenv

# Charger les variables d’environnement
load_dotenv()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")

# Fonction d’achat de token
def buy_token(token_address, pair_address, web3):
    print(f"💸 Tentative d'achat du token : {token_address}")

    router_address = Web3.toChecksumAddress("0x10ED43C718714eb63d5aA57B78B54704E256024E")  # PancakeSwap Router V2
    router_abi_path = os.path.join(os.path.dirname(__file__), 'abis', 'pancake_router_v2.json')

    with open(router_abi_path, 'r') as file:
        router_abi = json.load(file)

    router = web3.eth.contract(address=router_address, abi=router_abi)

    nonce = web3.eth.getTransactionCount(WALLET_ADDRESS)
    deadline = web3.eth.getBlock("latest")["timestamp"] + 60  # 60s

    # Montant de BNB à utiliser (0.01 BNB par exemple)
    bnb_amount = web3.toWei(0.01, 'ether')

    tx = router.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
        0,  # min amount out
        [Web3.toChecksumAddress("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"), Web3.toChecksumAddress(token_address)],
        WALLET_ADDRESS,
        deadline
    ).buildTransaction({
        'from': WALLET_ADDRESS,
        'value': bnb_amount,
        'gas': 250000,
        'gasPrice': web3.toWei('5', 'gwei'),
        'nonce': nonce
    })

    signed_tx = web3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)

    print(f"✅ Transaction envoyée ! TX Hash : {web3.toHex(tx_hash)}")