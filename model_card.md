# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

A content-based music recommendation engine built for the CodePath AI110 Module 3 classroom simulation. "VibeFinder" reflects the system's core goal: matching a song's energy, mood, and genre signature to a listener's stated preferences, rather than relying on what other people listened to.

---

## 2. Intended Use

VibeFinder 1.0 is designed for classroom exploration of how rule-based recommendation systems work. It takes a single user's taste profile (their favorite genre, mood, target energy level, and acoustic preference) and ranks a catalog of 20 songs from best match to worst, returning the top 5 with a full Score Breakdown explaining exactly why each song was recommended.

The system assumes that the user can accurately state their preferences up front — it does not learn from listening history, skips, or repeated plays. It is not designed for production use or real user data. Its value is educational: by making every scoring decision visible and traceable, it lets students see exactly how a simple recommendation algorithm turns input data into a ranked list.

---

## 3. How the Model Works

VibeFinder compares every song in the catalog to a user's taste profile across four dimensions. Each dimension contributes a number of points, and the song's total point score determines its rank.

First, if the song's genre matches the user's preferred genre (for example, both are "pop"), the song earns 2 points. Genre is the heaviest factor because musical genre is the strongest signal of whether a listener will enjoy a track — a jazz fan and a metal fan will rarely agree on the same song even if both feel "happy" or "high energy."

Second, if the song's mood tag matches the user's preferred mood (for example, both are "chill"), the song earns 1 additional point. Mood works as a refining filter within a genre — two pop songs can feel very different if one is happy and upbeat while the other is moody and introspective.

Third, the song earns up to 1 additional point based on how close its energy level is to the user's target. The closer the match, the higher the bonus. A perfect energy match adds 1.0; a large gap adds almost nothing. This treats energy as a continuous measurement rather than a simple high/low category, which is more realistic.

Fourth, if the user has said they prefer acoustic music and the song has a high acousticness score (above 0.6 on a 0-to-1 scale), the song earns a small bonus of 0.5 points. This lets the profile capture a preference that genre alone cannot express.

The maximum possible score is 4.5 points. All scores are also shown on a 0-to-10 scale in the output to make the results immediately intuitive.

---

## 4. Data

The catalog contains 20 songs stored in a CSV file (`data/songs.csv`). Each song has the following attributes: a unique ID, title, artist, genre, mood, energy level, tempo (BPM), valence, danceability, and acousticness. Of these attributes, VibeFinder 1.0 uses genre, mood, energy, and acousticness for scoring. The remaining fields (tempo, valence, danceability) are present in the data but are not yet connected to any user preference — they are available for future improvement.

The catalog covers 12 genres: pop, lofi, rock, ambient, jazz, indie pop, synthwave, rnb, folk, edm, country, metal, classical, hiphop, and electronic. It covers 9 moods: happy, chill, intense, relaxed, moody, focused, romantic, sad, euphoric, angry, and dreamy. The original starter catalog had 10 songs; 10 additional songs were added manually during Phase 2 to broaden genre and mood coverage.

Important gaps in the dataset include: no lyrics or language information, no release decade or era, no artist gender or cultural origin, no explicit tempo-based preferences, and no user listening history. Songs were chosen manually and do not represent any particular real-world popularity distribution — genres like pop and lofi have 2-3 catalog entries, while others (rnb, country, metal, edm) have only one. This catalog size and distribution is a major constraint on recommendation diversity.

---

## 5. Strengths

VibeFinder works best when the user has clear, single-genre preferences. When a user wants "lofi/chill/low energy/acoustic," the system correctly surfaces all three lofi songs before any other genre, with Library Rain achieving a perfect 10.0/10 score because every single preference matched: genre, mood, exact energy target, and acoustic bonus all fired at once. This kind of end-to-end transparency — where the math is fully traceable in the Score Breakdown — is one of the system's strongest design features. A user can look at the output and explain exactly why every song ranked where it did, which most production recommenders cannot offer.

The energy proximity formula is also a genuine strength over a simpler high/low energy binary. By using `1.0 - abs(gap)`, the system rewards nearness in either direction — a user who wants medium energy 0.5 will score a song at 0.52 almost as high as one at exactly 0.5, rather than arbitrarily penalizing it for being "too high." This is closer to how humans actually experience energy levels than a strict cutoff would be.

---

## 6. Limitations and Bias

**Genre dominance bias.** The genre weight of 2.0 is twice as large as any other single factor. This means any song that matches genre automatically earns 2 points even if everything else is wrong — enough to outrank songs from the "wrong" genre that are nearly perfect on mood, energy, and acoustic preferences. In the weight-shift experiment (Phase 4), halving the genre weight to 1.0 caused Rooftop Lights (indie pop, happy, energy=0.76) to jump from #3 to #2 for the pop/happy profile, ahead of Gym Hero (pop, intense, energy=0.93), because Rooftop Lights had a better mood match and closer energy. The original ranking kept Gym Hero at #2 purely because of its genre match. This is a real bias: users who say "pop" may genuinely enjoy an indie pop or rnb song that perfectly fits their vibe, but the system will consistently bury those songs below any pop song no matter how poor the rest of the fit.

