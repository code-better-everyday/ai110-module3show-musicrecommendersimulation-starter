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

### Phase 4: All Four Profile Outputs

The following is the full terminal output from running all four profiles added in Phase 4. Each profile block is separated by a divider line and a "PROFILE N of 4" header.

```
Loaded songs: 20

======================================================
   *** MUSIC RECOMMENDER  --  Let's get going! ***
======================================================

  PROFILE 1 of 4: High-Energy Pop
  ------------------------------------------------------

  YOUR TASTE PROFILE
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

  PROFILE 2 of 4: Chill Lofi Acoustic
  ------------------------------------------------------

  YOUR TASTE PROFILE
  Preferred genre   : LOFI
  Preferred mood    : Chill
  Target energy     : 0.35 (low energy)
  Likes acoustic    : Yes - prefers unplugged/acoustic sounds
  Catalog size      : 20 songs

  TOP 5 RECOMMENDATIONS
  ------------------------------------------------------

  #1  Library Rain  -  Paper Lanterns  [ Match: 10.0 / 10 ]
       Genre   : Lofi         (matches your preference)
       Mood    : Chill        (matches your preference)
       Energy  : 0.35 (low)

       Score Breakdown:
         Genre match            +2.00 pts  ->  4.4 / 10
         Mood match             +1.00 pts  ->  2.2 / 10
         Energy proximity       +1.00 pts  ->  2.2 / 10
         Acoustic bonus         +0.50 pts  ->  1.1 / 10
         ----------------------------------------
         Total                   4.50 / 4.5  =  10.0 / 10

  #2  Midnight Coding  -  LoRoom  [ Match: 9.8 / 10 ]
       Genre   : Lofi         (matches your preference)
       Mood    : Chill        (matches your preference)
       Energy  : 0.42 (medium)

       Score Breakdown:
         Genre match            +2.00 pts  ->  4.4 / 10
         Mood match             +1.00 pts  ->  2.2 / 10
         Energy proximity       +0.93 pts  ->  2.1 / 10
         Acoustic bonus         +0.50 pts  ->  1.1 / 10
         ----------------------------------------
         Total                   4.43 / 4.5  =  9.8 / 10

  #3  Focus Flow  -  LoRoom  [ Match: 7.7 / 10 ]
       Genre   : Lofi         (matches your preference)
       Mood    : Focused      (your preference: chill)
       Energy  : 0.4 (low)

       Score Breakdown:
         Genre match            +2.00 pts  ->  4.4 / 10
         Energy proximity       +0.95 pts  ->  2.1 / 10
         Acoustic bonus         +0.50 pts  ->  1.1 / 10
         ----------------------------------------
         Total                   3.45 / 4.5  =  7.7 / 10

  #4  Spacewalk Thoughts  -  Orbit Bloom  [ Match: 5.4 / 10 ]
       Genre   : Ambient      (your preference: lofi)
       Mood    : Chill        (matches your preference)
       Energy  : 0.28 (low)

       Score Breakdown:
         Mood match             +1.00 pts  ->  2.2 / 10
         Energy proximity       +0.93 pts  ->  2.1 / 10
         Acoustic bonus         +0.50 pts  ->  1.1 / 10
         ----------------------------------------
         Total                   2.43 / 4.5  =  5.4 / 10

  #5  Sunday Porch  -  Delta Bloom  [ Match: 3.3 / 10 ]
       Genre   : Folk         (your preference: lofi)
       Mood    : Happy        (your preference: chill)
       Energy  : 0.35 (low)

       Score Breakdown:
         Energy proximity       +1.00 pts  ->  2.2 / 10
         Acoustic bonus         +0.50 pts  ->  1.1 / 10
         ----------------------------------------
         Total                   1.50 / 4.5  =  3.3 / 10

======================================================

  PROFILE 3 of 4: Deep Intense Rock
  ------------------------------------------------------

  YOUR TASTE PROFILE
  Preferred genre   : ROCK
  Preferred mood    : Intense
  Target energy     : 0.91 (high energy)
  Likes acoustic    : No - prefers produced/electronic sounds
  Catalog size      : 20 songs

  TOP 5 RECOMMENDATIONS
  ------------------------------------------------------

  #1  Storm Runner  -  Voltline  [ Match: 8.9 / 10 ]
       Genre   : Rock         (matches your preference)
       Mood    : Intense      (matches your preference)
       Energy  : 0.91 (high)

       Score Breakdown:
         Genre match            +2.00 pts  ->  4.4 / 10
         Mood match             +1.00 pts  ->  2.2 / 10
         Energy proximity       +1.00 pts  ->  2.2 / 10
         ----------------------------------------
         Total                   4.00 / 4.5  =  8.9 / 10

  #2  Gym Hero  -  Max Pulse  [ Match: 4.4 / 10 ]
       Genre   : Pop          (your preference: rock)
       Mood    : Intense      (matches your preference)
       Energy  : 0.93 (high)

       Score Breakdown:
         Mood match             +1.00 pts  ->  2.2 / 10
         Energy proximity       +0.98 pts  ->  2.2 / 10
         ----------------------------------------
         Total                   1.98 / 4.5  =  4.4 / 10

  #3  Neon Jungle  -  Pulse Theory  [ Match: 4.4 / 10 ]
       Genre   : Electronic   (your preference: rock)
       Mood    : Intense      (matches your preference)
       Energy  : 0.88 (high)

       Score Breakdown:
         Mood match             +1.00 pts  ->  2.2 / 10
         Energy proximity       +0.97 pts  ->  2.2 / 10
         ----------------------------------------
         Total                   1.97 / 4.5  =  4.4 / 10

  #4  Void Protocol  -  NullSet  [ Match: 2.1 / 10 ]
       Genre   : Metal        (your preference: rock)
       Mood    : Angry        (your preference: intense)
       Energy  : 0.95 (high)

       Score Breakdown:
         Energy proximity       +0.96 pts  ->  2.1 / 10
         ----------------------------------------
         Total                   0.96 / 4.5  =  2.1 / 10

  #5  Bass Drop City  -  DVBBS  [ Match: 2.1 / 10 ]
       Genre   : Edm          (your preference: rock)
       Mood    : Euphoric     (your preference: intense)
       Energy  : 0.97 (high)

       Score Breakdown:
         Energy proximity       +0.94 pts  ->  2.1 / 10
         ----------------------------------------
         Total                   0.94 / 4.5  =  2.1 / 10

======================================================

  PROFILE 4 of 4: Adversarial -- Conflicting Signals
  ------------------------------------------------------

  YOUR TASTE PROFILE
  Preferred genre   : EDM
  Preferred mood    : Sad
  Target energy     : 0.95 (high energy)
  Likes acoustic    : Yes - prefers unplugged/acoustic sounds
  Catalog size      : 20 songs

  TOP 5 RECOMMENDATIONS
  ------------------------------------------------------

  #1  Bass Drop City  -  DVBBS  [ Match: 6.6 / 10 ]
       Genre   : Edm          (matches your preference)
       Mood    : Euphoric     (your preference: sad)
       Energy  : 0.97 (high)

       Score Breakdown:
         Genre match            +2.00 pts  ->  4.4 / 10
         Energy proximity       +0.98 pts  ->  2.2 / 10
         ----------------------------------------
         Total                   2.98 / 4.5  =  6.6 / 10

  #2  Rainy Window  -  Acoustic Soul  [ Match: 3.9 / 10 ]
       Genre   : Folk         (your preference: edm)
       Mood    : Sad          (matches your preference)
       Energy  : 0.22 (low)

       Score Breakdown:
         Mood match             +1.00 pts  ->  2.2 / 10
         Energy proximity       +0.27 pts  ->  0.6 / 10
         Acoustic bonus         +0.50 pts  ->  1.1 / 10
         ----------------------------------------
         Total                   1.77 / 4.5  =  3.9 / 10

  #3  Void Protocol  -  NullSet  [ Match: 2.2 / 10 ]
       Genre   : Metal        (your preference: edm)
       Mood    : Angry        (your preference: sad)
       Energy  : 0.95 (high)

       Score Breakdown:
         Energy proximity       +1.00 pts  ->  2.2 / 10
         ----------------------------------------
         Total                   1.00 / 4.5  =  2.2 / 10

  #4  Velvet Underground  -  Jazz Noir  [ Match: 2.2 / 10 ]
       Genre   : Jazz         (your preference: edm)
       Mood    : Moody        (your preference: sad)
       Energy  : 0.45 (medium)

       Score Breakdown:
         Energy proximity       +0.50 pts  ->  1.1 / 10
         Acoustic bonus         +0.50 pts  ->  1.1 / 10
         ----------------------------------------
         Total                   1.00 / 4.5  =  2.2 / 10

  #5  Gym Hero  -  Max Pulse  [ Match: 2.2 / 10 ]
       Genre   : Pop          (your preference: edm)
       Mood    : Intense      (your preference: sad)
       Energy  : 0.93 (high)

       Score Breakdown:
         Energy proximity       +0.98 pts  ->  2.2 / 10
         ----------------------------------------
         Total                   0.98 / 4.5  =  2.2 / 10

======================================================
```

