# Ronstrapp Catalog — Song Entry Template

Use this format to add new songs to the catalog:

```json
{
  "id": 1,
  "title": "Song Title Here",
  "genre": "country|rock|blues|spanish|metal|pop",
  "lyrics_status": "complete|in-progress|needs-review",
  "arrangement_status": "demo|rough-mix|final|in-progress",
  "release_status": "unreleased|planned|in-production",
  "key": "C",
  "bpm": 110,
  "duration": "3:30",
  "notes": "Any notes about the song",
  "lyrics": "Link to lyrics file or paste here",
  "arrangement": "Link to audio file",
  "date_added": "2026-02-18",
  "last_updated": "2026-02-18"
}
```

---

## Genre Tags
- `country` — Country-rock, Nashville vibes
- `rock` — Classic rock, grit
- `blues` — Blues rock, soul
- `spanish` — Latin, Mexican, Spanish-language
- `metal` — Harder edge, heavy
- `pop` — Radio-friendly, polished

## Status Values

### Lyrics Status
- `in-progress` — You're writing it
- `needs-review` — Ready for you to review
- `complete` — Finalized

### Arrangement Status
- `demo` — Rough idea
- `rough-mix` — Better, needs work
- `in-progress` — AI working on it
- `final` — Ready to record

### Release Status
- `unreleased` — Not计划
- `planned` — On the roadmap
- `in-production` — Actively being worked on

---

## Quick Add Command
To add a song, tell me:
- Song title
- Genre
- Any notes

I'll add it to the catalog!
