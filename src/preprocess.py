import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA


class DataScaler:
    # wraps sklearn scaler + pca so we can reuse fitted objects later

    def __init__(self, num_pca_dims=2):
        self._sc = StandardScaler()
        self._pca = PCA(n_components=num_pca_dims, random_state=7)
        self._cache = None

    def scale_data(self, feat_df):
        # tempo is like 60-200, danceability is 0-1, scaling makes distances fair
        scaled = self._sc.fit_transform(feat_df)
        self._cache = scaled

        print(f"scaled {feat_df.shape[1]} features, mean={scaled.mean():.4f} std={scaled.std():.4f}")
        return scaled

    def reduce_to_2d(self):
        if self._cache is None:
            raise RuntimeError("call scale_data() first")

        proj = self._pca.fit_transform(self._cache)
        vr = self._pca.explained_variance_ratio_
        print(f"PCA: pc1={vr[0]*100:.1f}%  pc2={vr[1]*100:.1f}%  total={sum(vr)*100:.1f}%")
        return proj

    def unscale(self, arr):
        return self._sc.inverse_transform(arr)

    def get_feature_names(self):
        if hasattr(self._sc, "feature_names_in_"):
            return list(self._sc.feature_names_in_)
        return []
