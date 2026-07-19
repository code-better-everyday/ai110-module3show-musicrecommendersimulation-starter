# Plan: Phase 4 — Evaluate and Explain (~45 mins)

## What the PDF Requires

| Step | What to do |
|---|---|
| Step 1: Stress Test with Diverse Profiles | Define 3+ distinct user profiles in main.py; add an adversarial edge-case profile; run and paste all outputs as fenced code blocks in README.md or model_card.md |
| Step 2: Look for Accuracy and Surprises | Compare at least one profile's results to musical intuition; explain why a specific song ranked first |
| Step 3: Run a Small Data Experiment | Change weights (double energy, halve genre) OR remove mood check; run and document what changed |
| Step 4: Identify Bias and Limitations | Document filter bubbles / biases in model_card.md Limitations section (3-5 sentences) |
| Step 5: Document Your Evaluation | Fill model_card.md Evaluation section with profiles tested, surprises, and per-pair comparison comments |

---

## Context

Phase 3 built a working recommender with one default profile (pop/happy/energy=0.8).
Phase 4 stress-tests it with multiple profiles, runs one experiment to observe algorithm
sensitivity, and documents everything in model_card.md (which is currently all placeholder
text) and README.md (Experiments section still placeholder).

---

## Step 1: Three Profiles + One Adversarial in `src/main.py`

**Change:** Replace the single `user_prefs` dict + single `recommend_songs` call with a
loop over a list of named profiles. Each profile prints its own full recommendation block.

**Four profiles to define:**

```python
# Phase 4 edit: Added multiple named profiles for stress testing as required by Phase 4.
profiles = [
    {
        "name": "High-Energy Pop",
        "genre": "pop", "mood": "happy",
        "target_energy": 0.8, "likes_acoustic": False,
    },
    {
        "name": "Chill Lofi Acoustic",
        "genre": "lofi", "mood": "chill",
        "target_energy": 0.35, "likes_acoustic": True,
    },
    {
        "name": "Deep Intense Rock",
        "genre": "rock", "mood": "intense",
        "target_energy": 0.91, "likes_acoustic": False,
    },
    {
        "name": "Adversarial -- Conflicting Signals",
        # High energy EDM user who also says they like acoustic and want a sad mood.
        # These preferences actively fight each other: EDM is almost never acoustic,
        # and high-energy songs rarely carry a sad mood. This tests whether the system
        # produces reasonable or nonsensical results under conflicting inputs.
        "genre": "edm", "mood": "sad",
        "target_energy": 0.95, "likes_acoustic": True,
    },
]
```

The existing print block in `main.py` becomes a `for user_prefs in profiles:` loop.
The profile `"name"` key is printed as a sub-header before each block.

**File to edit:** `src/main.py`

---

## Step 2: Accuracy and Surprise Analysis (documented in model_card.md)

Pre-calculated outputs verified against the CSV before running:

**Profile 1 — High-Energy Pop** (genre=pop, mood=happy, energy=0.8, acoustic=False)
- Sunrise City #1: genre +2.0, mood +1.0, energy gap=0.02 → +0.98 → **3.98 raw = 8.8/10**. Intuitive.

**Profile 2 — Chill Lofi Acoustic** (genre=lofi, mood=chill, energy=0.35, acoustic=True)
- Library Rain #1: genre +2.0, mood +1.0, energy gap=0.0 → +1.0, acousticness=0.86 → +0.5 → **4.5 raw = 10.0/10** (PERFECT MATCH — great showcase for model_card.md Strengths).
- Midnight Coding #2: genre +2.0, mood +1.0, energy gap=0.07 → +0.93, acousticness=0.71 → +0.5 → **4.43 raw = 9.8/10**.

**Profile 3 — Deep Intense Rock** (genre=rock, mood=intense, energy=0.91, acoustic=False)
- Storm Runner #1: genre +2.0, mood +1.0, energy gap=0.0 → +1.0 → **4.0 raw = 8.9/10**. Intuitive.

