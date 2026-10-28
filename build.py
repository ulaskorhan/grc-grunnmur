"""Build the static GitHub Pages version of Grunnmur into the docs/ folder.

Run with:  .venv/bin/python build.py

How it works:
  1. Switch the Flask app into STATIC_SITE mode (no database, empty progress).
  2. Ask Flask for each page, the same way a browser would, and save the HTML.
  3. Copy the static/ folder (CSS and JavaScript) next to the pages.
GitHub Pages then serves docs/ at https://ulaskorhan.github.io/grc-grunnmur/

For a local preview of the build, use an empty base path:
  BASE_PATH= .venv/bin/python build.py
  python3 -m http.server 8000 --directory docs
"""

import os
import shutil
from pathlib import Path

import nsm_data
from app import app

# GitHub Pages serves a project site under /<repo-name>/, so every link needs that prefix.
BASE_PATH = os.environ.get("BASE_PATH", "/grc-grunnmur")
OUT = Path(__file__).parent / "docs"


def save_page(client, url, file_path):
    """Request one page from Flask and write its HTML to docs/."""
    response = client.get(url, base_url="http://localhost" + BASE_PATH)
    if response.status_code != 200:
        raise SystemExit(f"Failed to build {url}: HTTP {response.status_code}")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(response.data)
    print("built", file_path.relative_to(OUT.parent))


def main():
    app.config["STATIC_SITE"] = True

    # Start from an empty docs/ folder so old files never linger.
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    client = app.test_client()
    save_page(client, "/", OUT / "index.html")
    # Each category becomes kategori/<id>/index.html, so the URL /kategori/<id>/ works.
    for category in nsm_data.CATEGORIES:
        save_page(client, f"/kategori/{category['id']}",
                  OUT / "kategori" / category["id"] / "index.html")

    shutil.copytree(Path(__file__).parent / "static", OUT / "static")
    # Tells GitHub Pages to serve the files as they are, without Jekyll processing.
    (OUT / ".nojekyll").touch()
    print("Done. Base path:", BASE_PATH or "/")


if __name__ == "__main__":
    main()
