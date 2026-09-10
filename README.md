# Grad Hub Live - https://maximus4811.github.io/Grad-Job-Hub/

A self-updating UK graduate job tracker: a GitHub Action pulls live listings
from the Reed and Adzuna job APIs on a schedule, writes them to `data/jobs.json`,
and a static site (hosted free on GitHub Pages) displays them, plus a
"predicted opening windows" table and a per-listing tracker.

## Setup (about 10 minutes)

### 1. Create the repo
Create a new **public** GitHub repository (Pages' free tier needs public,
unless you have GitHub Pro/Team) and push all these files to it, keeping the
folder structure exactly as given:
```
.github/workflows/update-jobs.yml
scripts/fetch_jobs.py
data/jobs.json
index.html
README.md
```

### 2. Get free API keys
- **Reed**: sign up at https://www.reed.co.uk/developers/jobseeker — you get
  an API key instantly, no approval wait.
- **Adzuna**: sign up at https://developer.adzuna.com/ — gives you an
  `app_id` and `app_key`, free tier is generous.

You can run with just one of the two if you only get around to one signup;
the script skips whichever isn't configured.

### 3. Add the keys as repo secrets
In your repo: **Settings → Secrets and variables → Actions → New repository secret**.
Add three secrets:
- `REED_API_KEY`
- `ADZUNA_APP_ID`
- `ADZUNA_APP_KEY`

### 4. Turn on GitHub Pages
**Settings → Pages → Build and deployment → Source: Deploy from a branch →
Branch: `main`, folder: `/ (root)`**. Save. Your site will be live at
`https://<your-username>.github.io/<repo-name>/` within a minute or two.

### 5. Run the workflow once manually
**Actions tab → "Update job listings" → Run workflow**. This does the first
fetch so `data/jobs.json` isn't empty. After that it runs automatically every
day at 06:15 UTC (edit the `cron` line in
`.github/workflows/update-jobs.yml` to change the schedule).

## What you get
- **Live listings tab** — real, current graduate/entry-level roles across
  Aerospace & Defence, Automotive, Manufacturing, and Finance & Data, pulled
  fresh daily.
- **Predicted opening windows tab** — a static reference table of when large
  employers typically open/close grad-scheme applications, since most job
  boards don't list a role until the day it opens.
- **My tracker tab** — click "+ Track" on any live listing to add it to your
  personal tracker with a stage dropdown (Not started → Researching →
  Applied → Interview/AC → Offer). Saved in your browser via localStorage,
  so it's private to you and persists between visits on the same device.

## Extending it
- Add more search terms per sector in `scripts/fetch_jobs.py` (`SECTOR_QUERIES`).
- Add more companies/windows to the `PREDICTED` array in `index.html`.
- Want it to also search specific named companies rather than generic
  keywords? Reed's API supports an `employerId` filter — ask if you want
  that wired in.
