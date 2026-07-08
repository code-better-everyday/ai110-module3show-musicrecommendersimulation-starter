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

    # Phase 2 edit: Expanded the starter profile into a complete taste profile dictionary.
    # The original starter only had genre, mood, and energy - which was not enough to
    # differentiate between "intense rock" and "chill lofi" because it lacked the
    # likes_acoustic field and used the wrong key name for energy (should be target_energy
    # to match the UserProfile dataclass). A complete profile lets the scoring function
    # use all four comparison points: genre match, mood match, energy proximity, and
    # the acoustic preference bonus. This profile represents a "High-Energy Pop" listener
    # who wants upbeat, produced (non-acoustic) music at high energy.
    user_prefs = {
        "genre": "pop",           # the genre this user most wants to hear
        "mood": "happy",          # the emotional vibe the user is looking for
        "target_energy": 0.8,     # how energetic the music should feel (0.0=very calm, 1.0=very intense)
        "likes_acoustic": False,  # this user prefers produced/electronic sounds over acoustic ones
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    # Phase 3 edit (output formatting): Added a bold header banner, a verbose line-by-line
    # user profile block, and per-song genre/mood/energy details so the terminal output is
    # fully self-contained and readable without opening any source files.
    # The separator lines use a fixed width of 54 chars to keep everything aligned.
    SEP  = "=" * 54
    DASH = "-" * 54

    print(f"\n{SEP}")
    print("   *** MUSIC RECOMMENDER  --  Let's get going! ***")
    print(SEP)

    # Verbose user profile block - one preference per line for clarity
    print("\n  YOUR TASTE PROFILE")
    print(f"  {DASH}")
    print(f"  Preferred genre   : {user_prefs['genre'].upper()}")
    print(f"  Preferred mood    : {user_prefs['mood'].capitalize()}")
    print(f"  Target energy     : {user_prefs['target_energy']} "
          f"({'high energy' if user_prefs['target_energy'] >= 0.7 else 'low energy' if user_prefs['target_energy'] <= 0.4 else 'medium energy'})")
    print(f"  Likes acoustic    : {'Yes - prefers unplugged/acoustic sounds' if user_prefs['likes_acoustic'] else 'No - prefers produced/electronic sounds'}")
    print(f"  Catalog size      : {len(songs)} songs\n")

    print(f"  TOP {len(recommendations)} RECOMMENDATIONS")
    print(f"  {DASH}")

    # MAX_SCORE is the highest possible raw score from score_song()
    # (2.0 genre + 1.0 mood + 1.0 energy + 0.5 acoustic = 4.5).
    # Dividing by MAX_SCORE and multiplying by 10 maps any raw score onto a 0-10 scale
    # so a perfect match reads as 10.0 and a zero-match reads as 0.0 — much more
    # intuitive than seeing "3.98 / 4.50" and having to do the math yourself.
    MAX_SCORE = 4.5

    for rank, rec in enumerate(recommendations, start=1):
        # Each rec is now (song_dict, raw_score, reasons_list) from recommend_songs()
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
