"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

# Phase 3 edit: Changed import from bare 'recommender' to 'src.recommender' so the
# module resolves correctly when running 'python -m src.main' from the project root.
# The bare import only worked when running Python from inside the src/ directory directly.
from src.recommender import load_songs, recommend_songs


# Phase 6 edit: Challenge 4 — ASCII table helper for Score Breakdown display.
# Replaces the inline printing loop in main() so the output is a proper columnar
# table rather than loose indented lines. Uses fixed-width f-string formatting only
# (no tabulate import needed) to satisfy the challenge's "simple ASCII formatting"
# requirement.
def format_score_table(rank, song, score, reasons, MAX_SCORE, user_prefs):
    """Print one recommendation with an ASCII table for the Score Breakdown."""
    normalized = (score / MAX_SCORE) * 10

    print(f"\n  #{rank}  {song['title']}  -  {song['artist']}  "
          f"[ Match: {normalized:.1f} / 10 ]")

    genre_note = "(matches your preference)" if song["genre"] == user_prefs["genre"] \
                 else f"(your preference: {user_prefs['genre']})"
    mood_note  = "(matches your preference)" if song["mood"] == user_prefs["mood"] \
                 else f"(your preference: {user_prefs['mood']})"

    print(f"       Genre   : {song['genre'].capitalize():<12} {genre_note}")
    print(f"       Mood    : {song['mood'].capitalize():<12} {mood_note}")
    print(f"       Energy  : {song['energy']} "
          f"({'high' if song['energy'] >= 0.7 else 'low' if song['energy'] <= 0.4 else 'medium'})")

    W1, W2, W3 = 22, 9, 9
    border = f"       +{'-' * (W1 + 2)}+{'-' * (W2 + 2)}+{'-' * (W3 + 2)}+"
    print(f"\n       Score Breakdown:")
    print(border)
    print(f"       | {'Rule':<{W1}} | {'Raw pts':>{W2}} | {'Score/10':>{W3}} |")
    print(border)
    for reason in reasons:
        label    = reason.split(" (+")[0].capitalize()
        raw_pts  = float(reason.split("(+")[1].rstrip(")"))
        norm_pts = (raw_pts / MAX_SCORE) * 10
        print(f"       | {label:<{W1}} | {f'+{raw_pts:.2f}':>{W2}} | {f'{norm_pts:.1f}/10':>{W3}} |")
    print(border)
    total_raw = f"{score:.2f}/{MAX_SCORE}"
    total_nrm = f"{normalized:.1f}/10"
    print(f"       | {'TOTAL':<{W1}} | {total_raw:>{W2}} | {total_nrm:>{W3}} |")
    print(border)


