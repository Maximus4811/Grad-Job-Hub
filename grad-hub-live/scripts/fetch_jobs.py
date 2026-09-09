"""
Grad Hub live job fetcher.

Pulls current UK graduate / entry-level listings from two free, legitimate
job-search APIs (Reed and Adzuna) across four sectors, tags them, dedupes
them, and writes the combined result to data/jobs.json.

Run by the GitHub Actions workflow on a schedule. Needs three secrets set
in the repo (Settings -> Secrets and variables -> Actions):
  REED_API_KEY
  ADZUNA_APP_ID
  ADZUNA_APP_KEY

Both APIs are free to sign up for:
  Reed:   https://www.reed.co.uk/developers/jobseeker
  Adzuna: https://developer.adzuna.com/
"""
import os
import json
import time
import requests
from datetime import datetime, timezone

REED_API_KEY = os.environ.get("REED_API_KEY", "")
ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.environ.get("ADZUNA_APP_KEY", "")

# Search terms per sector. Kept broad but qualified with "graduate" /
# "entry level" so senior roles don't flood the results.
SECTOR_QUERIES = {
    "aero": [
        "graduate aerospace engineer",
        "graduate defence engineer",
        "entry level aerospace",
    ],
    "auto": [
        "graduate automotive engineer",
        "graduate manufacturing engineer automotive",
    ],
    "mfg": [
        "graduate manufacturing engineer",
        "graduate process engineer",
        "graduate production engineer",
    ],
    "fin": [
        "graduate data analyst",
        "graduate finance scheme",
        "graduate data scientist",
    ],
}

HEADERS_UA = {"User-Agent": "grad-hub-live/1.0 (personal job tracker)"}


def fetch_reed(query, sector, results_per_query=25):
    """Reed API: https://www.reed.co.uk/developers/jobseeker"""
    if not REED_API_KEY:
        return []
    jobs = []
    url = "https://www.reed.co.uk/api/1.0/search"
    params = {
        "keywords": query,
        "locationName": "UK",
        "graduate": "true",
        "resultsToTake": results_per_query,
    }
    try:
        resp = requests.get(
            url, params=params, auth=(REED_API_KEY, ""), headers=HEADERS_UA, timeout=20
        )
        resp.raise_for_status()
        data = resp.json()
        for j in data.get("results", []):
            jobs.append({
                "id": f"reed-{j.get('jobId')}",
                "title": j.get("jobTitle"),
                "company": j.get("employerName"),
                "location": j.get("locationName"),
                "url": j.get("jobUrl"),
                "salary_min": j.get("minimumSalary"),
                "salary_max": j.get("maximumSalary"),
                "posted_date": j.get("date"),
                "source": "Reed",
                "sector": sector,
            })
    except requests.RequestException as e:
        print(f"[reed] {query!r} failed: {e}")
    return jobs


def fetch_adzuna(query, sector, results_per_query=25):
    """Adzuna API: https://developer.adzuna.com/"""
    if not (ADZUNA_APP_ID and ADZUNA_APP_KEY):
        return []
    jobs = []
    url = "https://api.adzuna.com/v1/api/jobs/gb/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results_per_query,
        "what": query,
        "content-type": "application/json",
    }
    try:
        resp = requests.get(url, params=params, headers=HEADERS_UA, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        for j in data.get("results", []):
            jobs.append({
                "id": f"adzuna-{j.get('id')}",
                "title": j.get("title"),
                "company": (j.get("company") or {}).get("display_name"),
                "location": (j.get("location") or {}).get("display_name"),
                "url": j.get("redirect_url"),
                "salary_min": j.get("salary_min"),
                "salary_max": j.get("salary_max"),
                "posted_date": j.get("created"),
                "source": "Adzuna",
                "sector": sector,
            })
    except requests.RequestException as e:
        print(f"[adzuna] {query!r} failed: {e}")
    return jobs


def dedupe(jobs):
    seen = set()
    out = []
    for j in jobs:
        key = (
            (j.get("title") or "").strip().lower(),
            (j.get("company") or "").strip().lower(),
            (j.get("location") or "").strip().lower(),
        )
        if key in seen or not j.get("title"):
            continue
        seen.add(key)
        out.append(j)
    return out


def main():
    all_jobs = []
    for sector, queries in SECTOR_QUERIES.items():
        for q in queries:
            all_jobs.extend(fetch_reed(q, sector))
            time.sleep(0.5)
            all_jobs.extend(fetch_adzuna(q, sector))
            time.sleep(0.5)

    all_jobs = dedupe(all_jobs)
    all_jobs.sort(key=lambda j: j.get("posted_date") or "", reverse=True)

    output = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "count": len(all_jobs),
        "jobs": all_jobs,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/jobs.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(all_jobs)} jobs to data/jobs.json")


if __name__ == "__main__":
    main()