**Key observations across profiles:**
- Profile 2 (Chill Lofi Acoustic): Library Rain achieves **10.0/10** — the first and only perfect score in the catalog. Every preference fired: genre, mood, exact energy, and acoustic bonus.
- Profile 3 (Deep Intense Rock): Storm Runner scores 8.9/10, but the gap between #1 (8.9) and #2 (4.4) is 4.5 points — exactly the genre weight. No non-rock song can come close regardless of mood or energy.
- Profile 4 (Adversarial): Rainy Window (quiet folk ballad) outranks Void Protocol (high-energy metal) because mood=sad (+1.0) and acoustic bonus (+0.5) outweigh perfect energy proximity (+1.0). The system is rule-correct but musically nonsensical.

---

## Experiments You Tried

### Experiment 1: Weight Shift — Halve Genre, Double Energy

**Setup:** The default algorithm weights genre at +2.0 and energy proximity at a maximum of +1.0. To test whether genre dominance was actively suppressing better-vibe songs, I temporarily changed the weights to genre=+1.0 and energy max=+2.0. The maximum possible score (4.5) did not change because the redistribution is even: genre went down by 1.0 and energy went up by 1.0. This meant the 0-to-10 normalization in the display layer was also unaffected.

**Profile tested:** High-Energy Pop (genre=pop, mood=happy, energy=0.8, acoustic=False)

