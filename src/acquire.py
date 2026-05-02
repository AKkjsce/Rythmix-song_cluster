import sys
import pandas as pd


AUDIO_COLUMNS = [
    "danceability", "energy", "valence",
    "acousticness", "tempo", "loudness",
    "speechiness", "instrumentalness", "liveness",
]


def load_and_clean(filepath="data/dataset.csv"):
    # try to load, bail if not found
    try:
        df = pd.read_csv(filepath, low_memory=False)
    except FileNotFoundError:
        print(f"cant find dataset at '{filepath}'")
        print("grab it from: https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset")
        sys.exit(1)

    n_before = len(df)
    print(f"loaded {n_before:,} rows from {filepath}")
    print(f"cols: {list(df.columns)}")

    # quick sanity check on audio feature ranges
    print(df[AUDIO_COLUMNS].describe().to_string())

    df = df.dropna(subset=AUDIO_COLUMNS)
    dropped_nulls = n_before - len(df)
    print(f"dropped {dropped_nulls:,} rows w/ missing audio vals")

    # same song can appear in multiple albums/regions, dedupe by name+artist
    if "track_name" in df.columns and "artists" in df.columns:
        before_dd = len(df)
        df = df.drop_duplicates(subset=["track_name", "artists"], keep="first")
        print(f"removed {before_dd - len(df):,} dupes (same name+artist)")
    elif "track_id" in df.columns:
        before_dd = len(df)
        df = df.drop_duplicates(subset=["track_id"], keep="first")
        print(f"removed {before_dd - len(df):,} dupes by track_id")
    else:
        print("warning: no id cols found, skipped dedup")

    print(f"final: {len(df):,} songs\n")
    df = df.reset_index(drop=True)
    return df
