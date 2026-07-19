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

        recommendations = recommend_songs(user_prefs, songs, k=5)

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

        for rank, rec in enumerate(recommendations, start=1):
            # Each rec is (song_dict, raw_score, reasons_list) from recommend_songs()
            song, score, reasons = rec

            # Normalize raw score (0-4.5) to a 0-10 scale for readability
            normalized = (score / MAX_SCORE) * 10

            # Score transparency fix: title line shows the normalized total first
            print(f"\n  #{rank}  {song['title']}  -  {song['artist']}  "
                  f"[ Match: {normalized:.1f} / 10 ]")

            # Genre and Mood lines show whether the song matched the user's preference
            # so the reader immediately sees which attributes contributed before looking
            # at the breakdown numbers below.
            genre_note = "(matches your preference)" if song["genre"] == user_prefs["genre"] \
                         else f"(your preference: {user_prefs['genre']})"
            mood_note  = "(matches your preference)" if song["mood"] == user_prefs["mood"] \
                         else f"(your preference: {user_prefs['mood']})"

            print(f"       Genre   : {song['genre'].capitalize():<12} {genre_note}")
            print(f"       Mood    : {song['mood'].capitalize():<12} {mood_note}")
            print(f"       Energy  : {song['energy']} "
                  f"({'high' if song['energy'] >= 0.7 else 'low' if song['energy'] <= 0.4 else 'medium'})")

            # Score Breakdown block — each component shown with raw points AND its
            # normalized contribution so the sub-scores visibly add up to the Match total.
            # Parsing: every reason string ends with "(+N.NN)" so we split on "(+" and
            # strip the trailing ")" to extract the raw float reliably.
            print(f"\n       Score Breakdown:")
            for reason in reasons:
                label   = reason.split(" (+")[0].capitalize()
                raw_pts = float(reason.split("(+")[1].rstrip(")"))
                norm_pts = (raw_pts / MAX_SCORE) * 10
                print(f"         {label:<22} +{raw_pts:.2f} pts  ->  {norm_pts:.1f} / 10")

            print(f"         {'':->40}")
            print(f"         {'Total':<22}  {score:.2f} / {MAX_SCORE}  =  {normalized:.1f} / 10")

        print(f"\n{SEP}\n")


if __name__ == "__main__":
    main()
