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
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET=oneproof
S3_PREFIX=oneproof/uploads
RPC_URL=
PRIVATE_KEY=
CONTRACT_ADDRESS=
```

Use a Sepolia RPC and a funded signer wallet for testnet mints. Long-running requests time out and return a retryable error. When S3_BUCKET is set, OneProof stores each upload in the private S3 bucket and gives SerpApi a 10-minute pre-signed URL.

## Deploy to Heroku

The repository includes a Procfile and runtime configuration.

    heroku create your-oneproof-app
    heroku config:set SERPAPI_KEY=... AWS_REGION=ap-south-1 AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=... S3_BUCKET=oneproof RPC_URL=... PRIVATE_KEY=... CONTRACT_ADDRESS=...
    git push heroku master

Leave `IMAGE_PUBLIC_URL` blank. In production, OneProof uploads to the private S3 bucket and shares only a 10-minute pre-signed URL with SerpApi for the Lens lookup. Local temporary files on Heroku remain ephemeral.