**Profile 4 — Adversarial: Conflicting Signals** (genre=edm, mood=sad, energy=0.95, acoustic=True)
- Bass Drop City #1: genre +2.0, mood miss (euphoric ≠ sad), energy gap=0.02 → +0.98, acousticness=0.03 < 0.6 (acoustic bonus blocked) → **2.98 raw = 6.6/10**.
- **Surprise result: Rainy Window (folk/sad) ranks #2** — genre miss, mood=sad ✓ +1.0, acousticness=0.94 → +0.5, energy gap=0.73 → +0.27 → **1.77 raw = 3.9/10**. A quiet folk ballad outranks high-energy metal because mood+acoustic_bonus outweighs energy proximity. This is the adversarial insight: the system produces a logically consistent but musically nonsensical result — "I want EDM but I'm sad and like acoustic" surfaces a soft folk song at #2.

**Document this in model_card.md section 7 (Evaluation) as the key surprise finding.**

---

## Step 3: Weight Shift Experiment in `src/recommender.py`

**The experiment:** Halve the genre weight (2.0 → 1.0) and double the energy weight
(cap of 1.0 → cap of 2.0, by multiplying energy_score by 2). This directly tests the
genre dominance bias we documented in Phase 2.

```python
# Phase 4 experiment: Weight shift — halved genre, doubled energy.
# Original: genre=2.0, energy=up to 1.0
# Experiment: genre=1.0, energy=up to 2.0
# Expected: songs with close energy but wrong genre start outranking genre-matches
# with poor energy. This tests whether genre dominance is a design choice or a flaw.
if song["genre"] == user_prefs["genre"]:
    score += 1.0          # was 2.0
    reasons.append("genre match (+1.0)")

energy_score = max(0.0, 1.0 - energy_gap) * 2   # was * 1.0, max now 2.0
```

**MAX_SCORE stays 4.5** — genre(1.0) + mood(1.0) + energy(2.0 max) + acoustic(0.5) = 4.5 even with the redistribution. Normalization in `main.py` is unaffected.

After running the experiment, **revert** `score_song` back to the original weights
(2.0 genre, 1.0 energy max) and document the finding in README.md Experiments section
and model_card.md. We do NOT leave the weights changed permanently.

**File to edit temporarily:** `src/recommender.py` (then revert)

---

## Step 4 & 5: Fill `model_card.md`

All 9 sections are currently placeholder text. Fill them all in Phase 4:

| Section | Content |
|---|---|
| 1. Model Name | "VibeFinder 1.0" |
| 2. Intended Use | Content-based recommender for classroom exploration; assumes user can express genre/mood/energy preferences |
| 3. How the Model Works | Plain-language explanation of scoring (no code): genre match, mood match, energy nearness, acoustic bonus |
| 4. Data | 20 songs, 12 genres, 9 moods; manually expanded from 10; missing lyrics/language, tempo preferences, release decade |
| 5. Strengths | Works well for clear single-genre profiles; Score Breakdown makes reasoning transparent; energy proximity handles continuous values better than binary match |
| 6. Limitations and Bias | Genre dominance (2.0 weight), small catalog (only 1-3 songs per genre), energy direction blindness, no temporal/mood-history awareness |
| 7. Evaluation | 4 profiles tested (High-Energy Pop, Chill Lofi Acoustic, Deep Intense Rock, Adversarial Conflicting); weight shift experiment results; per-pair comparisons |
| 8. Future Work | Add tempo/valence preferences to UserProfile; implement diversity penalty for same-artist results; expand catalog; add collaborative filtering layer |
| 9. Personal Reflection | Fill in after running experiments |

Also update **README.md "Experiments You Tried"** section with the weight-shift experiment
results (before/after ranking comparison for the pop profile).

---

## Files to Edit in Phase 4

| File | What changes |
|---|---|
| `src/main.py` | Replace single profile with loop over 4 named profiles; add profile name sub-header |
| `src/recommender.py` | Temporarily apply weight shift experiment, capture output, then revert weights |
| `model_card.md` | Fill all 9 sections with real content (currently all placeholder) |
| `README.md` | Fill "Experiments You Tried" section with weight-shift experiment results |
| `ai_plan_mode_files/phase4_plan.md` | Save this plan |

---

## Verification (Checkpoint per PDF)

1. `python -m src.main` shows 4 separate recommendation blocks — one per profile, each with the full Score Breakdown.
2. All 4 profiles produce different #1 results (if same song appears at top of every list, genre weight is too strong — the weight-shift experiment will demonstrate this).
3. `model_card.md` has real content in all 9 sections — no placeholder prompts remaining.
4. `README.md` "Experiments You Tried" has at least one documented experiment with before/after output.
5. `pytest` still passes — weight experiment is reverted before committing.
