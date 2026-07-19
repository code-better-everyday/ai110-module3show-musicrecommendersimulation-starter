from src.recommender import Song, UserProfile, Recommender, score_song, recommend_songs

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# Phase 5 edit: Added 3 new unit tests to exercise score_song() and
# recommend_songs() directly, verifying the Algorithm Recipe weights
# and the acoustic bonus threshold gate.

def test_score_song_genre_match_adds_2_points():
    # Genre match is worth exactly 2.0 points regardless of other attributes.
    # Energy=0.0 so energy proximity contributes essentially nothing (gap=1.0 → 0.0).
    # Mood deliberately mismatches so only genre fires.
    user = {"genre": "rock", "mood": "happy", "target_energy": 0.0, "likes_acoustic": False}
    song = {"genre": "rock", "mood": "intense", "energy": 0.0, "acousticness": 0.0}
    score, reasons = score_song(user, song)
    assert score >= 2.0
    assert any("genre match" in r for r in reasons)


def test_score_song_acoustic_bonus_fires_above_threshold():
    # Acoustic bonus fires only when the song's acousticness > 0.6.
    user = {"genre": "lofi", "mood": "chill", "target_energy": 0.4, "likes_acoustic": True}

    # Above threshold (0.8 > 0.6) — bonus must fire
    song_acoustic = {"genre": "lofi", "mood": "chill", "energy": 0.4, "acousticness": 0.8}
    score_with, reasons_with = score_song(user, song_acoustic)
    assert any("acoustic bonus" in r for r in reasons_with)

    # Below threshold (0.5 < 0.6) — bonus must NOT fire
    song_not_acoustic = {"genre": "lofi", "mood": "chill", "energy": 0.4, "acousticness": 0.5}
    score_without, reasons_without = score_song(user, song_not_acoustic)
    assert not any("acoustic bonus" in r for r in reasons_without)
    assert score_with > score_without


def test_recommend_songs_returns_k_results_sorted_descending():
    # recommend_songs() must return exactly k results in descending score order.
    songs = [
        {"genre": "pop",  "mood": "happy",   "energy": 0.8, "acousticness": 0.1},
        {"genre": "lofi", "mood": "chill",   "energy": 0.4, "acousticness": 0.8},
        {"genre": "rock", "mood": "intense", "energy": 0.9, "acousticness": 0.1},
        {"genre": "jazz", "mood": "relaxed", "energy": 0.3, "acousticness": 0.6},
    ]
    user = {"genre": "pop", "mood": "happy", "target_energy": 0.8, "likes_acoustic": False}
    results = recommend_songs(user, songs, k=3)

    assert len(results) == 3
    # Each result is (song, score, reasons) — verify descending score order
    scores = [r[1] for r in results]
    assert scores[0] >= scores[1] >= scores[2]
