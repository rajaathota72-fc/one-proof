"""Step 2: reverse image search via SerpApi Google Lens. Needs SERPAPI_KEY env var.

Google Lens needs a public image URL, not a local file. If IMAGE_PUBLIC_URL
isn't set, the local image is auto-uploaded to catbox.moe (permanent public
host, no key needed) so any uploaded photo works out of the box.

Swap search_image() for another provider (Bing Visual Search, PimEyes) if needed —
pipeline just needs back a list of {url, title, snippet} dicts.
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

SERPAPI_ENDPOINT = "https://serpapi.com/search.json"
CATBOX_ENDPOINT = "https://catbox.moe/user/api.php"


def upload_temp_public(image_path: str) -> str:
    """Uploads a local image to catbox.moe, returns its public URL."""
    with open(image_path, "rb") as f:
        resp = requests.post(
            CATBOX_ENDPOINT,
            data={"reqtype": "fileupload"},
            files={"fileToUpload": f},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=30,
        )
    resp.raise_for_status()
    url = resp.text.strip()
    if not url.startswith("http"):
        raise RuntimeError(f"Public upload failed: {url}")
    return url


def search_image(image_path: str, image_url: str | None = None) -> list[dict]:
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        raise EnvironmentError("Set SERPAPI_KEY env var (get one at serpapi.com)")

    image_url = image_url or os.environ.get("IMAGE_PUBLIC_URL") or upload_temp_public(image_path)

    def fetch_matches(match_type: str, result_group: str) -> list[dict]:
        resp = requests.get(
            SERPAPI_ENDPOINT,
            params={
                "engine": "google_lens",
                "url": image_url,
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
