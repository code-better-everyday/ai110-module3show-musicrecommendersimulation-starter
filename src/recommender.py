import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Songs sorted by match score against the given UserProfile."""
        # Phase 3 edit: Implemented Recommender.recommend() to satisfy the test suite in
        # tests/test_recommender.py. The test creates Song dataclass instances and a
        # UserProfile dataclass instance, so we cannot call score_song directly — it expects
        # plain dicts. We convert both to dicts first, run score_song, then sort and return
        # the original Song objects (not dicts) so the test can check .genre and .mood
        # attributes directly on the returned items.
        user_dict = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "target_energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        scored = []
        for song in self.songs:
            song_dict = {
                "genre": song.genre,
                "mood": song.mood,
                "energy": song.energy,
                "acousticness": song.acousticness,
            }
            score, _ = score_song(user_dict, song_dict)
            scored.append((song, score))
        # Sort by score descending so index 0 is always the best match
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a plain-English explanation of why this song was recommended."""
        # Phase 3 edit: Implemented explain_recommendation() to satisfy the test that
        # checks for a non-empty string return. We reuse score_song with the same
        # dict-conversion approach as recommend(), then join the reasons list into a
        # single readable sentence. If somehow no rules fire (score is 0 and reasons
        # is empty), we fall back to a generic message rather than returning an empty string.
        user_dict = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "target_energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        song_dict = {
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "acousticness": song.acousticness,
        }
        _, reasons = score_song(user_dict, song_dict)
        if reasons:
            return "Recommended because: " + ", ".join(reasons)
        return "No strong match found — included for variety."

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and return them as a list of dicts with typed fields."""
    # Phase 3 edit: Implemented load_songs using csv.DictReader.
    # DictReader automatically uses the first CSV row as column headers, so each
    # row comes back as a dict like {"title": "Sunrise City", "genre": "pop", ...}.
    # We must cast numeric fields explicitly — CSV reads everything as strings by
    # default, and abs(song["energy"] - 0.8) would raise a TypeError if energy is
    # still the string "0.82". Casting here means every downstream function can do
    # math on these fields without worrying about type errors.
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"]           = int(row["id"])
            row["energy"]       = float(row["energy"])
            row["tempo_bpm"]    = float(row["tempo_bpm"])
            row["valence"]      = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a single song against user preferences; return (score, reasons)."""
    # Phase 3 edit: Implemented score_song using the Algorithm Recipe designed in Phase 2.
    # The recipe awards points across four rules: genre match, mood match, energy proximity,
    # and an optional acoustic bonus. Each rule that fires appends a human-readable reason
    # string to the reasons list, so the CLI output can explain WHY a song was recommended
    # rather than just showing a raw number. This mirrors how production recommender systems
    # surface "Because you listened to X" or "Matches your energy preference" explanations.
    #
    # Energy proximity uses the formula: 1.0 - abs(song_energy - target_energy).
    # This rewards songs that are CLOSE to the user's target in either direction —
    # it does not simply favor high-energy or low-energy songs. We clamp to 0.0 with
    # max() so a very large energy gap never produces a negative contribution to the score.
    #
    # Maximum possible score: 4.5 points (2.0 + 1.0 + 1.0 + 0.5).
    score = 0.0
    reasons = []

    # Rule 1: Genre match — strongest signal, worth 2 points.
    # Genre is weighted the highest because it is the most decisive filter:
    # a jazz fan and a metal fan rarely enjoy the same song regardless of energy or mood.
    if song["genre"] == user_prefs["genre"]:
        score += 2.0
        reasons.append("genre match (+2.0)")

    # Rule 2: Mood match — secondary filter, worth 1 point.
    # Mood refines within a genre: "chill pop" vs "intense pop" are meaningfully different.
    if song["mood"] == user_prefs["mood"]:
        score += 1.0
        reasons.append("mood match (+1.0)")

    # Rule 3: Energy proximity — continuous score up to 1.0 point.
    # Rewards songs whose energy level is close to the user's target rather than
    # unconditionally favoring high or low energy. A gap of 0 gives +1.0; a gap of
    # 0.5 gives +0.5; a gap of 1.0 gives 0.0. Never goes negative.
    energy_gap = abs(song["energy"] - user_prefs["target_energy"])
    energy_score = max(0.0, 1.0 - energy_gap)
    score += energy_score
    reasons.append(f"energy proximity (+{energy_score:.2f})")

    # Rule 4: Acoustic bonus — small bonus of 0.5 points.
    # Only fires when the user prefers acoustic music AND the song has high acousticness
    # (threshold: > 0.6). This lets the system capture a preference that genre alone
    # cannot express — e.g., two folk songs at the same energy but one is electric.
    if user_prefs.get("likes_acoustic") and song["acousticness"] > 0.6:
        score += 0.5
        reasons.append("acoustic bonus (+0.5)")

    return (score, reasons)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score and rank all songs; return the top-k as (song, score, explanation) tuples."""
    # Phase 3 edit: Implemented recommend_songs by calling score_song on every song in
    # the catalog and then sorting the results from highest score to lowest.
    #
    # We use sorted() instead of list.sort() deliberately:
    # - sorted() returns a NEW list and leaves the original `songs` list untouched.
    # - list.sort() mutates the list IN PLACE, which would permanently reorder the catalog.
    # - If main.py ever calls recommend_songs twice with different user profiles, using
    #   list.sort() on the first call would corrupt the order seen by the second call.
    #   sorted() avoids this side-effect entirely.
    #
    # The key=lambda x: x[1] tells sorted() to rank by the score (index 1 of each tuple).
    # reverse=True means highest scores come first — index 0 is always the best match.
    # We join the reasons list into a comma-separated string for clean CLI printing.
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        # Score transparency fix: store the raw reasons list (not a joined string) so
        # main.py can normalize each component individually and display a breakdown
        # where sub-scores visibly add up to the final Match score.
        scored.append((song, score, reasons))

    # Sort all scored songs from highest to lowest score, then slice the top k
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)
    return ranked[:k]
