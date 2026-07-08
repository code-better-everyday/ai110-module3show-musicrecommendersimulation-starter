# 🎵 Music Recommender Simulation

## Project Summary

This project simulates a content-based music recommendation system — the same approach used by platforms like Pandora — where songs are scored against a user's taste profile rather than relying on what other users listened to. The system loads a 20-song catalog from a CSV file, scores every song using a weighted Algorithm Recipe (genre match +2.0, mood match +1.0, energy proximity up to +1.0, acoustic bonus +0.5), ranks all songs from highest to lowest score, and prints the top-k recommendations in the terminal with a full Score Breakdown showing exactly why each song ranked where it did. Match scores are displayed on a normalized 0–10 scale so results are immediately readable without knowing the raw point maximum. The project also includes a model card documenting intended use, known biases (genre dominance, small catalog diversity, energy direction blindness), and ideas for future improvement.

---

## How The System Works

Real-world music platforms like Spotify and Pandora use two main strategies to decide what to play next. The first is **collaborative filtering**, which looks at what millions of other users with similar listening habits enjoyed — it does not care about the song itself at all, only about patterns in user behavior across a massive database of plays, skips, likes, and saves. The second is **content-based filtering**, which looks at the actual attributes of the song — its genre, mood, energy level, tempo, acousticness — and finds other songs with similar characteristics. Our simulation uses **content-based filtering** because it only requires a catalog of songs and a single user's taste profile; it does not need any behavioral data from other users.

Our version works by representing every song as a set of measurable attributes and representing the user as a "taste profile" — a collection of target values for those same attributes. To generate a recommendation, the system scores every song in the catalog by comparing its attributes to the user's preferences. Songs that match more strongly get higher scores. Once every song has a numeric score, the system sorts the entire catalog from highest to lowest and returns the top results. This two-step process — first scoring, then ranking — mirrors exactly how production recommenders work at a simplified scale.

### How the scoring works (Algorithm Recipe)

Each song earns points based on how well it matches the user's preferences:

- **Genre match (+2.0 points):** If the song's genre exactly matches the user's favorite genre, it earns 2 points. Genre is weighted the highest because it is the strongest signal of whether a listener will enjoy a track. A jazz fan is unlikely to enjoy a metal song regardless of its energy or mood.
- **Mood match (+1.0 point):** If the song's mood tag exactly matches the user's favorite mood, it earns 1 point. Mood is a secondary filter — it refines within a genre. A "chill pop" user should rank higher than a "happy pop" user for chill songs even if genre matches.
- **Energy proximity (up to +1.0 point):** Energy is a continuous value from 0.0 to 1.0. Rather than penalizing a song just for having high or low energy, the system rewards songs that are *close* to the user's target energy. The formula is `1.0 - abs(song_energy - target_energy)`. A perfect match gives +1.0; a gap of 0.5 gives +0.5; a gap of 1.0 gives 0.0. This rewards nearness, not just high or low values.
- **Acoustic bonus (+0.5 points, optional):** If the user prefers acoustic music (`likes_acoustic = True`) and the song has an acousticness score above 0.6, the song earns a small bonus. This lets the profile capture a nuance that genre alone cannot express.

**Maximum possible score: 4.5 points.**

The ranking rule is separate from the scoring rule: after every song has a score, the system sorts the full list in descending order and returns the top-k results to the user. The scoring function judges one song; the ranking function finds the best across all songs.

### Song features used in this system

Each `Song` object uses the following attributes from `data/songs.csv`:

- `genre` — the musical genre (e.g., pop, lofi, rock, jazz, ambient, indie pop, synthwave)
- `mood` — the emotional tag (e.g., happy, chill, intense, relaxed, moody, focused)
- `energy` — a float from 0.0 to 1.0 representing how energetic the track feels (0 = very calm, 1 = very intense)
- `acousticness` — a float from 0.0 to 1.0 indicating how acoustic vs. produced the track is (1 = fully acoustic, 0 = fully electronic)

The remaining song attributes (`tempo_bpm`, `valence`, `danceability`) are present in the dataset but not yet used in scoring because the `UserProfile` has no corresponding preference fields to compare them against. They are available for future improvement.

### What the UserProfile stores

The `UserProfile` object captures a listener's taste preferences:

- `favorite_genre` — the genre the user most wants to hear (string, e.g., `"pop"`)
- `favorite_mood` — the mood the user is in the mood for (string, e.g., `"happy"`)
- `target_energy` — how energetic the user wants the music to be (float 0.0–1.0, e.g., `0.8` for high energy)
- `likes_acoustic` — whether the user prefers acoustic-sounding tracks (boolean, `True` or `False`)

### Data flow summary