**Before (original weights: genre=2.0, energy max=1.0):**
```
  #1  Sunrise City    [8.8/10]   genre match +2.0, mood match +1.0, energy proximity +0.98
  #2  Gym Hero        [6.4/10]   genre match +2.0, energy proximity +0.87
  #3  Rooftop Lights  [4.4/10]   mood match +1.0, energy proximity +0.96
  #4  Sunday Porch    [3.4/10]   mood match +1.0, energy proximity +0.55
  #5  Night Drive     [2.1/10]   energy proximity +0.95
```

**After (experiment weights: genre=1.0, energy max=2.0):**
```
  #1  Sunrise City    [8.8/10]   genre match +1.00, mood match +1.00, energy proximity +1.96
  #2  Rooftop Lights  [6.5/10]   mood match +1.00, energy proximity +1.92
  #3  Gym Hero        [6.1/10]   genre match +1.00, energy proximity +1.74
  #4  Sunday Porch    [4.7/10]   mood match +1.00, energy proximity +1.10
  #5  Night Drive     [4.2/10]   energy proximity +1.90
```

**What changed:** Sunrise City stayed at #1, but Gym Hero (pop/intense, energy=0.93) and Rooftop Lights (indie pop/happy, energy=0.76) swapped positions. Under the original weights, Gym Hero ranked #2 because its genre match (+2.0) more than compensated for its mood miss and slightly higher energy. Under the new weights, Gym Hero's genre advantage shrank to +1.0, and Rooftop Lights' better mood match (+1.0) and closer energy (gap of 0.04 vs 0.13) pushed it ahead to #2 at 6.5/10 vs Gym Hero's 6.1/10.

**What this proves:** The genre weight in the original design is strong enough to keep genre-matched songs above genre-mismatched songs even when the mismatched song has a better vibe on every other dimension. A user who says "pop" might genuinely prefer Rooftop Lights (indie pop, happy, energy=0.76) over Gym Hero (pop, intense, energy=0.93) in real listening — they got the mood right and the energy right — but the original algorithm buries it at #3 because of the genre label difference. This is the genre dominance bias operating on a real output.

