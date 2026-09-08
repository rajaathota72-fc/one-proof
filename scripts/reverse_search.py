"""Step 2: reverse image search via SerpApi Google Lens.

Production uses a private S3 object and a 10-minute signed URL. Google Lens
can retrieve that URL without the bucket ever being public.
"""
import os
import sys
from typing import List

import requests
from dotenv import load_dotenv

load_dotenv()

SERPAPI_ENDPOINT = "https://serpapi.com/search.json"


def search_image(image_url: str) -> List[dict]:
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        raise EnvironmentError("Set SERPAPI_KEY env var (get one at serpapi.com)")
    if not image_url:
        raise EnvironmentError("Set S3_BUCKET and AWS credentials so Lens can use a private signed image URL.")

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