```
Input: UserProfile (favorite_genre, favorite_mood, target_energy, likes_acoustic)
         |
         v
Process: For each Song in catalog → score_song(user, song) → (numeric score, reasons list)
         |
         v
Ranking: Sort all (song, score, reasons) tuples from highest to lowest score
         |
         v
Output:  Top-k recommendations printed with title, score, and explanation
```

### Potential Biases in This Design

<!-- Phase 2 edit: Added bias analysis as required by Phase 2 Step 5. The assignment asks
     us to document expected biases in the Algorithm Recipe before we start coding, so we
     know what to look for when we evaluate the system in Phase 4. -->

Every scoring algorithm bakes in assumptions, and those assumptions become biases when they do not match reality. Here are the three most significant biases we expect in this design:

**1. Genre Dominance Bias.** Genre is worth +2.0 points — twice as much as mood (+1.0) and twice as much as a perfect energy match (+1.0). This means a song that matches the genre but gets everything else wrong (wrong mood, opposite energy, no acoustic match) will still score 2.0 points, while a song that matches mood, has near-perfect energy, and hits the acoustic bonus but misses on genre will only score 2.4 points. In practice this means the recommender will almost never surface a song from the "wrong" genre even if it perfectly captures the user's energy and vibe. A user who says "pop" might actually enjoy a well-matched indie or rnb track that feels exactly like what they want — but our system will bury it below any pop song regardless of fit.

**2. Small Catalog Diversity Bias.** With only 20 songs in the catalog, most user profiles will trigger the same top-3 results regardless of small differences in preferences. For example, any user with `genre="pop"` will always see "Sunrise City", "Gym Hero", and "Rooftop Lights" near the top because those are the only pop songs in the dataset. The catalog is simply too small to demonstrate meaningful diversity in recommendations. Real systems work across millions of tracks — at 20 songs, genre alone is a near-deterministic filter.

**3. Energy Gap Asymmetry (Direction Blindness).** The energy proximity formula `1.0 - abs(song_energy - target_energy)` rewards closeness but does not distinguish between *direction*. A user who wants calm music (`target_energy = 0.2`) will score "Moonlit Sonata" (energy 0.18) at +0.98 and "Sunrise City" (energy 0.82) at only +0.38 — which is correct behavior. However, a user who wants very high energy (`target_energy = 0.95`) and a low-energy chill song (`energy = 0.2`) will score that song at +0.25 on energy alone. If it genre-matches, it could still appear in the top results. The formula does not "know" that the user is asking for something more energetic — it only knows the gap, not whether the song is too high or too low. This could lead to surprisingly quiet songs appearing in "intense" recommendation lists if the genre label matches.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Output Design Overrides

After the initial Phase 3 implementation produced working output, two user-requested changes were made to improve readability. These are documented here because they represent deliberate design decisions that go beyond the starter spec, and they affect how the output should be interpreted.

**Override 1 — Match score moved to the song title line.**

In the first version of the output, the score appeared on its own `Score:` line below the song title. This meant a reader's eye had to travel down past the artist name before seeing the most important number. The override moves the match score directly onto the title line as `[ Match: X / 10 ]` so it is the first thing read after the song name. This mirrors how apps like Spotify or YouTube surface a "relevance" signal right next to the content item rather than in a secondary detail row.

Before:
```
  #1  Sunrise City  -  Neon Echo
       Score   : 3.98 / 4.50
       Why     : genre match (+2.0), mood match (+1.0), energy proximity (+0.98)
```

After:
```
  #1  Sunrise City  -  Neon Echo  [ Match: 8.8 / 10 ]
       Why     : genre match (+2.0), mood match (+1.0), energy proximity (+0.98)
```

**Override 2 — Score normalized from raw 0–4.5 to a 0–10 scale.**

The raw score output (`3.98 / 4.50`) is accurate but not intuitive — a reader cannot tell at a glance whether 3.98 is a strong or weak match without knowing that 4.5 is the maximum. Normalizing to a 0–10 scale makes the score self-explanatory: `8.8 / 10` immediately reads as "strong match" and `2.1 / 10` immediately reads as "weak match." The normalization formula is:

```
normalized_score = (raw_score / 4.5) * 10
```

This is a display-only transformation — the internal scoring logic in `score_song()` is unchanged and still uses the raw 0–4.5 scale. Only `main.py` applies the normalization before printing. The score values stored in each `(song, score, reasons)` tuple remain in the original scale so the ranking order is unaffected.

**Override 3 — Score Breakdown block replaces the single "Why" line.**

An earlier version showed `Why: genre match (+2.0), mood match (+1.0), energy proximity (+0.98)` alongside a total of `8.8 / 10`. This created a visible disconnect: the sub-scores (+2.0, +1.0, +0.98) added up to 3.98, but the displayed total was 8.8 — because the normalization was applied to the total but not to the components. A reader who tried to add up the "Why" numbers could not reach the displayed Match score.

