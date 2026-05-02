import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.mixture import GaussianMixture


def evaluate_k_range(scaled_data, min_k=6, max_k=15, save_dir="outputs"):
    os.makedirs(save_dir, exist_ok=True)

    # cap at 30k rows so this doesn't take all day on big datasets
    n = min(30000, len(scaled_data))
    if n < len(scaled_data):
        rng = np.random.default_rng(1337)
        test_data = scaled_data[rng.choice(len(scaled_data), size=n, replace=False)]
    else:
        test_data = scaled_data

    ks = list(range(min_k, max_k + 1))
    bics, aics = [], []

    print(f"testing k={min_k}..{max_k}")
    print(f"  {'k':>3}  {'bic':>14}  {'aic':>14}")

    for k in ks:
        m = GaussianMixture(n_components=k, covariance_type='diag', n_init=2, random_state=None)
        m.fit(test_data)
        b, a = m.bic(test_data), m.aic(test_data)
        bics.append(b)
        aics.append(a)
        print(f"  {k:>3}  {b:>14,.1f}  {a:>14,.1f}")

    best_k = ks[int(np.argmin(bics))]
    print(f"  -> best k={best_k} (lowest bic)\n")

    _plot_bic(ks, bics, aics, best_k, save_dir)
    return best_k


def _plot_bic(ks, bics, aics, best_k, save_dir):
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#16213e")

    ax.plot(ks, bics, color="#e94560", lw=1.8, marker="o", ms=5, label="BIC")
    ax.plot(ks, aics, color="#53d8fb", lw=1.8, marker="s", ms=5, ls="--", label="AIC")
    ax.axvline(x=best_k, color="#f5a623", ls=":", lw=1.5, label=f"best k={best_k}")

    ax.set_xlabel("k", color="white")
    ax.set_ylabel("score (lower = better)", color="white")
    ax.tick_params(colors="white")

    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["bottom", "left"]:
        ax.spines[s].set_color("#555")

    ax.legend(facecolor="#1a1a2e", labelcolor="white", framealpha=0.7,
              loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=3)
    plt.title("GMM k selection: BIC & AIC", color="white", fontsize=14, pad=12)
    plt.tight_layout()

    out = os.path.join(save_dir, "bic_aic_chart.png")
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  saved plot -> {out}")
