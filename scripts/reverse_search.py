"""Step 2: reverse image search via SerpApi Google Lens.

The portrait is uploaded directly to SerpApi's short-lived Image API and Lens
receives the returned ``image_id``. This keeps matching independent of public
hosting, S3 permissions, and third-party image hosts.
"""
import os
import sys
from io import BytesIO
from typing import List

import requests
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

SERPAPI_ENDPOINT = "https://serpapi.com/search.json"
SERPAPI_IMAGE_ENDPOINT = "https://serpapi.com/image"
SERPAPI_MAX_IMAGE_BYTES = 500 * 1024


def upload_image_to_serpapi(image_path: str, api_key: str) -> str:
    """Upload a compressed portrait and return SerpApi's temporary image ID."""
    with Image.open(image_path) as source:
        image = source.convert("RGB")
        image.thumbnail((1600, 1600))

        image_bytes = None
        for quality in (88, 80, 72, 64, 56):
            buffer = BytesIO()
            image.save(buffer, format="JPEG", quality=quality, optimize=True)
            if buffer.tell() <= SERPAPI_MAX_IMAGE_BYTES:
                image_bytes = buffer.getvalue()
                break

    if image_bytes is None:
        raise RuntimeError("This portrait could not be prepared for visual search. Try a smaller image.")

    response = requests.post(
        SERPAPI_IMAGE_ENDPOINT,
        data={"api_key": api_key},
        files={"image": ("portrait.jpg", image_bytes, "image/jpeg")},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    image_id = payload.get("image_id")
    if not image_id:
        raise RuntimeError(payload.get("error") or "SerpApi could not prepare this portrait for search.")
    return image_id


def search_image(image_path: str) -> List[dict]:
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        raise EnvironmentError("Set SERPAPI_KEY env var (get one at serpapi.com)")

    image_id = upload_image_to_serpapi(image_path, api_key)

    def fetch_matches(match_type: str, result_group: str) -> list[dict]:
        resp = requests.get(
            SERPAPI_ENDPOINT,
            params={
                "engine": "google_lens",
                "image_id": image_id,
                "type": match_type,
                "api_key": api_key,
            },
            timeout=30,
        )
        resp.raise_for_status()
        results = []
        for match in resp.json().get(result_group, []):
            url = match.get("link")
            if url:
                results.append({
                    "url": url,
                    "title": match.get("title"),
                    "snippet": match.get("source"),
                })
        return results

    # Visual search is fast for similar images. If it returns nothing, query
    # the dedicated Exact Matches tab, where public profile references appear.
    matches = fetch_matches("visual_matches", "visual_matches")
    return matches or fetch_matches("exact_matches", "exact_matches")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python reverse_search.py <image_path>")
        sys.exit(1)

    results = search_image(sys.argv[1])
    if not results:
        print("No matches found.")
        sys.exit(0)

    print(f"Found {len(results)} matches. Top result:")
    print(results[0])