The fix replaces the "Why" line with a full Score Breakdown table. Each component is shown with both its raw points and its normalized contribution to the /10 total, followed by a divider row showing the raw-to-normalized conversion explicitly. Now the sub-scores visibly add up to the Match total:

```
  Score Breakdown:
    Genre match            +2.00 pts  ->  4.4 / 10
    Mood match             +1.00 pts  ->  2.2 / 10
    Energy proximity       +0.98 pts  ->  2.2 / 10
    ----------------------------------------
    Total                   3.98 / 4.5  =  8.8 / 10
```

`4.4 + 2.2 + 2.2 = 8.8` — the math is now fully traceable end-to-end. The Genre and Mood lines also gained inline match indicators (`(matches your preference)` vs `(your preference: pop)`) so the reader sees which attributes matched before reading the breakdown numbers.

---

## Sample Recommendation Output

The following is the actual terminal output produced by running `python -m src.main` from the project root with the default "High-Energy Pop" user profile (`genre=pop, mood=happy, energy=0.8, acoustic=False`). The output reflects all three output design overrides documented above: match score on the title line normalized to 0–10, inline match indicators on Genre and Mood, and a full Score Breakdown block where sub-scores visibly add up to the Match total. The catalog has 20 songs.

```
Loaded songs: 20

======================================================
   *** MUSIC RECOMMENDER  --  Let's get going! ***
======================================================

  YOUR TASTE PROFILE
  ------------------------------------------------------
  Preferred genre   : POP
  Preferred mood    : Happy
  Target energy     : 0.8 (high energy)
  Likes acoustic    : No - prefers produced/electronic sounds
  Catalog size      : 20 songs

  TOP 5 RECOMMENDATIONS
  ------------------------------------------------------

  #1  Sunrise City  -  Neon Echo  [ Match: 8.8 / 10 ]
       Genre   : Pop          (matches your preference)
       Mood    : Happy        (matches your preference)
       Energy  : 0.82 (high)

       Score Breakdown:
         Genre match            +2.00 pts  ->  4.4 / 10
         Mood match             +1.00 pts  ->  2.2 / 10
         Energy proximity       +0.98 pts  ->  2.2 / 10
         ----------------------------------------
         Total                   3.98 / 4.5  =  8.8 / 10

  #2  Gym Hero  -  Max Pulse  [ Match: 6.4 / 10 ]
       Genre   : Pop          (matches your preference)
       Mood    : Intense      (your preference: happy)
       Energy  : 0.93 (high)

       Score Breakdown:
         Genre match            +2.00 pts  ->  4.4 / 10
         Energy proximity       +0.87 pts  ->  1.9 / 10
         ----------------------------------------
         Total                   2.87 / 4.5  =  6.4 / 10

  #3  Rooftop Lights  -  Indigo Parade  [ Match: 4.4 / 10 ]
       Genre   : Indie pop    (your preference: pop)
       Mood    : Happy        (matches your preference)
       Energy  : 0.76 (high)

       Score Breakdown:
         Mood match             +1.00 pts  ->  2.2 / 10
         Energy proximity       +0.96 pts  ->  2.1 / 10
         ----------------------------------------
         Total                   1.96 / 4.5  =  4.4 / 10

  #4  Sunday Porch  -  Delta Bloom  [ Match: 3.4 / 10 ]
       Genre   : Folk         (your preference: pop)
       Mood    : Happy        (matches your preference)
       Energy  : 0.35 (low)

       Score Breakdown:
         Mood match             +1.00 pts  ->  2.2 / 10
         Energy proximity       +0.55 pts  ->  1.2 / 10
         ----------------------------------------
         Total                   1.55 / 4.5  =  3.4 / 10

  #5  Night Drive Loop  -  Neon Echo  [ Match: 2.1 / 10 ]
       Genre   : Synthwave    (your preference: pop)
       Mood    : Moody        (your preference: happy)
       Energy  : 0.75 (high)

       Score Breakdown:
         Energy proximity       +0.95 pts  ->  2.1 / 10
         ----------------------------------------
         Total                   0.95 / 4.5  =  2.1 / 10

======================================================
```

**Reading the output:** "Sunrise City" scores 8.8/10 — the sub-scores `4.4 + 2.2 + 2.2 = 8.8` add up exactly, making the math fully traceable. "Gym Hero" drops to 6.4/10 despite matching genre because it misses the mood match entirely and has slightly lower energy proximity. "Rooftop Lights" at #3 is indie pop (genre miss, no genre points) yet still scores 4.4/10 purely from mood + energy — this is the genre dominance bias visible in the output: the #2 song with a genre match scores 6.4 while the #3 song without one scores only 4.4, a gap of 2.0 points that corresponds exactly to the genre weight.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



