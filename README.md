# OneProof

OneProof turns a face photo into a reusable Proof-of-Human badge.

## Architecture

```text
Browser
  └─ Flask UI
       ├─ face_id.py           → detects and hashes the face
       ├─ reverse_search.py    → finds a matching public web post
       └─ blockchain_verify.py → mints and verifies a soulbound badge
                                      ↓
                              Sepolia / EVM contract
```

The browser connects a wallet. The backend signs the mint transaction and sends the non-transferable badge to that wallet. Only hashes and the matched post reference are stored on-chain.

## Run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open:

- `http://127.0.0.1:5000` — landing page
- `http://127.0.0.1:5000/app` — verification and minting flow

## Environment

Create a `.env` with:

```text
SERPAPI_KEY=
IMAGE_PUBLIC_URL=
RPC_URL=
PRIVATE_KEY=
CONTRACT_ADDRESS=
```

Use a Sepolia RPC and a funded signer wallet for testnet mints. Long-running requests time out and return a retryable error.
