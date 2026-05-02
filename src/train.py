import os
import pandas as pd
from sklearn.mixture import GaussianMixture


def run_gmm(tracks_df, scaled_data, scaler_obj, k):
    print(f"fitting GMM with k={k}...")

    gmm = GaussianMixture(n_components=k, covariance_type='diag', n_init=2, random_state=None)
    labels = gmm.fit_predict(scaled_data)

    df = tracks_df.copy()
    df["cluster"] = labels

    # gmm stores cluster centers in .means_ (not .cluster_centers_ like kmeans)
    raw_cents = gmm.means_
    unscaled_cents = scaler_obj.unscale(raw_cents)

    cent_df = pd.DataFrame(unscaled_cents, columns=scaler_obj.get_feature_names())
    df.attrs["centroid_table"] = cent_df
    scaler_obj.cluster_centers = unscaled_cents

    os.makedirs("outputs", exist_ok=True)
    out = os.path.join("outputs", "clustered_tracks.csv")
    df.to_csv(out, index=False)

    print(f"  {len(df):,} tracks -> {k} clusters, saved to {out}\n")
    return df
