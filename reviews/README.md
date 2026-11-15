# Review Records

`reviews/<id>/` holds the reviews of an article, exported from its thread, so that they outlive
the discussion platform and travel with the article's archive copy.

`reviews/<id>/status.yml` is the article's review state, which every version's page shows:

```yaml
status: Review open        # Review open | Reviewed | Retracted
thread: ""                 # the address of the review thread
retraction: ""             # the reason, when retracted
reviews: []                # - {reviewer: "Name", date: YYYY-MM-DD, version: 1, url: "https://..."}
```

After changing it, run `python scripts/journal.py record <id>`. No published version changes.

| Article | Review thread | Status |
|---|---|---|
| `2026-001` | https://github.com/Hertzforge/journal/discussions/1 | Review open |
| `2026-002` | https://github.com/Hertzforge/journal/discussions/2 | Review open |
| `2026-003` | https://github.com/Hertzforge/journal/discussions/3 | Review open |
| `2026-004` | https://github.com/Hertzforge/journal/discussions/4 | Review open |
