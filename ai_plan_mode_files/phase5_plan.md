# Plan: Phase 5 — Polish and Submit (~30 mins)

## What the PDF Requires

| Step | What to do |
|---|---|
| Step 1: Final Code Cleanup | Review src/main.py and src/recommender.py — no broken output, no placeholder comments, clean `python -m src.main` run |
| Step 2: Write More Tests | Add 2-3 new tests to `tests/test_recommender.py` beyond the 2 starter tests |
| Step 3: Fill ai_interactions.md | Document the agentic workflow (SF8 stretch feature) — we used Claude Code throughout all 5 phases |
| Step 4: Final README Scan | Confirm zero placeholder text remaining in README.md and model_card.md |
| Step 5: Verify and Submit | `python -m src.main` clean run + `pytest` all pass + git commit + push |

---

## Context

Phases 1-4 are complete and pushed. The project runs correctly, all docs are filled, 
and 3 weight experiments are documented. Phase 5 is final polish — tests, agentic 
workflow log, last scan for gaps, and submission commit.

Key finding: `ai_interactions.md` in the project root is a stretch feature file for 
SF8 (Agentic Workflow). Since Claude Code was used as an AI agent throughout all 5 
phases making autonomous multi-step changes, SF8 applies and should be filled in.

---

## Step 1: Final Code Cleanup

Quick scan of `src/main.py` and `src/recommender.py`:
- Confirm no leftover Phase 4 experiment weight changes in `score_song()` (already verified, weights are back to 2.0/1.0)
- Confirm `print(f"Loaded songs: {len(songs)}")` in `load_songs()` is still present (required for checkpoint)
- Confirm the 4-profile loop runs clean with no UnicodeEncodeError or crash
- No changes expected — this is a verification step only

**File:** `src/recommender.py`, `src/main.py`

---

## Step 2: Write 2-3 New Tests in `tests/test_recommender.py`

Current state: 2 starter tests both passing.
- `test_recommend_returns_songs_sorted_by_score` — checks that pop/happy song ranks #1
- `test_explain_recommendation_returns_non_empty_string` — checks non-empty explanation

**3 new tests to add:**

**Test A — `test_score_song_genre_match_adds_2_points`**
Directly unit-tests `score_song()`. Create a song dict that exactly matches genre only
(mood mismatch, energy=0.0). Assert `score >= 2.0` and `"genre match" in reasons[0]`.
This verifies the genre weight is exactly 2.0.

**Test B — `test_score_song_acoustic_bonus_fires_above_threshold`**
Create a user with `likes_acoustic=True` and a song with `acousticness=0.8`. Assert
acoustic bonus fires (`score` includes the +0.5). Then repeat with `acousticness=0.5`
(below 0.6 threshold) and assert the bonus does NOT fire.

**Test C — `test_recommend_songs_returns_k_results`**
Tests `recommend_songs()` (the functional API, not the OOP class). Load a small song
list, call `recommend_songs(user_prefs, songs, k=3)`, assert `len(result) == 3` and
that results are sorted descending (result[0][1] >= result[1][1] >= result[2][1]).

**File to edit:** `tests/test_recommender.py`

---

## Step 3: Fill `ai_interactions.md` (Stretch Feature SF8)

The file currently has empty placeholder sections. SF8 (Agentic Workflow) applies
because Claude Code was used as an AI agent making autonomous multi-step changes 
across all 5 phases.

**Content to fill in:**

**What task did you give the agent?**
Complete the entire Music Recommender Simulation assignment across 5 phases — from 
designing the algorithm, expanding the dataset, implementing all scoring functions, 
building the CLI output, running multi-profile evaluations, running weight experiments,
and writing all documentation (README.md, model_card.md).

**Prompts used:**  
Key prompts from each phase:
- "plan for Phase 1" / "approve this plan, finish Phase 1 deliverables"  
- "plan for Phase 2" / "approve and execute Phase 2"
- "plan for Phase 3" / "approve and execute Phase 3"  
- "I want to see genre, mood, energy of recommended songs — add verbose output"  
- "there's a disconnect between the score sub-scores and total — plan mode"  
- "plan for Phase 4" / "document findings in README and model_card"
- "what happens if we reduce genre weight and raise mood weight — run 4 profiles"

**What did the agent generate or change?**
- `src/recommender.py`: implemented `load_songs()`, `score_song()`, `recommend_songs()`, `Recommender.recommend()`, `Recommender.explain_recommendation()`
- `src/main.py`: complete verbose CLI output with 4-profile loop, Score Breakdown block, normalized 0-10 scoring
- `data/songs.csv`: expanded from 10 to 20 songs
- `README.md`: all sections filled including Algorithm Recipe, bias analysis, 3 output design overrides, sample outputs for all 4 profiles, 3 experiment write-ups, Limitations, Reflection
- `model_card.md`: all 9 sections filled with real content
- `ai_plan_mode_files/`: 5 plan files saved across all phases

**What did you verify or fix manually?**
- Approved each phase plan before execution began
- Caught a UnicodeEncodeError (emoji in Windows terminal) — agent fixed by switching to ASCII
- Caught an import path error (`from recommender import` → `from src.recommender import`)
- Caught a score transparency disconnect (sub-scores didn't add up to total) — directed the fix
- Reviewed all model_card.md and README.md content for accuracy before each git push

**File to edit:** `ai_interactions.md`

---

## Step 4: Final README and model_card.md Scan

Check for any remaining placeholder text:
- README.md "Project Summary" — filled ✅
- README.md "How The System Works" — filled ✅  
- README.md "Sample Recommendation Output" — filled ✅
- README.md "Output Design Overrides" — filled ✅
- README.md "Experiments You Tried" — filled (3 experiments) ✅
- README.md "Limitations and Risks" — filled ✅
- README.md "Reflection" — filled ✅
- model_card.md sections 1-9 — filled ✅

No changes expected — this is a scan only.

---

## Step 5: Verification and Submission Commit

1. `python -m src.main` — confirm 4 profiles print cleanly, no errors
2. `python -m pytest` — confirm all tests pass (currently 2, will be 5 after Step 2)
3. `git add tests/test_recommender.py ai_interactions.md`
4. `git commit` with message: "Phase 5: add 3 tests + fill ai_interactions.md SF8 agentic workflow"
5. `git push`

---

## Files to Edit in Phase 5

| File | What changes |
|---|---|
| `tests/test_recommender.py` | Add 3 new tests: score_song genre weight, acoustic bonus threshold, recommend_songs k-results |
| `ai_interactions.md` | Fill SF8 Agentic Workflow section with prompts, changes, and verification notes |
| `ai_plan_mode_files/phase5_plan.md` | Save this plan |

No changes to `src/recommender.py`, `src/main.py`, `README.md`, or `model_card.md` expected.

---

## Verification Checklist (per PDF)

- [ ] `python -m src.main` prints all 4 profiles with Score Breakdown — no errors
- [ ] `pytest` — all 5 tests pass (2 original + 3 new)
- [ ] `model_card.md` — zero placeholder text remaining
- [ ] `README.md` — zero placeholder text remaining  
- [ ] `ai_interactions.md` — SF8 section filled
- [ ] Git push completed