**Small catalog diversity.** With only 1-3 songs per genre, any user profile that specifies a genre will almost always see the same 2-3 songs at the top of every run regardless of how much they vary their other preferences. A "pop user" will always see Sunrise City, Gym Hero, and Rooftop Lights near the top because those are the only pop and indie-pop songs in the catalog. The catalog is simply too small to demonstrate meaningful diversity.

**Energy direction blindness.** The energy proximity formula does not know whether a song is too high or too low relative to the user's target — it only knows the gap. This means a user who wants very calm music will score a very loud song at the same distance penalty as a user who wants very loud music scores a very calm song. There is no "I want more energy, not less" signal.

**No temporal or contextual awareness.** The system does not know what time of day it is, what mood the user was in yesterday, whether they have heard a song recently, or whether they are looking for something new versus familiar. Every recommendation run is stateless — two runs with identical inputs produce identical outputs with no variety.

**Conflicting preferences produce structurally nonsensical results with no warning.** When a user's stated preferences contradict each other — for example, wanting high-energy EDM (0.95 energy target) while also preferring acoustic sounds and a sad mood — the scoring rules follow their own logic and produce results that are technically valid but musically absurd. For the adversarial profile tested in Phase 4, a quiet acoustic folk ballad (Rainy Window, energy=0.22) ranked #2 ahead of high-energy metal (Void Protocol, energy=0.95) because mood=sad (+1.0) and acoustic bonus (+0.5) outweighed perfect energy proximity (+1.0). The weight-shift analysis confirmed this is structural, not a fluke: even doubling the energy weight to 2x (max +2.0) leaves Rainy Window at #2 because its mood+acoustic combination (1.5 points) plus a small energy score (0.54) still totals 2.04 — just barely ahead of Void Protocol's perfect energy score of 2.0. The system would require approximately 3x energy weighting before high-energy non-acoustic songs consistently outrank mood-matched acoustic ones for this profile. A production system should detect contradictory inputs and warn the user before running the algorithm.

---

## 7. Evaluation

Four distinct user profiles were tested. Each profile was chosen to probe a different aspect of the scoring algorithm.

**Profile 1: High-Energy Pop** (genre=pop, mood=happy, energy=0.8, acoustic=False) — This was the baseline profile from Phase 3. Sunrise City ranked #1 at 8.8/10, exactly matching on genre, mood, and near-perfect energy. The results were intuitive and matched musical expectation. Gym Hero at #2 demonstrated genre dominance: it ranked above Rooftop Lights (#3) entirely because of its genre match, even though Rooftop Lights had a better mood match and similar energy.

**Profile 2: Chill Lofi Acoustic** (genre=lofi, mood=chill, energy=0.35, acoustic=True) — Library Rain achieved a perfect score of 10.0/10, the first time any song earned the maximum 4.5 raw points. Every single preference fired: genre match, mood match, exact energy match (both 0.35), and acoustic bonus (acousticness=0.86). This result matched intuition perfectly and is the strongest demonstration of the algorithm working as intended. Midnight Coding at #2 scored 9.8/10 — almost perfect, missing only a tiny energy gap of 0.07.

**Profile 3: Deep Intense Rock** (genre=rock, mood=intense, energy=0.91, acoustic=False) — Storm Runner ranked #1 at 8.9/10 with a genre match, mood match, and perfect energy match (both 0.91). The result was highly intuitive. The interesting observation at #2 was Gym Hero (pop) and Neon Jungle (electronic) tied at 4.4/10, both having the right mood and close energy but no genre match — demonstrating how the 2.0 genre weight creates a wide gap between a genre match (8.9) and the next-best non-genre-match (4.4).

**Profile 4: Adversarial — Conflicting Signals** (genre=edm, mood=sad, energy=0.95, acoustic=True) — This profile produced the most interesting result of the evaluation. Bass Drop City ranked #1 at 6.6/10 on genre match alone, with no mood match (the song is "euphoric," not "sad") and acoustic bonus blocked (acousticness=0.03). The real surprise was #2: Rainy Window (folk/sad) scored 3.9/10, outranking Void Protocol (metal, energy=0.95) despite being a quiet acoustic folk ballad for a user who said they want high-energy EDM. Rainy Window won #2 because its mood tag matched "sad" (+1.0) and its acousticness of 0.94 triggered the acoustic bonus (+0.5) — together those two points outweighed Void Protocol's perfect energy match (+1.0). The result is logically consistent with the scoring rules, but musically nonsensical: an "I want EDM and I'm sad" user gets a soft folk ballad as their second recommendation. This is the clearest illustration of what conflicting inputs do to a rule-based system — it does not crash or warn the user, it just produces a result that follows the rules but defies common sense.

