# Rythmix – Acoustic-Based Music Clustering & Discovery

Rythmix is a machine learning pipeline that processes over 100k Spotify tracks and groups them into clusters based purely on how they *sound*. Instead of relying on genre, artist, or track names, the system uses only acoustic features to uncover natural groupings in music.  

The results are then visualized and explored through a custom-built Flask web application.

---

## How to Use (Step-by-Step Workflow)

If you’ve cloned this project and want to run it locally, follow these steps:

### Step 1: Install Dependencies
Open your terminal in the project folder and run:
```bash
pip install -r requirements.txt
```

### Step 2: Get the dataset
The dataset is too big to put on GitHub. 
1. Go to Kaggle: https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset
2. Download `dataset.csv`
3. Put it in the `data/` folder. So the path should look exactly like: `Rythmix/data/dataset.csv`.

### Step 3: Run the pipeline
To execute the full pipeline (data cleaning, clustering, and visualization), run:
```bash
python main.py
```
*Note: The algorithm automatically tests cluster values between K = 6 and K = 15 to determine the most optimal number of groups using statistical methods.*

**Want it to run faster?**
If you already know how many clusters you want (let's say 5), you can skip the search!
```bash
python main.py --k 5
```

### Step 4: Launch the Frontend Web App!
After the clustering process completes, start the frontend:
```bash
python frontend/app.py
```
Open a browser and go to `http://127.0.0.1:5000`. Features of the Web App:
- **Global & Cluster-Based Search:** Search across all songs or within a specific acoustic cluster
- **Discover Similar Tracks:** Select a song and find other tracks with similar acoustic profiles
- **Cluster Exploration:** Browse songs grouped by their acoustic characteristics

---

## What's happening inside

The pipeline runs in 6 distinct phases (all separated out in the `src/` folder), plus a frontend app:

| File / Folder | What it does |
|---|---|
| `src/acquire.py` | Loads the CSV, drops missing values, and aggressively deduplicates by checking track names against artist names (purging 32,000+ hidden duplicates) |
| `src/features.py` | Extracts the 9 audio features we actually care about |
| `src/preprocess.py` | Normalizes the features so things like BPM don't overpower 0-to-1 features using `StandardScaler` |
| `src/choose_k.py` | Tries different cluster sizes (min K=6) and uses BIC & AIC scores to mathematically nail the sweet spot |
| `src/train.py` | Fits a Gaussian Mixture Model (GMM), assigns the labels, and translates the centroids back to human units |
| `src/analyse.py` | Makes the radar and scatter charts and automatically gives each cluster a descriptor name |
| `frontend/` | A lightweight vanilla Javascript & Flask web app to play with the clustered data |

## The Features We Used
- `danceability`
- `energy`
- `valence`
- `acousticness`
- `tempo`
- `loudness`
- `speechiness`
- `instrumentalness`
- `liveness`

## Summary

Rythmix provides a genre-independent way to explore music by focusing on the actual acoustic properties of songs. It enables users to discover patterns and relationships in music that are often hidden by traditional classification systems.