# Phase 6 edit: Challenge 3 — Diversity Penalty.
# Prevents the same artist from appearing more than once in the top-5 results.
# Runs as a post-ranking step after recommend_songs() so it never touches
# score_song() weights. Songs from a repeated artist are moved to a backfill list
# and only appear if we run out of unique-artist candidates.
def apply_diversity_filter(ranked_songs):
    """Re-rank to remove duplicate artists; unique-artist songs fill the top slots."""
    seen_artists = set()
    diverse = []
    backfill = []
    for entry in ranked_songs:
        artist = entry[0]["artist"]
        if artist not in seen_artists:
            seen_artists.add(artist)
            diverse.append(entry)
        else:
            backfill.append(entry)
    return diverse + backfill


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Phase 4 edit: Replaced the single user_prefs dict with a list of four named profiles
    # for stress-testing the recommender across diverse and conflicting inputs. Each profile
    # has a "name" key (used as a sub-header in the output) and the same four scoring keys
    # the recommender expects: genre, mood, target_energy, likes_acoustic.
    #
    # Profile design rationale:
    # 1. "High-Energy Pop" — kept from Phase 3; baseline for regression comparison.
    # 2. "Chill Lofi Acoustic" — targets the acoustic bonus pathway explicitly.
    # 3. "Deep Intense Rock" — tests a near-perfect single-genre match scenario.
    # 4. "Adversarial -- Conflicting Signals" — preferences that actively fight each other:
    #    EDM is almost never acoustic, and high-energy songs rarely carry a sad mood.
    #    This tests whether the system produces reasonable or nonsensical results under
    #    internally contradictory inputs.
    profiles = [
        {
            "name": "High-Energy Pop",
            "genre": "pop",
            "mood": "happy",
            "target_energy": 0.8,
            "likes_acoustic": False,
        },
        {
            "name": "Chill Lofi Acoustic",
            "genre": "lofi",
            "mood": "chill",
            "target_energy": 0.35,
            "likes_acoustic": True,
        },
        {
            "name": "Deep Intense Rock",
            "genre": "rock",
            "mood": "intense",
            "target_energy": 0.91,
            "likes_acoustic": False,
        },
        {
            "name": "Adversarial -- Conflicting Signals",
            "genre": "edm",
            "mood": "sad",
            "target_energy": 0.95,
            "likes_acoustic": True,
        },
    ]

    # Phase 3 edit (output formatting): Added a bold header banner, a verbose line-by-line
    # user profile block, and per-song genre/mood/energy details so the terminal output is
    # fully self-contained and readable without opening any source files.
    # The separator lines use a fixed width of 54 chars to keep everything aligned.
    SEP  = "=" * 54
    DASH = "-" * 54

    print(f"\n{SEP}")
    print("   *** MUSIC RECOMMENDER  --  Let's get going! ***")
    print(f"{SEP}")

    # MAX_SCORE is the highest possible raw score from score_song()
    # (2.0 genre + 1.0 mood + 1.0 energy + 0.5 acoustic = 4.5).
    # Dividing by MAX_SCORE and multiplying by 10 maps any raw score onto a 0-10 scale
    # so a perfect match reads as 10.0 and a zero-match reads as 0.0.
    MAX_SCORE = 4.5

    # Phase 4 edit: Wrapped all output in a loop over profiles so one run of main.py
    # shows all four profiles back-to-back. Each profile gets its own recommendation block
    # separated by a divider line so the output is easy to scan.
    for profile_num, user_prefs in enumerate(profiles, start=1):
        profile_name = user_prefs["name"]

        print(f"\n  PROFILE {profile_num} of {len(profiles)}: {profile_name}")
        print(f"  {DASH}")

        # Phase 6 edit: Challenge 3 — fetch k=10 candidates so the diversity filter
        # has enough unique-artist options after dropping duplicates. Slice to 5 after.
        recommendations = recommend_songs(user_prefs, songs, k=10)
        recommendations = apply_diversity_filter(recommendations)[:5]

        # Verbose user profile block - one preference per line for clarity
        print("\n  YOUR TASTE PROFILE")
        print(f"  Preferred genre   : {user_prefs['genre'].upper()}")
        print(f"  Preferred mood    : {user_prefs['mood'].capitalize()}")
        print(f"  Target energy     : {user_prefs['target_energy']} "
              f"({'high energy' if user_prefs['target_energy'] >= 0.7 else 'low energy' if user_prefs['target_energy'] <= 0.4 else 'medium energy'})")
        print(f"  Likes acoustic    : {'Yes - prefers unplugged/acoustic sounds' if user_prefs['likes_acoustic'] else 'No - prefers produced/electronic sounds'}")
        print(f"  Catalog size      : {len(songs)} songs\n")

        print(f"  TOP {len(recommendations)} RECOMMENDATIONS")
        print(f"  {DASH}")

        # Phase 6 edit: Challenge 4 — replaced inline Score Breakdown loop with
        # format_score_table(), which displays the same data in a clean ASCII table.
        for rank, rec in enumerate(recommendations, start=1):
            song, score, reasons = rec
            format_score_table(rank, song, score, reasons, MAX_SCORE, user_prefs)

        print(f"\n{SEP}\n")


if __name__ == "__main__":
    main()
