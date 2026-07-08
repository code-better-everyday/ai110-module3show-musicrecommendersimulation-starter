# Plan: Score Transparency Fix

## Problem

The "Why" sub-scores (+2.0, +1.0, +0.98) summed to the raw total (3.98) but the
displayed Match score was the normalized total (8.8/10). The math was invisible and
inconsistent — users could not trace how the components produced the final score.

## Fix

Changed the "Why" single line into a full Score Breakdown block showing each component
with both raw points and normalized contribution. Added a divider row showing the
raw-to-normalized conversion. Added inline match indicators on Genre and Mood lines.

## Files Changed

| File | Change |
|---|---|
| `src/recommender.py` | `recommend_songs()` stores `reasons` list instead of joined string |
| `src/main.py` | Score Breakdown block replaces "Why" line; Genre/Mood get match indicators |
| `README.md` | "Output Design Overrides" updated (Override 3 added); Sample Output refreshed |

## Result

Sub-scores now visibly add up to the Match total: 4.4 + 2.2 + 2.2 = 8.8. Tests: 2/2 pass.
