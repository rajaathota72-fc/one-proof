"""
End-to-end pipeline:
  face scan -> web/social search -> blockchain upload + re-verification

Usage:
    python main.py sample_images/input.jpg
"""
import sys
from dotenv import load_dotenv

from scripts.face_id import encode_face, face_hash
from scripts.reverse_search import search_image
from scripts.blockchain_verify import upload_record, reverify

load_dotenv()


def run(image_path: str):
    print(f"[1/3] Encoding face from {image_path} ...")
    encoding = encode_face(image_path)
    fhash = face_hash(encoding)
    print(f"      face hash: {fhash}")

    print("[2/3] Searching web for matching post ...")
    matches = search_image(image_path)
    if not matches:
        print("No matching post found. Pipeline stops here.")
        return
    top = matches[0]
    print(f"      top match: {top['url']}  ({top['title']})")

    post_content = f"{top['title']} | {top['snippet']}"

    print("[3/3] Uploading hash record to blockchain ...")
    record_id = upload_record(fhash, top["url"], post_content)
    ok = reverify(record_id, fhash, top["url"], post_content)

    print()
    print("Pipeline complete." if ok else "Pipeline complete but verification FAILED.")
    print(f"  face_hash   = {fhash}")
    print(f"  post_url    = {top['url']}")
    print(f"  record_id   = {record_id}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <image_path>")
        sys.exit(1)
    run(sys.argv[1])
