"""
Deploys the compiled Verification contract to the chain at RPC_URL,
using the account from PRIVATE_KEY. Prints the deployed address —
set that as CONTRACT_ADDRESS for the rest of the pipeline.
"""
import json
import os
from web3 import Web3

BUILD_DIR = os.path.join(os.path.dirname(__file__), "..", "build")


def main():
    rpc_url = os.environ.get("RPC_URL", "http://127.0.0.1:8545")
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise ConnectionError(f"Cannot connect to chain at {rpc_url}")

    with open(os.path.join(BUILD_DIR, "Verification.abi.json")) as f:
        abi = json.load(f)
    with open(os.path.join(BUILD_DIR, "Verification.bin")) as f:
        bytecode = f.read()

    account = w3.eth.account.from_key(os.environ["PRIVATE_KEY"])
    Verification = w3.eth.contract(abi=abi, bytecode=bytecode)

    tx = Verification.constructor().build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 1_500_000,
        "gasPrice": w3.eth.gas_price,
    })
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"Deployed at: {receipt.contractAddress}")
    print("Set this as CONTRACT_ADDRESS in your .env")


if __name__ == "__main__":
    main()