**The weights were reverted to the original values (genre=2.0, energy max=1.0) after the experiment.** The experiment result is documented here and in the [model card](model_card.md) for the assignment, but the production algorithm is unchanged.

---

### Experiment 2: Same Weight Shift Applied to the Adversarial Profile (Calculated)

After running Experiment 1 on the pop/happy profile, the question became: what does the same weight shift do to the adversarial "EDM / sad / acoustic" profile? The adversarial profile already produced nonsensical results under the original weights (#2 was a quiet folk ballad). Does doubling energy fix that?

**Adversarial profile:** genre=edm, mood=sad, energy=0.95, acoustic=True

**Original weights (genre=2.0, energy max=1.0):**
```
  #1  Bass Drop City  [6.6/10]   genre +2.00, energy proximity +0.98
  #2  Rainy Window    [3.9/10]   mood +1.00, energy proximity +0.27, acoustic bonus +0.50
  #3  Void Protocol   [2.2/10]   energy proximity +1.00
```

**Experiment weights (genre=1.0, energy max=2.0) — calculated:**
```
  #1  Bass Drop City  [6.6/10]   genre +1.00, energy proximity +1.96        (barely changes)
  #2  Rainy Window    [4.5/10]   mood +1.00, energy proximity +0.54, acoustic +0.50
  #3  Void Protocol   [4.4/10]   energy proximity +2.00                      (jumps from 2.2)
```

**What changed and why:**

Bass Drop City stays at #1 with almost the same score in both scenarios. Here is why: the genre weight loss of 1.0 is almost perfectly cancelled out by the energy gain. Bass Drop City's energy is 0.97 against a target of 0.95 — a gap of only 0.02, giving an energy score of 0.98. Doubling that gives 1.96, a gain of +0.98. The genre loss (-1.0) and energy gain (+0.98) nearly cancel. No matter how you weight the algorithm, the only EDM song in the catalog wins slot #1 for an EDM user.

Void Protocol (metal, perfect energy=0.95) shows the most dramatic change: its energy score goes from +1.00 to +2.00 — a full point gained — because it has a perfect energy match. It nearly catches Rainy Window at #3 (4.4 vs 4.5/10). Under the original weights, Void Protocol scored just 2.2/10 and was invisible. Doubling energy makes it almost as competitive as the mood-matched folk song.

**The critical finding:** even with doubled energy weight, Rainy Window (a soft folk ballad) remains #2 for a user who asked for high-energy EDM, because its mood match (+1.0) and acoustic bonus (+0.5) together (1.5 points) still beat Void Protocol's doubled-energy score (2.0 points → net 2.0 vs 2.04 for Rainy Window). You would need to weight energy at approximately 3x before the energy-close non-acoustic songs consistently beat the mood+acoustic combination. The nonsensical result is not a fluke — it is structurally baked into a profile where the user's own stated preferences (high energy + acoustic + sad) pull the scoring in contradictory directions simultaneously.

---

### Experiment 3: Mood Higher Weights — Can We Fix the Adversarial Profile?

**Motivation:** The adversarial profile (genre=edm, mood=sad, energy=0.95, acoustic=True) produced a folk ballad at #2 because mood+acoustic outweighed energy proximity. The question was: can adjusting mood vs genre weights fix the edge case without breaking the other three profiles?

Two configurations were tested across all four profiles simultaneously. MAX_SCORE stays 4.5 in both, so normalization is unaffected.

| Config | genre | mood | energy max | acoustic |
|---|---|---|---|---|
| Baseline | 2.0 | 1.0 | 1.0 | 0.5 |
| Exp A | 1.5 | 1.5 | 1.0 | 0.5 |
| Exp B | 1.0 | 2.0 | 1.0 | 0.5 |

**Adversarial profile results (genre=edm, mood=sad, energy=0.95):**

| Config | #1 | Score | #2 | Score |
|---|---|---|---|---|
| Baseline | Bass Drop City | 6.6/10 | Rainy Window (folk) | 3.9/10 |
| Exp A | Bass Drop City | 5.5/10 | Rainy Window (folk) | 5.0/10 |
| Exp B | **Rainy Window (folk)** | **6.2/10** | Bass Drop City | 4.4/10 |

Experiment A narrows the gap — Rainy Window climbs from 3.9 to 5.0 — but the folk ballad stays at #2. Experiment B flips it entirely: Rainy Window becomes #1, which is arguably *more* broken, since the top pick for an EDM/high-energy user is now a quiet acoustic folk song. Raising mood weight honored "sad" over everything else.

**Key finding:** No weight configuration fixes the adversarial profile because the inputs contradict each other. The system cannot simultaneously satisfy `genre=edm` (electronic, loud) and `mood=sad + likes_acoustic=True` (soft, gentle, unplugged). Every weight setting just decides which contradiction wins — genre or mood+acoustic. The real fix is input validation before scoring, not weight tuning.

**Effect on the other three profiles** (Exp A was the most balanced):
- Profile 1 (Pop): Rooftop Lights (indie pop/happy) jumped from #3 to #2 in Exp A, passing Gym Hero, because the higher mood weight rewarded its correct happy mood over Gym Hero's genre match with the wrong mood.
- Profile 2 (Lofi Acoustic): Library Rain stayed at 10.0/10 in all configs — the profile is internally consistent and the total doesn't change regardless of weight ratios.
- Profile 3 (Rock): Storm Runner stayed at #1. Gym Hero and Neon Jungle (both mood=intense) rose in score as mood got heavier.

**Conclusion:** Experiment A (genre=1.5, mood=1.5) produces the most balanced results across the three well-formed profiles. It surfaces better mood-matched songs while keeping genre as a meaningful signal. The adversarial profile cannot be fixed by reweighting and requires a design-level solution (input contradiction detection) that is out of scope for this simulation.

---

## Limitations and Risks

MusicMoodMapper 1.0 has several important limitations that any real deployment would need to address:

**It only works on a small catalog.** With just 20 songs and 1-3 per genre, users will see the same top results across many different profiles. Any "pop" user will always see Sunrise City and Gym Hero because those are the only pop songs. The system cannot demonstrate real diversity until the catalog grows substantially.

**It does not understand lyrics, language, or cultural context.** Two songs can share the same genre, mood, and energy but feel completely different because of their subject matter, language, or cultural origin. MusicMoodMapper has no way to capture this. A user who wants "Spanish-language reggaeton" and a user who wants "English pop-punk" would receive identical treatment if both say genre="pop" and energy=0.8.

**It overweights genre as a categorical label.** "Indie pop" and "pop" are scored as completely different genres — a binary miss — even though a fan of one is likely to enjoy the other. Real musical similarity is a spectrum, not a set of identical-or-totally-different buckets.

**It has no memory.** Every run is independent. If a user listens to Sunrise City every day, the system will still recommend it at #1 on the next run. There is no mechanism for variety, novelty, or avoiding songs the user has already heard.

See the [model card](model_card.md) for a more detailed analysis of each limitation and ideas for future improvement.

---

## Reflection

Read the full analysis in the [model card](model_card.md).

Building this recommender revealed how much the invisible math of a scoring function shapes what users see. The weights — genre=2.0, mood=1.0, energy max=1.0 — are not just technical parameters. They encode a belief that genre is twice as important as mood and twice as important as energy match. That belief became a bias when the weight-shift experiment showed that Rooftop Lights (indie pop, happy, near-perfect energy) was being ranked below Gym Hero (pop, wrong mood, further energy) purely because the genre label matched. The song a user would actually enjoy more was buried by a design decision made before anyone ran a single profile.

The adversarial profile experiment was even more surprising. Giving the system contradictory preferences — "I want high-energy EDM, I feel sad, and I like acoustic music" — did not produce an error. It produced a folk ballad at #2. The algorithm followed its own rules perfectly and still delivered a result that would make no sense to a real listener. That gap between "rule-correct" and "human-sensible" is exactly where most AI recommendation systems fail quietly, without any error message. The Score Breakdown display in MusicMoodMapper at least makes the reasoning visible so a user can see *why* the system made a strange choice — something production recommenders rarely offer.



