# Plan: Phase 3 — Implementation (~90 mins)

## What the PDF Requires

| Step | What to do | Status |
|---|---|---|
| Step 1: Set Up Project Files | Implement `load_songs()` — CSV reader with numeric type casting | Done |
| Step 2: Implement Scoring Function | Implement `score_song()` — Algorithm Recipe returning (score, reasons) | Done |
| Step 3: Build Recommender Function | Implement `recommend_songs()` — score all, sort, return top-k | Done |
| Step 3b: OOP Class Methods | Implement `Recommender.recommend()` and `Recommender.explain_recommendation()` for test suite | Done |
| Step 4: CLI Verification | Update main.py output format, run app, paste output in README.md | Done |
| Step 5: Document | Add Phase 3 comments + 1-line docstrings to all functions | Done |

---

## Context

Phases 1 and 2 were complete before starting Phase 3:
- 20-song catalog in `data/songs.csv`
- Finalized Algorithm Recipe: +2.0 genre, +1.0 mood, +up to 1.0 energy proximity, +0.5 acoustic bonus
- Complete `user_prefs` dict in `src/main.py`
- Full design + bias analysis in `README.md`

All three functions in `src/recommender.py` were stubs returning empty values. Phase 3 implemented all of them.

---

## What Was Implemented

### `load_songs(csv_path)` — `src/recommender.py`
- Uses `csv.DictReader` to read the CSV with headers as dict keys
- Explicitly casts all numeric fields to their correct Python types (`int` for id, `float` for energy/tempo_bpm/valence/danceability/acousticness)
- Prints "Loaded songs: N" for verification
- Returns a list of dicts

### `score_song(user_prefs, song)` — `src/recommender.py`
- Rule 1: Genre match → +2.0 ("genre match (+2.0)")
- Rule 2: Mood match → +1.0 ("mood match (+1.0)")
- Rule 3: Energy proximity → `max(0.0, 1.0 - abs(song_energy - target_energy))` up to +1.0
- Rule 4: Acoustic bonus → +0.5 if `likes_acoustic=True` and `acousticness > 0.6`
- Returns `(score: float, reasons: List[str])`
- Maximum possible score: 4.5

### `recommend_songs(user_prefs, songs, k=5)` — `src/recommender.py`
- Calls `score_song` on every song in the catalog
- Joins reasons list into a comma-separated explanation string
- Uses `sorted()` (not `.sort()`) to avoid mutating the original songs list
- Returns `ranked[:k]` as `(song_dict, score, explanation)` tuples

### `Recommender.recommend(user, k)` — `src/recommender.py`
- Converts `UserProfile` dataclass to dict and each `Song` dataclass to dict
- Calls `score_song` for each, sorts by score descending
- Returns original `Song` dataclass instances (not dicts) so tests can access `.genre`, `.mood`

### `Recommender.explain_recommendation(user, song)` — `src/recommender.py`
- Same dict-conversion approach as `recommend()`
- Calls `score_song`, joins reasons into "Recommended because: ..." string
- Falls back to "No strong match found — included for variety." if reasons list is empty

---

## Files Edited in Phase 3

| File | What changed |
|---|---|
| `src/recommender.py` | Added `import csv`; implemented all 5 stubs with Phase 3 comments and docstrings |
| `src/main.py` | Fixed import to `src.recommender`; added user profile header; improved output formatting with rank numbers and artist names; added Phase 3 comments |
| `README.md` | Replaced placeholder "Sample Recommendation Output" with actual terminal output as a fenced code block, plus explanation of the results |

---

## Actual App Output (default pop/happy profile)

```
Loaded songs: 20

User profile: genre=pop, mood=happy, energy=0.8, acoustic=False

Top recommendations:

  1. Sunrise City by Neon Echo
     Score: 3.98 | genre match (+2.0), mood match (+1.0), energy proximity (+0.98)

  2. Gym Hero by Max Pulse
     Score: 2.87 | genre match (+2.0), energy proximity (+0.87)

  3. Rooftop Lights by Indigo Parade
     Score: 1.96 | mood match (+1.0), energy proximity (+0.96)

  4. Sunday Porch by Delta Bloom
     Score: 1.55 | mood match (+1.0), energy proximity (+0.55)

  5. Night Drive Loop by Neon Echo
     Score: 0.95 | energy proximity (+0.95)
```

---

## Test Results

```
tests/test_recommender.py::test_recommend_returns_songs_sorted_by_score PASSED
tests/test_recommender.py::test_explain_recommendation_returns_non_empty_string PASSED

2 passed in 0.08s
```

---

## Checkpoint (as per PDF)

- `python -m src.main` prints "Loaded songs: 20" then top 5 results with scores and reasons.
- Top result for pop/happy/energy=0.8 profile is "Sunrise City" (score 3.98) — correct.
- Both starter tests pass.
- README.md "Sample Recommendation Output" has actual terminal output as a fenced code block.

Ready for Phase 4 — Evaluate and Explain.
