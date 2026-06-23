"""Generate per-language, per-format resume PDFs via pdf.co.

Reads PDFCO_KEY (secret) and RESUME_URL (live site root) from the environment,
fetches each language's print view, and writes one file per language/format:

    static_pdf/resume.{lang}.{format}.pdf   e.g. resume.en.a4.pdf

These filenames match the download links rendered in the top bar.
"""
import os
import uuid
from datetime import datetime
from pathlib import Path

import requests

API_KEY = os.environ.get("PDFCO_KEY")
SITE_URL = (os.environ.get("RESUME_URL") or "").rstrip("/")

LANGUAGES = ["en", "fr"]
FORMATS = ["A4", "Letter"]


def convert(page_url: str, paper_size: str, out_path: Path) -> Path:
    config = {
        "url": page_url,
        "margins": "5mm",
        "paperSize": paper_size,
        "orientation": "Portrait",
        "printBackground": True,
        "header": f"AUTO GENERATED {uuid.uuid4()} @ {datetime.now().isoformat()}",
        "footer": "",
        "mediaType": "print",  # uses the @media print stylesheet
        "async": False,
        "encrypt": False,
        "profiles": '{ "CustomScript": ";; " }',
    }
    resp = requests.post(
        "https://api.pdf.co/v1/pdf/convert/from/url",
        json=config,
        headers={"x-api-key": API_KEY},
        timeout=120,
    )
    resp.raise_for_status()
    pdf_url = resp.json()["url"]
    content = requests.get(pdf_url, timeout=120).content
    out_path.write_bytes(content)
    return out_path


def main() -> None:
    if not API_KEY:
        raise SystemExit("PDFCO_KEY is not set")
    if not SITE_URL:
        raise SystemExit("RESUME_URL is not set")

    out_dir = Path("static_pdf")
    out_dir.mkdir(exist_ok=True)

    for lang in LANGUAGES:
        for paper_size in FORMATS:
            page_url = f"{SITE_URL}/{lang}/"
            out = out_dir / f"resume.{lang}.{paper_size.lower()}.pdf"
            print(f"Generating {out.name} from {page_url} ({paper_size}) ...")
            convert(page_url, paper_size, out)
            print(f"  -> {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
