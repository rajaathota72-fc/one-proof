"""
Step 2: Reverse image / web search to find a matching social media post.

Uses SerpApi's Google Lens engine (https://serpapi.com/google-lens-api) for a
genuine reverse-image search against the live web — not a hardcoded result.
Requires SERPAPI_KEY env var (free tier available at serpapi.com).

Swap `search_image` for Bing Visual Search / PimEyes API if preferred; the
pipeline only needs a dict back with {url, title, snippet}.
"""
import os
import sys
import requests

SERPAPI_ENDPOINT = "https://serpapi.com/search.json"


def search_image(image_path: str) -> list[dict]:
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        raise EnvironmentError("Set SERPAPI_KEY env var (get one at serpapi.com)")

    # SerpApi Google Lens needs a public image URL, not a local file.
    # Simplest free path: upload to a temp image host first, or host the
    # image yourself and pass that URL in. Here we accept an already-public
    # URL via IMAGE_PUBLIC_URL, falling back to explaining the requirement.
    image_url = os.environ.get("IMAGE_PUBLIC_URL")
    if not image_url:
        raise EnvironmentError(
            "SerpApi Google Lens requires a public image URL. "
            "Upload sample_images/<file> somewhere public (e.g. imgur, a gist, "
            "S3 bucket) and set IMAGE_PUBLIC_URL to it."
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
