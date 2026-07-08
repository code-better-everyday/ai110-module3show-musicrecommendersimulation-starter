# Plan: Phase 2 — Designing the Simulation (~45 mins)

## What the PDF Requires

| Step | What to do | Status |
|---|---|---|
| Step 1: Define Your Data | Expand songs.csv with 5–10 new songs (diverse genres/moods not yet present) | Done |
| Step 2: Create a User Profile | Define a concrete taste-profile dictionary with favorite_genre, favorite_mood, target_energy | Done |
| Step 3: Sketch Recommendation Logic | Finalize Algorithm Recipe with weights (+2.0 genre, +1.0 mood, energy proximity) | Done in Phase 1 |
| Step 4: Visualize the Design | Data flow: Input → Process (loop + score) → Output (top-k ranking) | Done in Phase 1 |
| Step 5: Document Your Plan | Write finalized Algorithm Recipe + potential biases in README.md "How The System Works" | Done |

---

## Context

Phase 1 established our algorithm recipe (+2.0 genre, +1.0 mood, +up to 1.0 energy proximity, +0.5 acoustic bonus) and wrote the "How The System Works" section in README.md. Phase 2 is still design-only — no implementation code yet. The goal is to have a complete, expanded dataset and a fully documented design (including bias analysis) before Phase 3 coding begins.

---

## Step 1: Expand `data/songs.csv`

**Original catalog (10 songs):** pop, lofi, rock, ambient, jazz, indie pop, synthwave. Moods: happy, chill, intense, relaxed, moody, focused.

**Gaps filled:** Added rnb, folk, edm, country, metal, classical, hiphop, electronic. New moods: romantic, sad, euphoric, angry, dreamy.

**10 new songs added (ids 11–20):**

| id | title | artist | genre | mood | energy | tempo_bpm | valence | danceability | acousticness |
|---|---|---|---|---|---|---|---|---|---|
| 11 | Golden Hour | Kali Uchis | rnb | romantic | 0.55 | 95 | 0.82 | 0.72 | 0.41 |
| 12 | Rainy Window | Acoustic Soul | folk | sad | 0.22 | 68 | 0.30 | 0.38 | 0.94 |
| 13 | Bass Drop City | DVBBS | edm | euphoric | 0.97 | 140 | 0.88 | 0.92 | 0.03 |
| 14 | Mountain Echo | Pine Ridge | country | relaxed | 0.40 | 88 | 0.70 | 0.55 | 0.80 |
| 15 | Void Protocol | NullSet | metal | angry | 0.95 | 168 | 0.20 | 0.50 | 0.05 |
| 16 | Moonlit Sonata | Clara Voss | classical | dreamy | 0.18 | 58 | 0.75 | 0.25 | 0.98 |
| 17 | Street Cipher | Lox Chatterbox | hiphop | focused | 0.72 | 95 | 0.60 | 0.85 | 0.10 |
| 18 | Neon Jungle | Pulse Theory | electronic | intense | 0.88 | 128 | 0.65 | 0.90 | 0.04 |
| 19 | Sunday Porch | Delta Bloom | folk | happy | 0.35 | 76 | 0.85 | 0.48 | 0.90 |
| 20 | Velvet Underground | Jazz Noir | jazz | moody | 0.45 | 85 | 0.42 | 0.58 | 0.72 |

**File edited:** `data/songs.csv`

---

## Step 2: Define the User Profile

**Starter `main.py` had:**
```python
user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
```
This was missing `likes_acoustic` and used the wrong key name for energy.

**Updated to:**
```python
# Phase 2 edit: Expanded the starter profile into a complete taste profile dictionary.
user_prefs = {
    "genre": "pop",           # the genre this user most wants to hear
    "mood": "happy",          # the emotional vibe the user is looking for
    "target_energy": 0.8,     # how energetic the music should feel (0.0=very calm, 1.0=very intense)
    "likes_acoustic": False,  # this user prefers produced/electronic sounds over acoustic ones
}
```

This profile (High-Energy Pop listener) can now clearly differentiate between "intense rock" and "chill lofi" because genre+mood+energy+acoustic together give four independent comparison axes.

**File edited:** `src/main.py`

---

## Step 3: Potential Biases Documented in README.md

Added a "Potential Biases in This Design" section to README.md after the data flow diagram. Three biases documented:

1. **Genre Dominance Bias** — Genre at +2.0 can carry a song to the top even when mood and energy are wrong. The system may bury well-matched songs from "wrong" genres.
2. **Small Catalog Diversity Bias** — 20 songs is too few to show meaningful recommendation diversity. Any `genre="pop"` user will always see the same 3 pop songs.
3. **Energy Gap Asymmetry (Direction Blindness)** — The formula `1.0 - abs(gap)` rewards closeness but does not know if the song is too high or too low. A genre-matching calm song could appear in a high-energy recommendation list.

**File edited:** `README.md`

---

## Files Edited in Phase 2

| File | What changed |
|---|---|
| `data/songs.csv` | Appended 10 new songs (ids 11–20) covering 8 new genres and 5 new moods |
| `src/main.py` | Updated `user_prefs` dict — added `target_energy` and `likes_acoustic`, added Phase 2 comment block |
| `README.md` | Added "Potential Biases in This Design" section with 3 documented biases |

No changes to `src/recommender.py` — that is Phase 3.

---

## Checkpoint (as per PDF)

- `data/songs.csv` has 20 rows (10 original + 10 new) with valid values in all columns.
- `src/main.py` has a complete `user_prefs` dict with all 4 fields: `genre`, `mood`, `target_energy`, `likes_acoustic`.
- `README.md` "How The System Works" includes the Algorithm Recipe AND a documented bias analysis.
- Can state clearly: "My recommender uses a 20-song catalog, scores each song on genre (+2), mood (+1), and energy proximity (+up to 1), and I expect it will over-favor genre matches because that weight is highest."

Ready for Phase 3 — Implementation.
