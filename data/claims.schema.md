# claims.json schema (informal)

Each entry:
- id: string (unique)
- tweetUrl: string
- author: string (handle or name)
- tweetDate: YYYY-MM-DD
- claimText: string (quote)
- claimType: one of ["sci-fi", "never", "we-would-never", "too-hard", "years-away", "other"]
- taxonomy:
  - domain: ["capability", "deployment", "safety", "governance"]
  - modality: ["text", "vision", "audio", "agents", "robotics", "multimodal", "other"]
  - topic: string[] (free tags)
- status: one of ["not-yet", "partial", "achieved", "ambiguous"]
- achievedDate: YYYY-MM-DD (optional; when status became achieved/partial)
- lastChecked: YYYY-MM-DD
- evidence: array of { url, title, date?, notes }
- notes: string (optional)
