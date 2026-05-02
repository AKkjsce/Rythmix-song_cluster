import os
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_from_directory

base_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__,
            template_folder=os.path.join(base_dir, 'templates'),
            static_folder=os.path.join(base_dir, 'static'))

csv_file = os.path.join(base_dir, "..", "outputs", "clustered_tracks.csv")

# load everything upfront - searching a 16mb csv on every keystroke is too slow
print("loading track data...")
try:
    cols = ["track_name", "artists", "track_genre", "cluster"]
    song_data = pd.read_csv(csv_file, usecols=cols).dropna()
    song_data["cluster"] = song_data["cluster"].astype(int)
    print(f"got {len(song_data):,} tracks")
except FileNotFoundError:
    print("csv not found - run main.py first")
    song_data = pd.DataFrame()
except Exception as e:
    print(f"error loading data: {e}")
    song_data = pd.DataFrame()


@app.route("/")
def homepage():
    return render_template("index.html")


@app.route("/api/search")
def do_search():
    q = request.args.get("q", "").strip().lower()
    cluster_filter = request.args.get("cluster", "")

    if not q or song_data.empty:
        return jsonify([])

    by_name = song_data["track_name"].str.lower().str.contains(q, na=False)
    by_artist = song_data["artists"].str.lower().str.contains(q, na=False)
    matches = song_data[by_name | by_artist]

    if cluster_filter != "":
        matches = matches[matches["cluster"] == int(cluster_filter)]

    return jsonify(matches.head(50).to_dict(orient="records"))


@app.route("/api/cluster/<int:cid>")
def get_cluster_songs(cid):
    limit = int(request.args.get("limit", 10))
    exclude = request.args.get("exclude", "").strip().lower()

    if song_data.empty:
        return jsonify([])

    cluster_songs = song_data[song_data["cluster"] == cid].copy()

    if exclude:
        # drop the track the user is already looking at
        cluster_songs = cluster_songs[
            ~cluster_songs["track_name"].str.lower().str.contains(exclude, na=False)
        ]

    if cluster_songs.empty:
        return jsonify([])

    picked = cluster_songs.sample(min(limit, len(cluster_songs)))
    return jsonify(picked.to_dict(orient="records"))


@app.route("/api/clusters")
def list_all_clusters():
    if song_data.empty:
        return jsonify([])

    counts = song_data["cluster"].value_counts().sort_index().reset_index()
    counts.columns = ["cluster_id", "track_count"]
    return jsonify(counts.to_dict(orient="records"))


@app.route("/outputs/<path:fname>")
def get_output_file(fname):
    out_folder = os.path.join(base_dir, "..", "outputs")
    return send_from_directory(out_folder, fname)


if __name__ == "__main__":
    app.run(port=5000)
