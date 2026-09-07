"""Step 3: mint a soulbound Proof-of-Human badge for the verified match,
then re-read on-chain to confirm no tampering. RPC_URL defaults to local Ganache.
"""
import os
import json
import hashlib
import sys
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

CONTRACT_ABI_PATH = os.path.join(os.path.dirname(__file__), "..", "build", "ProofOfHuman.abi.json")


def get_web3() -> Web3:
    rpc_url = os.environ.get("RPC_URL", "http://127.0.0.1:8545")  # local Ganache/Hardhat default
    w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 20}))
    if not w3.is_connected():
        raise ConnectionError(f"Cannot connect to chain at {rpc_url}")
    return w3


def get_contract(w3: Web3):
    contract_address = os.environ["CONTRACT_ADDRESS"]
    with open(CONTRACT_ABI_PATH) as f:
        abi = json.load(f)
    return w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=abi)


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def mint_badge(face_hash_hex: str, post_url: str, post_content: str, recipient: str = None) -> int:
    """Mints the Proof-of-Human badge to `recipient` (defaults to the signing wallet).
    Gas is always paid by the backend signer, even when the badge goes to a
    connected MetaMask address, so the user never needs test ETH themselves.
    """
    w3 = get_web3()
    contract = get_contract(w3)

    account = w3.eth.account.from_key(os.environ["PRIVATE_KEY"])
    to_address = Web3.to_checksum_address(recipient) if recipient else account.address
    post_hash_hex = sha256_hex(post_url + post_content)

    tx = contract.functions.mint(
        to_address,
        bytes.fromhex(face_hash_hex),
        bytes.fromhex(post_hash_hex),
        post_url,
    ).build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 300_000,
        "gasPrice": w3.eth.gas_price,
    })

    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    # A pending testnet transaction must never leave the web request open
    # indefinitely. The caller receives a clear retryable error after 75 s.
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=75, poll_latency=2)
    if receipt.status != 1:
        raise RuntimeError("The mint transaction was reverted on-chain.")

    token_id = contract.functions.nextTokenId().call() - 1
    print(f"Badge minted. tx: {tx_hash.hex()}  token_id: {token_id}  owner: {to_address}")
    return token_id


def reverify(token_id: int, face_hash_hex: str, post_url: str, post_content: str) -> bool:
    w3 = get_web3()
    contract = get_contract(w3)
    post_hash_hex = sha256_hex(post_url + post_content)
    matched = contract.functions.verify(
        token_id,
        bytes.fromhex(face_hash_hex),
        bytes.fromhex(post_hash_hex),
    ).call()
    print(f"Re-verification against on-chain badge {token_id}: {'MATCH' if matched else 'MISMATCH'}")
    return matched


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python blockchain_verify.py <face_hash_hex> <post_url> <post_content>")
        sys.exit(1)

    face_hash_hex, post_url, post_content = sys.argv[1], sys.argv[2], sys.argv[3]
    tid = mint_badge(face_hash_hex, post_url, post_content)
    reverify(tid, face_hash_hex, post_url, post_content)
