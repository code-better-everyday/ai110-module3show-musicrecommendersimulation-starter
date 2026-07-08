# Plan: Phase 1 — Understanding the Problem (~25 mins)

## What the PDF Requires

| Step | What to do |
|---|---|
| Step 1: Explore Real Recommendation Systems | Research how Spotify/YouTube predict music; understand collaborative vs content-based filtering; identify key data types |
| Step 2: Identify Key Features | Examine data/songs.csv; use AI to analyze which features are most effective for a content-based recommender |
| Step 3: Mapping the Logic | Design the "Algorithm Recipe" — scoring rule for one song + ranking rule for all songs |
| Step 4: Summarize Your Concept | Write the "How The System Works" section in README.md; list Song and UserProfile features |

---

## Context

Phase 1 is a research-and-design phase — no coding. The goal is to understand how real recommenders work, analyze the starter dataset, design an Algorithm Recipe, and document a concept sketch in README.md before any implementation begins.

Due date: Monday, July 20th at 1:59 AM CDT.

---

## Step 1 — Research: Collaborative vs Content-Based Filtering

**Collaborative filtering:** Recommends based on what similar users liked (e.g., "users who liked X also liked Y"). Needs user-behavior data: plays, skips, likes, playlist adds. Used by Spotify Discover Weekly. Fails for new users with no history (cold-start problem).

**Content-based filtering:** Recommends based on the song's own attributes — genre, tempo, mood, energy, acousticness. Only needs one user's taste profile + the song catalog. No other users' data required. This is what we are building — it mirrors Pandora's Music Genome Project approach.

**Key data types in real systems:** play count, skip rate, playlist membership, likes/dislikes, tempo (BPM), mood tags, energy level, valence (emotional positivity), acousticness, danceability, key/mode, loudness.

---

## Step 2 — Analyze `data/songs.csv`

The 10-song starter catalog has these features:

| Feature | Type | Range | Use in recommender? |
|---|---|---|---|
| genre | string | pop, lofi, rock, jazz, ambient, indie pop, synthwave | YES — strongest signal |
| mood | string | happy, chill, intense, relaxed, moody, focused | YES — secondary filter |
| energy | float | 0.0–1.0 | YES — continuous proximity score |
| acousticness | float | 0.0–1.0 | YES — acoustic bonus |
| tempo_bpm | float | 60–152 | SKIP — no UserProfile field for it |
| valence | float | 0.0–1.0 | SKIP — no UserProfile field for it |
| danceability | float | 0.0–1.0 | SKIP — no UserProfile field for it |

**Why we skip tempo/valence/danceability:** The `UserProfile` dataclass has no field for these preferences — there is nothing to compare them against without adding `target_tempo`, `target_valence`, etc. to `UserProfile`.

---

## Step 3 — Algorithm Recipe

**Scoring Rule** (judges ONE song against the user's profile):

```
score = 0.0
reasons = []

if song["genre"] == user["genre"]:
    score += 2.0
    reasons.append("genre match (+2.0)")

if song["mood"] == user["mood"]:
    score += 1.0
    reasons.append("mood match (+1.0)")

energy_gap = abs(song["energy"] - user["target_energy"])
energy_score = max(0.0, 1.0 - energy_gap)
score += energy_score
reasons.append(f"energy proximity (+{energy_score:.2f})")

if user["likes_acoustic"] and song["acousticness"] > 0.6:
    score += 0.5
    reasons.append("acoustic bonus (+0.5)")

return (score, reasons)   # max possible = 4.5
```

**Ranking Rule** (judges ALL songs, picks top-k):
Loop over every song → call score_song → sort all results by score descending → return first k items.

**Why we need both:** The Scoring Rule answers "how good is this one song?" The Ranking Rule answers "which songs are best overall?" Scoring without ranking gives raw numbers with no order. Ranking without a scoring function has nothing to sort by.

---

## Step 4 — README.md Deliverable

Wrote the full "How The System Works" section in `README.md` including:
- Plain-language explanation of collaborative vs content-based filtering
- How scoring and ranking work together
- Algorithm Recipe with all four rules documented
- Song features used and why (genre, mood, energy, acousticness)
- UserProfile fields documented (favorite_genre, favorite_mood, target_energy, likes_acoustic)
- Data flow diagram: Input → Process → Ranking → Output

---

## Files Edited in Phase 1

| File | Change |
|---|---|
| `README.md` | Filled in "How The System Works" section — concept summary, algorithm recipe, feature lists, data flow diagram |

No changes to `src/recommender.py` or `src/main.py` in Phase 1.

---

## Checkpoint (as per PDF)

- README.md "How The System Works" section is fully written (not placeholder text).
- Algorithm Recipe is documented with weights and reasoning.
- Can explain in plain language: "My recommender scores a song by checking if the genre matches (+2), if the mood matches (+1), and how close the energy level is to the user's target (+up to 1), with a small acoustic bonus (+0.5) for users who prefer unplugged sounds."
