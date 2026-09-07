"""Step 2: reverse image search via SerpApi Google Lens. Needs SERPAPI_KEY env var.

Google Lens needs a public image URL, not a local file. If IMAGE_PUBLIC_URL
isn't set, the local image is auto-uploaded to a temporary public host
(litterbox.catbox.moe, 1h expiry) so any uploaded photo works out of the box.

Swap search_image() for another provider (Bing Visual Search, PimEyes) if needed —
pipeline just needs back a list of {url, title, snippet} dicts.
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

SERPAPI_ENDPOINT = "https://serpapi.com/search.json"
LITTERBOX_ENDPOINT = "https://litterbox.catbox.moe/resources/internals/api.php"


def upload_temp_public(image_path: str) -> str:
    """Uploads a local image to a temporary public host, returns its URL."""
    with open(image_path, "rb") as f:
        resp = requests.post(
            LITTERBOX_ENDPOINT,
            data={"reqtype": "fileupload", "time": "1h"},
            files={"fileToUpload": f},
            timeout=30,
        )
    resp.raise_for_status()
    url = resp.text.strip()
    if not url.startswith("http"):
        raise RuntimeError(f"Temp upload failed: {url}")
    return url


def search_image(image_path: str) -> list[dict]:
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        raise EnvironmentError("Set SERPAPI_KEY env var (get one at serpapi.com)")

    image_url = os.environ.get("IMAGE_PUBLIC_URL") or upload_temp_public(image_path)

    params = {
        "engine": "google_lens",
        "url": image_url,
        "api_key": api_key,
    }
    resp = requests.get(SERPAPI_ENDPOINT, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    matches = []
    for visual_match in data.get("visual_matches", []):
        matches.append({
            "url": visual_match.get("link"),
            "title": visual_match.get("title"),
            "snippet": visual_match.get("source"),
        })
    return matches


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
