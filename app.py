"""OneProof — simple web UI over the pipeline (face -> web match -> soulbound badge).
Run: python app.py, then open http://127.0.0.1:5000
"""
import os
import traceback
from typing import Optional
from uuid import uuid4
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def upload_to_s3(image_path: str, content_type: Optional[str]) -> Optional[str]:
    """Return a 10-minute S3 URL when an upload bucket is configured."""
    bucket = os.environ.get("S3_BUCKET")
    if not bucket:
        return None

    import boto3

    prefix = os.environ.get("S3_PREFIX", "oneproof/uploads").strip("/")
    key = f"{prefix}/{os.path.basename(image_path)}"
    client = boto3.client("s3", region_name=os.environ.get("AWS_REGION"))
    client.upload_file(
        image_path,
        bucket,
        key,
        ExtraArgs={"ContentType": content_type or "application/octet-stream"},
    )
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=600,
    )


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/app")
def index():
    return render_template("index.html")


@app.route("/api/verify", methods=["POST"])
def api_verify():
    file = request.files.get("image")
    if not file or file.filename == "":
        return jsonify({"error": "Pick an image first."}), 400

    filename = f"{uuid4().hex}-{secure_filename(file.filename)}"
    image_path = os.path.join(UPLOAD_DIR, filename)
    file.save(image_path)
    connected_wallet = request.form.get("wallet_address") or None

    try:
        from scripts.face_id import encode_face, face_hash
        from scripts.reverse_search import search_image
        from scripts.blockchain_verify import mint_badge, reverify, get_web3

        encoding = encode_face(image_path)
        fhash = face_hash(encoding)

        # The S3 object stays private. Lens receives only this 10-minute
        # pre-signed URL, which restores the prior URL-based match behavior.
        s3_image_url = upload_to_s3(image_path, file.mimetype)
        matches = search_image(s3_image_url)
        if not matches:
            return jsonify({
                "error": "No public reference was found for this portrait. Try a photo that already appears on a public profile or website."
            }), 404
        top = matches[0]
        post_content = f"{top['title']} | {top['snippet']}"

        token_id = mint_badge(fhash, top["url"], post_content, recipient=connected_wallet)
        verified = reverify(token_id, fhash, top["url"], post_content)

        w3 = get_web3()
        wallet_address = connected_wallet or w3.eth.account.from_key(os.environ["PRIVATE_KEY"]).address
        contract_address = os.environ.get("CONTRACT_ADDRESS", "")

        return jsonify({
            "image_url": s3_image_url or f"/static/uploads/{filename}",
            "face_hash": fhash,
            "match_url": top["url"],
            "match_title": top["title"],
            "token_id": token_id,
            "verified": verified,
            "wallet_address": wallet_address,
            "contract_address": contract_address,
            "etherscan_url": f"https://sepolia.etherscan.io/address/{contract_address}" if contract_address else None,
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
