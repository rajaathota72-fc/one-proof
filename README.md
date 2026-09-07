# Verifai — Proof of Human

HH Goa 2026 — Task 3.

Pipeline: face scan → find matching post on web → mint a soulbound "Proof-of-Human" badge → re-verify on-chain.

## Use case

**Proof-of-Human badge for dating apps, DAOs, freelance/marketplace platforms.**
User scans their face, we find a real social post matching it, then mint a
non-transferable NFT badge to their wallet as proof they're a real, findable
person — not a bot or catfish. Because it's soulbound, it can't be sold or
handed to a fake account. Any platform can check the badge on-chain instead
of trusting a screenshot, and the user only has to verify once and reuse the
badge everywhere.

## Steps

1. `scripts/face_id.py` — detects face, encodes it (128-d vector), hashes it (SHA-256).
2. `scripts/reverse_search.py` — reverse image search via SerpApi Google Lens, finds a real matching post.
3. `scripts/blockchain_verify.py` + `contracts/ProofOfHuman.sol` — mints a soulbound badge (faceHash, postHash, url) to the user's wallet, then re-reads it on-chain to confirm no tampering.

`main.py` runs all three in order.

## Blockchain

EVM chain via web3.py. `ProofOfHuman` is a minimal self-contained soulbound
token (no OpenZeppelin import — `transferFrom`/`safeTransferFrom`/`approve`
always revert, so a badge can never leave the wallet it was minted to).
Defaults to local Ganache (`http://127.0.0.1:8545`). Point `RPC_URL`/`PRIVATE_KEY`
at a testnet (e.g. Sepolia) for a real chain. Only hashes + URL go on-chain, no raw images.

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

### Web UI

```bash
python app.py
```
- `http://127.0.0.1:5000` — landing page: use cases, how it works, tech stack, "Launch App" CTA.
- `http://127.0.0.1:5000/app` — the app: connect MetaMask, upload a photo, watch the 3 steps run and the badge get minted straight to your wallet.

## Limitations

- Google Lens needs a public image URL, not a local file.
- Reverse search can return false positives (lookalikes, edited photos) — not guaranteed identity match.
- One badge per wallet (by design — re-minting to the same wallet reverts).
- Local Ganache resets on restart; use a testnet for persistent record.
- Small Flask UI included for demo purposes (task doesn't require a hosted website).
- dlib install can be slow on macOS/ARM.
