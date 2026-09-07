# Face Identification & Blockchain Verification

HH Goa 2026 — Task 3 shortlisting submission.

End-to-end pipeline: **face scan → web/social media reverse-image search → blockchain upload & re-verification**.

## Pipeline

1. **Face identification** (`scripts/face_id.py`) — detects and encodes a face
   from an input image using `face_recognition` (dlib), producing a 128-d
   vector. The vector is hashed (SHA-256) for on-chain use; the raw
   biometric encoding never leaves the local machine.
2. **Web/social search** (`scripts/reverse_search.py`) — sends the image to
   SerpApi's Google Lens engine for a genuine reverse-image search, returning
   real matching pages/posts from the live web.
3. **Blockchain verification** (`scripts/blockchain_verify.py` +
   `contracts/Verification.sol`) — hashes the matched post (URL + title/snippet)
   and uploads `(faceHash, postHash, sourceUrl)` to a `Verification` smart
   contract. `reverify()` re-reads the on-chain record and re-hashes the
   local data to prove the record hasn't been tampered with.

`main.py` runs all three steps in order.

## Blockchain used

EVM-compatible chain via `web3.py`. Defaults to a **local Ganache/Hardhat
node** (`http://127.0.0.1:8545`) for demo purposes; point `RPC_URL` /
`PRIVATE_KEY` at a public testnet (e.g. Sepolia via Infura/Alchemy) to run
against a real chain. Only hashes and a source URL go on-chain — no raw
face data or images.

## Setup

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in keys below
```

Fill in `.env`:
- `SERPAPI_KEY` — from [serpapi.com](https://serpapi.com) (free tier works)
- `IMAGE_PUBLIC_URL` — a publicly reachable URL of the input image (Google
  Lens needs a public URL, not a local file — upload to any image host)
- `RPC_URL` / `PRIVATE_KEY` — local Ganache (`ganache`) or a testnet RPC +
  funded test-account private key
- `CONTRACT_ADDRESS` — filled after deploy (next step)

## Run

```bash
# 1. Start a local chain (or skip and point RPC_URL at a testnet)
ganache

# 2. Compile + deploy the contract, then set CONTRACT_ADDRESS in .env
python scripts/compile_contract.py
python scripts/deploy_contract.py

# 3. Run the full pipeline
python main.py sample_images/input.jpg
```

Each step is also runnable standalone:
```bash
python scripts/face_id.py sample_images/input.jpg
python scripts/reverse_search.py sample_images/input.jpg
python scripts/blockchain_verify.py <face_hash> <post_url> <post_content>
```

## Known limitations

- Google Lens (via SerpApi) requires a **publicly hosted** image URL, not a
  local file path — an extra upload step is needed before search.
- Face matching here identifies *a* face and searches the web for visually
  similar images; it is not a guaranteed identity match — reverse image
  search can return false positives (lookalikes, edited photos).
- Local Ganache chain resets on restart; for a persistent tamper-evident
  record, deploy to a public testnet (Sepolia) or mainnet.
- No UI/website — CLI pipeline only, per task requirements.
- `face_recognition`/`dlib` install can be slow on macOS/ARM; prebuilt
  wheels or `conda install -c conda-forge dlib` may be needed.
