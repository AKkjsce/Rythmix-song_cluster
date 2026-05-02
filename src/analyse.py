import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.features import AUDIO_FEATURES


PALETTE = [
    "#e94560", "#53d8fb", "#f5a623", "#7ed321",
    "#9b59b6", "#1abc9c", "#e67e22", "#3498db",
    "#e74c3c", "#2ecc71", "#f39c12", "#8e44ad",
    "#16a085", "#d35400", "#27ae60",
]


def _label_cluster(row):
    # rough heuristic ordering - speechiness wins if high coz it's usually rap/spoken
    if row["speechiness"] > 0.25:
        return "Spoken-Word / Rap"
    if row["instrumentalness"] > 0.60:
        return "Instrumental / Ambient"
    if row["acousticness"] > 0.70 and row["energy"] < 0.35:
        return "Sparse Acoustic"
    if row["energy"] > 0.75 and row["danceability"] > 0.70:
        return "High-Energy Dance"
    if row["valence"] < 0.30 and row["tempo"] < 100:
        return "Dark & Low-Tempo"
    if row["valence"] > 0.65 and row["danceability"] > 0.60:
        return "Upbeat & Cheerful"
    if row["liveness"] > 0.60:
        return "Live Performance"
    if row["energy"] > 0.65 and row["loudness"] > -6:
        return "Hard-Hitting / Loud"
    if row["acousticness"] > 0.50 and row["instrumentalness"] > 0.30:
        return "Mellow Instrumental"
    return "Mixed / Balanced"


def assign_cluster_names(cent_tbl):
    raw = {i: _label_cluster(r) for i, r in cent_tbl.iterrows()}

    # dedupe by appending a counter when two clusters get the same label
    seen = {}
    out = {}
    for cid, name in raw.items():
        if name in seen:
            seen[name] += 1
            out[cid] = f"{name} {seen[name]}"
        else:
            seen[name] = 1
            out[cid] = name
    return out


def _draw_scatter(pca_pts, labels, names, k, save_dir):
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor("#0d0d1a")
    ax.set_facecolor("#13132a")

    n = len(labels)
    if n > 80000:
        rng = np.random.default_rng(99)
        idx = rng.choice(n, size=80000, replace=False)
        pts, lbls = pca_pts[idx], labels[idx]
    else:
        pts, lbls = pca_pts, labels

    for cid in range(k):
        mask = lbls == cid
        col = PALETTE[cid % len(PALETTE)]
        ax.scatter(pts[mask, 0], pts[mask, 1],
                   s=4, alpha=0.35, color=col,
                   label=f"C{cid}: {names[cid]}", rasterized=True)

    # star markers at cluster centers
    for cid in range(k):
        m = labels == cid
        cx, cy = pca_pts[m, 0].mean(), pca_pts[m, 1].mean()
        col = PALETTE[cid % len(PALETTE)]
        ax.scatter(cx, cy, s=220, marker="*", color=col,
                   edgecolors="white", linewidths=0.8, zorder=5)
        ax.annotate(f"C{cid}", (cx, cy), color="white", fontsize=8,
                    ha="center", va="bottom", xytext=(0, 8),
                    textcoords="offset points")

    ax.set_xlabel("PC 1", color="#aaa", fontsize=11)
    ax.set_ylabel("PC 2", color="#aaa", fontsize=11)
    ax.tick_params(colors="#666")
    for sp in ax.spines.values():
        sp.set_color("#333")

    ax.legend(loc="upper right", fontsize=8, facecolor="#1a1a2e",
              labelcolor="white", framealpha=0.85, markerscale=3)
    plt.title("Acoustic Cluster Map (PCA 2D)", color="white", fontsize=14,
              fontweight="bold", pad=14)
    plt.tight_layout()

    fp = os.path.join(save_dir, "pca_scatter.png")
    plt.savefig(fp, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  scatter -> {fp}")


def _draw_radar(cent_tbl, names, k, save_dir):
    col_min = cent_tbl.min()
    col_max = cent_tbl.max()
    rng = (col_max - col_min).replace(0, 1)
    norm = (cent_tbl - col_min) / rng

    nf = len(AUDIO_FEATURES)
    angles = np.linspace(0, 2 * np.pi, nf, endpoint=False)
    ang_closed = np.concatenate([angles, [angles[0]]])

    ncols = min(k, 2)
    nrows = int(np.ceil(k / ncols))
    fig, axes = plt.subplots(nrows, ncols,
                             figsize=(ncols * 5.5, nrows * 5.5),
                             subplot_kw={"polar": True},
                             constrained_layout=True)
    fig.patch.set_facecolor("#0d0d1a")

    # normalise axes shape
    if k == 1:
        axes = np.array([[axes]])
    elif nrows == 1:
        axes = axes[np.newaxis, :]
    elif ncols == 1:
        axes = axes[:, np.newaxis]

    for slot in range(nrows * ncols):
        r, c = divmod(slot, ncols)
        ax = axes[r, c]
        ax.set_facecolor("#13132a")

        if slot >= k:
            ax.set_visible(False)
            continue

        vals = norm.iloc[slot].values.tolist()
        vals.append(vals[0])
        col = PALETTE[slot % len(PALETTE)]

        ax.plot(ang_closed, vals, color=col, lw=2.5)
        ax.fill(ang_closed, vals, alpha=0.25, color=col)
        ax.set_thetagrids(np.degrees(angles), AUDIO_FEATURES, color="#ccc", fontsize=9)
        ax.tick_params(pad=14)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.25, 0.5, 0.75, 1.0])
        ax.set_yticklabels(["25%", "50%", "75%", "100%"], color="#666", fontsize=7)
        ax.spines["polar"].set_color("#444")
        ax.grid(color="#333", lw=0.7)
        ax.set_title(f"C{slot}: {names[slot]}", color="white",
                     fontsize=10, fontweight="bold", pad=12)

    fig.suptitle("Cluster Acoustic Fingerprints", color="white", fontsize=17, fontweight="bold")
    fp = os.path.join(save_dir, "radar_chart.png")
    plt.savefig(fp, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  radar  -> {fp}")


def generate_analysis(tracks_df, scaled_data, scaler_obj, k, save_dir="outputs"):
    os.makedirs(save_dir, exist_ok=True)
    print("running analysis...")

    cent_tbl = tracks_df.attrs.get("centroid_table")
    if cent_tbl is None:
        raise RuntimeError("no centroid table - did training run ok?")

    cnames = assign_cluster_names(cent_tbl)
    for cid, name in cnames.items():
        print(f"  cluster {cid} -> {name}")

    pca_coords = scaler_obj.reduce_to_2d()
    lbls = tracks_df["cluster"].values

    _draw_scatter(pca_coords, lbls, cnames, k, save_dir)
    _draw_radar(cent_tbl, cnames, k, save_dir)

    total = len(tracks_df)
    print(f"\n  {'id':>4}  {'name':<26}  {'count':>8}  {'%':>6}")
    for cid in range(k):
        cnt = (tracks_df["cluster"] == cid).sum()
        print(f"  {cid:>4}  {cnames[cid]:<26}  {cnt:>8,}  {cnt/total*100:>5.1f}%")

    print(f"\nall outputs in '{save_dir}/'\n")
