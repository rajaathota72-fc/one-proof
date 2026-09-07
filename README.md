# Face Identification & Blockchain Verification

HH Goa 2026 — Task 3.

Pipeline: face scan → find matching post on web → upload hash to blockchain → re-verify.

## Steps

1. `scripts/face_id.py` — detects face, encodes it (128-d vector), hashes it (SHA-256).
2. `scripts/reverse_search.py` — reverse image search via SerpApi Google Lens, finds a real matching post.
3. `scripts/blockchain_verify.py` + `contracts/Verification.sol` — hashes the matched post, uploads (faceHash, postHash, url) on-chain, then re-reads it to confirm no tampering.

`main.py` runs all three in order.

## Blockchain

EVM chain via web3.py. Defaults to local Ganache (`http://127.0.0.1:8545`). Point `RPC_URL`/`PRIVATE_KEY` at a testnet (e.g. Sepolia) for a real chain. Only hashes + URL go on-chain, no raw images.

## Setup

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill `.env`:
- `SERPAPI_KEY` — from serpapi.com
- `IMAGE_PUBLIC_URL` — public URL of input image (Google Lens needs a public URL)
- `RPC_URL` / `PRIVATE_KEY` — local Ganache or testnet + funded key
- `CONTRACT_ADDRESS` — set after deploy

## Run

```bash
ganache                              # local chain
python scripts/compile_contract.py
python scripts/deploy_contract.py    # copy address into .env
python main.py sample_images/input.jpg
```

Steps also run standalone:
```bash
python scripts/face_id.py sample_images/input.jpg
python scripts/reverse_search.py sample_images/input.jpg
python scripts/blockchain_verify.py <face_hash> <post_url> <post_content>
```

## Limitations

- Google Lens needs a public image URL, not a local file.
- Reverse search can return false positives (lookalikes, edited photos) — not guaranteed identity match.
- Local Ganache resets on restart; use a testnet for persistent record.
- CLI only, no website (per task requirements).
- dlib install can be slow on macOS/ARM.
