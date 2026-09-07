"""Step 2: reverse image search via SerpApi Google Lens. Needs SERPAPI_KEY env var.

Swap search_image() for another provider (Bing Visual Search, PimEyes) if needed —
pipeline just needs back a list of {url, title, snippet} dicts.
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

SERPAPI_ENDPOINT = "https://serpapi.com/search.json"


def search_image(image_path: str) -> list[dict]:
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        raise EnvironmentError("Set SERPAPI_KEY env var (get one at serpapi.com)")

    # Google Lens needs a public image URL, not a local file path.
    image_url = os.environ.get("IMAGE_PUBLIC_URL")
    if not image_url:
        raise EnvironmentError(
            "Set IMAGE_PUBLIC_URL — a public URL of the image (upload it anywhere public first)"
        )

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
