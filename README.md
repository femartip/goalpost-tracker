# Goalpost Tracker

A tiny static site (GitHub Pages–friendly) that tracks “AI will never do X / this is sci-fi” claims (usually tweets) versus what actually happened.

You add entries manually to a JSON file, and the UI renders a searchable list of cards with filters and a detail view with references.

## Live site

If GitHub Pages is enabled for this repo, the default URL is usually:

`https://femartip.github.io/goalpost-tracker/`

## How it works

- Data lives in `data/claims.json`.
- The site is plain static HTML/CSS/JS (Vite for local dev only).
- Cards show author/date/claim/status + tags.
- Clicking a card opens a detail modal with the tweet link and evidence links.

## Add a claim

Edit `data/claims.json` and add an object like:

```json
{
  "id": "2026-02-13-someone-001",
  "tweetUrl": "https://twitter.com/...",
  "author": "handle",
  "tweetDate": "2026-02-13",
  "claimText": "Exact quote from the tweet",
  "claimType": "never",
  "taxonomy": {
    "domain": "capability",
    "modality": "agents",
    "topic": ["tool-use", "planning"]
  },
  "status": "not-yet",
  "achievedDate": "",
  "lastChecked": "2026-02-13",
  "evidence": [
    {
      "url": "https://...",
      "title": "Demo/paper/news link",
      "date": "2025-01-01",
      "notes": "Short explanation of why this counts as achieved/partial/etc."
    }
  ]
}
```

Then commit and push.

## Local development

```bash
npm install
npm run dev
```

Open the printed local URL.

## Deploy on GitHub Pages

Simplest mode: repo **Settings → Pages → Deploy from a branch**, select `main` and `/ (root)`.

## Notes

This project stores the quoted claim text inside `claims.json` for reliability. The original tweet is always linked.
