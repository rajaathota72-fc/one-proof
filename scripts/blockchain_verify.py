"""
Step 3: Blockchain upload + re-verification.

Connects via web3.py to an EVM chain (default: local Ganache/Hardhat node,
or a public testnet like Sepolia if RPC_URL/PRIVATE_KEY point there),
uploads sha256 hashes of the face encoding + matched post to the
Verification contract, then re-reads them back to prove tamper-evidence.
"""
import os
import json
import hashlib
import sys
from web3 import Web3

CONTRACT_ABI_PATH = os.path.join(os.path.dirname(__file__), "..", "build", "Verification.abi.json")


def get_web3() -> Web3:
    rpc_url = os.environ.get("RPC_URL", "http://127.0.0.1:8545")  # local Ganache/Hardhat default
    w3 = Web3(Web3.HTTPProvider(rpc_url))
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


def upload_record(face_hash_hex: str, post_url: str, post_content: str) -> int:
    w3 = get_web3()
    contract = get_contract(w3)

    account = w3.eth.account.from_key(os.environ["PRIVATE_KEY"])
    post_hash_hex = sha256_hex(post_url + post_content)

    tx = contract.functions.addRecord(
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
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    record_id = contract.functions.totalRecords().call() - 1
    print(f"Uploaded. tx: {tx_hash.hex()}  record_id: {record_id}")
    return record_id


def reverify(record_id: int, face_hash_hex: str, post_url: str, post_content: str) -> bool:
    w3 = get_web3()
    contract = get_contract(w3)
    post_hash_hex = sha256_hex(post_url + post_content)
    matched = contract.functions.verify(
        record_id,
        bytes.fromhex(face_hash_hex),
        bytes.fromhex(post_hash_hex),
    ).call()
    print(f"Re-verification against on-chain record {record_id}: {'MATCH' if matched else 'MISMATCH'}")
    return matched


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python blockchain_verify.py <face_hash_hex> <post_url> <post_content>")
        sys.exit(1)

    face_hash_hex, post_url, post_content = sys.argv[1], sys.argv[2], sys.argv[3]
    rid = upload_record(face_hash_hex, post_url, post_content)
    reverify(rid, face_hash_hex, post_url, post_content)
