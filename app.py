"""Verifai — simple web UI over the pipeline (face -> web match -> soulbound badge).
Run: python app.py, then open http://127.0.0.1:5000
"""
import os
import traceback
from flask import Flask, render_template, request
from dotenv import load_dotenv

from scripts.face_id import encode_face, face_hash
from scripts.reverse_search import search_image
from scripts.blockchain_verify import mint_badge, reverify

load_dotenv()

app = Flask(__name__)
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html", result=None, error=None)

    file = request.files.get("image")
    if not file or file.filename == "":
        return render_template("index.html", result=None, error="Pick an image first.")

    image_path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(image_path)

    try:
        encoding = encode_face(image_path)
        fhash = face_hash(encoding)

        matches = search_image(image_path)
        if not matches:
            return render_template("index.html", result=None,
                                    error="No matching post found on the web for this face.")
        top = matches[0]
        post_content = f"{top['title']} | {top['snippet']}"

        token_id = mint_badge(fhash, top["url"], post_content)
        verified = reverify(token_id, fhash, top["url"], post_content)

        result = {
            "image_url": f"/static/uploads/{file.filename}",
            "face_hash": fhash,
            "match_url": top["url"],
            "match_title": top["title"],
            "token_id": token_id,
            "verified": verified,
        }
        return render_template("index.html", result=result, error=None)

    except Exception as e:
        traceback.print_exc()
        return render_template("index.html", result=None, error=str(e))


if __name__ == "__main__":
    app.run(debug=True)
