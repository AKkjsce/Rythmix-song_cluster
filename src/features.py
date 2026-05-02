import pandas as pd


AUDIO_FEATURES = [
    "danceability", "energy", "valence",
    "acousticness", "tempo", "loudness",
    "speechiness", "instrumentalness", "liveness",
]

# stuff we keep for display but never feed into the model
IDENTITY_COLS = ["track_id", "track_name", "artists", "track_genre"]


def pick_features(df):
    missing = [c for c in AUDIO_FEATURES if c not in df.columns]
    if missing:
        raise ValueError(f"missing audio cols: {missing}")

    feat_mat = df[AUDIO_FEATURES].copy()
    id_cols = [c for c in IDENTITY_COLS if c in df.columns]
    track_info = df[id_cols].copy()

    # just in case something leaked in
    for c in IDENTITY_COLS:
        if c in feat_mat.columns:
            raise RuntimeError(f"'{c}' ended up in feature matrix, that's wrong")

    print(f"feature matrix: {feat_mat.shape[0]:,} rows x {feat_mat.shape[1]} cols")

    # print ranges so we can see scale differences (tempo vs 0-1 features)
    for f in AUDIO_FEATURES:
        lo, hi, avg = feat_mat[f].min(), feat_mat[f].max(), feat_mat[f].mean()
        print(f"  {f:<20s}  [{lo:.3f}, {hi:.3f}]  mean={avg:.3f}")

    print()
    return feat_mat, track_info
