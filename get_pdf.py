"""Generate per-language, per-format resume PDFs via pdf.co.

Reads PDFCO_KEY (secret) and RESUME_URL (live site root) from the environment,
fetches each language's print view, and writes one file per language/format:

    static_pdf/resume.{lang}.{format}.pdf   e.g. resume.en.a4.pdf

These filenames match the download links rendered in the top bar.
"""
import os
import time
import uuid
from datetime import datetime
from pathlib import Path

import requests

API_KEY = os.environ.get("PDFCO_KEY")
SITE_URL = (os.environ.get("RESUME_URL") or "").rstrip("/")

LANGUAGES = ["en", "fr"]
FORMATS = ["A4", "Letter"]

CONVERT_URL = "https://api.pdf.co/v1/pdf/convert/from/url"
JOB_CHECK_URL = "https://api.pdf.co/v1/job/check"

# pdf.co renders the live page headless; a page that pulls remote fonts
# (Google Fonts + FontAwesome) can outlast the *synchronous* endpoint's gateway
# timeout and come back as HTTP 408. Async mode submits the job and we poll for
# the result, which avoids that timeout entirely.
MAX_ATTEMPTS = 3
JOB_MAX_SECONDS = 300
JOB_POLL_INTERVAL = 5


def _wait_for_job(job_id: str) -> str:
    """Poll pdf.co until the async job resolves; return the result PDF URL."""
    deadline = time.monotonic() + JOB_MAX_SECONDS
    while time.monotonic() < deadline:
        resp = requests.get(
            JOB_CHECK_URL,
            params={"jobid": job_id},
            headers={"x-api-key": API_KEY},
            timeout=60,
        )
        resp.raise_for_status()
        body = resp.json()
        status = (body.get("status") or "").lower()
        if status == "success":
            if body.get("url"):
                return body["url"]
            result = body.get("result")
            if isinstance(result, list) and result:
                return result[0]["url"]
            if isinstance(result, dict):
                return result["url"]
            raise RuntimeError(
                f"pdf.co job {job_id} succeeded but returned no URL: {body}"
            )
        if status == "failed":
            raise RuntimeError(f"pdf.co job {job_id} failed: {body}")
        time.sleep(JOB_POLL_INTERVAL)
    raise TimeoutError(
        f"pdf.co job {job_id} did not finish within {JOB_MAX_SECONDS}s"
    )


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
        "async": True,         # avoids the synchronous endpoint's 408 gateway timeout
        "encrypt": False,
        "profiles": '{ "CustomScript": ";; " }',
    }
    last_err = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            resp = requests.post(
                CONVERT_URL,
                json=config,
                headers={"x-api-key": API_KEY},
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            job_id = data.get("jobId")
            # Async returns a jobId to poll; fall back to a direct URL if not.
            pdf_url = _wait_for_job(job_id) if job_id else data["url"]
            content = requests.get(pdf_url, timeout=120).content
            out_path.write_bytes(content)
            return out_path
        except Exception as exc:  # retry transient pdf.co hiccups (timeouts, 5xx)
            last_err = exc
            print(f"  attempt {attempt}/{MAX_ATTEMPTS} failed: {exc}")
            time.sleep(5 * attempt)
    raise RuntimeError(
        f"Could not generate {out_path.name} after {MAX_ATTEMPTS} attempts: {last_err}"
    )


def main() -> None:
    if not API_KEY:
        raise SystemExit("PDFCO_KEY is not set")
    if not SITE_URL:
        raise SystemExit("RESUME_URL is not set")

    out_dir = Path("static_pdf")
    out_dir.mkdir(exist_ok=True)

    for lang in LANGUAGES:
        for paper_size in FORMATS:
            page_url = f"{SITE_URL}/{lang}/print/"
            out = out_dir / f"resume.{lang}.{paper_size.lower()}.pdf"
            print(f"Generating {out.name} from {page_url} ({paper_size}) ...")
            convert(page_url, paper_size, out)
            print(f"  -> {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