**Weight-shift experiment:** To test genre dominance directly, the genre weight was halved (2.0 to 1.0) and energy weight was doubled (max 1.0 to max 2.0), keeping MAX_SCORE at 4.5. For the pop/happy profile, this caused Rooftop Lights to jump from #3 to #2 (passing Gym Hero) because Rooftop Lights had a better mood match and closer energy. Gym Hero dropped to #3. The shift proved that genre dominance in the original weights was actively suppressing songs with stronger vibes but different labels.

The same weight shift was also analyzed for the adversarial profile. The result was striking: Bass Drop City (the only EDM song) stayed at #1 with essentially the same score either way, because the genre weight loss (-1.0) was almost exactly cancelled by the doubled energy gain (+0.98 → +1.96). Void Protocol (metal, perfect energy=0.95) jumped from 2.2/10 to 4.4/10 because its perfect energy match benefited enormously from the doubled cap. But Rainy Window (folk/sad) still held #2 at 4.5/10 even under the experiment weights — its mood+acoustic combination (1.5 points) plus a small energy score (0.54) totaled 2.04, just ahead of Void Protocol's 2.0. The nonsensical result survived because it is structurally baked into the contradictory inputs, not into any single weight value.

**Mood weight experiments (Experiments A and B):** To try to resolve the adversarial profile edge case, two additional weight configurations were tested — genre=1.5/mood=1.5 and genre=1.0/mood=2.0 — across all four profiles simultaneously (MAX_SCORE held at 4.5). Neither fixed the problem. Experiment A (genre=1.5, mood=1.5) narrowed the gap between Bass Drop City and Rainy Window (5.5 vs 5.0) but kept the folk ballad at #2. Experiment B (genre=1.0, mood=2.0) flipped the adversarial result entirely, making Rainy Window #1 at 6.2/10 — worse, not better. For the other three profiles, Experiment A produced the most balanced behavior: Rooftop Lights (indie pop/happy) moved above Gym Hero (pop/wrong mood) for the pop profile, rewarding correct mood match over genre label. The conclusion from all weight experiments is that the adversarial edge case cannot be resolved by tuning — it requires input validation to detect contradictory preferences before scoring begins.

---

## 8. Future Work

The most impactful single improvement would be expanding the catalog substantially — at least 50-100 songs per major genre would make the diversity bias much less severe and allow the system to demonstrate recommendation variety across a wide population of user profiles.

The `UserProfile` dataclass could be extended with `target_tempo_bpm` and `target_valence` preference fields, and the corresponding scoring rules added to `score_song()`. Both tempo and valence are already in the CSV and would let the system distinguish between "relaxed but upbeat" versus "relaxed and melancholic" — a distinction mood alone cannot capture.

A diversity penalty would prevent the same artist from appearing multiple times in the top-k results. Currently there is no such constraint, and profiles that match a well-represented genre can end up with the same artist (Neon Echo) at multiple positions — which would feel repetitive in a real product.

Connecting the system to a collaborative filtering layer would let it use listening patterns from other users to surface songs that similar-taste users enjoyed, even if they fall outside the strict genre/mood boundaries of the current profile. The two approaches (content-based and collaborative) can be blended — content-based for new users with no history, collaborative filtering once enough behavioral data is available.

---

## 9. Personal Reflection

Building VibeFinder 1.0 made the invisible math behind everyday apps suddenly very visible. Every time Spotify or YouTube Music recommends something, there is a scoring function running somewhere that assigns weights to features and ranks results by total score. What this project showed is how much those weights matter: moving genre from 2.0 to 1.0 changed the ranking order and surfaced songs that were genuinely better vibes but the "wrong" label. That is not just an academic observation — it is a live example of how a design decision made by an engineer becomes a bias experienced by every user of the product.

The adversarial profile result was the most surprising moment of the evaluation. I expected the system to break or return garbage. Instead, it returned a logically valid but musically absurd answer: a folk ballad for someone who asked for high-energy EDM, justified by two real scoring rules (mood match and acoustic bonus). That is what makes algorithmic bias subtle and hard to catch — the system is not wrong by its own rules. It is only wrong by human standards that the rules do not capture. Systems that cannot explain their outputs at all are harder to audit than this one, and yet VibeFinder with full Score Breakdown transparency still produced an outcome that would feel unfair or confusing to a real user. That gap between "rule-correct" and "human-sensible" is, I think, one of the most important things to understand about AI-powered recommendation systems.
