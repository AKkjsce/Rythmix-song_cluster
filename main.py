import argparse
import time

from src.acquire    import load_and_clean
from src.features   import pick_features
from src.preprocess import DataScaler
from src.choose_k   import evaluate_k_range
from src.train      import run_gmm
from src.analyse    import generate_analysis


def get_args():
    p = argparse.ArgumentParser(description="rythmix - acoustic clustering for spotify tracks")
    p.add_argument("--data", default="data/dataset.csv", help="path to csv")
    p.add_argument("--k", type=int, default=None, help="fix cluster count, skips search")
    p.add_argument("--sample", type=int, default=None, help="subsample size for k search")
    return p.parse_args()


def main():
    args = get_args()
    t0 = time.perf_counter()

    print("\nrythmix starting up...")

    tracks = load_and_clean(args.data)
    feats, info = pick_features(tracks)

    scaler = DataScaler(num_pca_dims=2)
    scaled = scaler.scale_data(feats)

    if args.k is not None:
        k = args.k
        print(f"using k={k} from flag, skipping search")
    else:
        if args.sample and args.sample < len(scaled):
            import numpy as np
            rng = np.random.default_rng(1337)
            idx = rng.choice(len(scaled), size=args.sample, replace=False)
            search_data = scaled[idx]
            print(f"subsampling {args.sample:,} rows for k search")
        else:
            search_data = scaled

        k = evaluate_k_range(search_data, min_k=6)

    tracks = run_gmm(tracks, scaled, scaler, k)
    generate_analysis(tracks, scaled, scaler, k)

    elapsed = time.perf_counter() - t0
    print(f"\ndone in {elapsed:.1f}s. check outputs/")


if __name__ == "__main__":
    main()
