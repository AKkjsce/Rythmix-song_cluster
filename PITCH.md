# Project Pitch: "Rythmix" – Acoustic-Based Music Discovery & Clustering System

## The Problem
Most modern music platforms rely heavily on predefined **genre labels** to organize and recommend songs. While this approach is convenient, it limits true music discovery.

For example, a song categorized as *Pop* might actually share more acoustic similarity—such as tempo, energy, or rhythm—with an *EDM* track than with another Pop song. However, due to rigid genre classification, these connections are rarely explored.

As a result, users remain confined within genre boundaries and miss out on discovering music that genuinely *sounds similar*.

---

## The Solution: Rythmix
**Rythmix** is a data-driven music discovery system that removes dependency on genre labels. Instead, it groups songs purely based on their **acoustic characteristics**.

The system processes a large dataset of Spotify tracks and intentionally ignores:
- Track names  
- Artist names  
- Genre labels  

Instead, it analyzes the following 9 acoustic features:
1. Danceability  
2. Energy  
3. Valence (musical positivity)  
4. Tempo (BPM)  
5. Acousticness  
6. Loudness  
7. Speechiness  
8. Instrumentalness  
9. Liveness  

---

## How It Works

### 1. Data Processing
The system cleans the dataset by removing missing values and duplicate entries based on track and artist combinations. It then extracts only the relevant acoustic features for further processing.

### 2. Feature Standardization
Since each feature operates on a different scale (e.g., tempo vs. acousticness), the data is normalized using **StandardScaler** to ensure fair comparison across all attributes.

### 3. Optimal Cluster Selection
The model evaluates multiple cluster sizes and determines the most suitable number using:
- **BIC (Bayesian Information Criterion)**  
- **AIC (Akaike Information Criterion)**  

This ensures meaningful and well-separated clusters.

### 4. Clustering using GMM
Rythmix uses **Gaussian Mixture Models (GMM)** instead of simpler algorithms. This allows:
- Flexible cluster shapes  
- Better handling of overlapping data  
- More realistic grouping of music patterns  

### 5. Acoustic Profiling
Each cluster is analyzed to generate a unique “acoustic signature,” representing how songs behave across all selected features.

### 6. Interactive Web Interface
Rythmix includes a lightweight web application built using **Flask and JavaScript**, allowing users to:
- Search songs across the dataset  
- Filter songs by acoustic clusters  
- View cluster assignments  
- Discover similar tracks based on acoustic similarity  

---

## Why It Matters
Rythmix challenges the traditional way music is categorized. Instead of relying on industry-defined labels, it focuses on the **actual sound structure** of songs.

This approach enables:
- Better cross-genre discovery  
- Smarter playlist creation  
- Deeper understanding of musical relationships  

Rythmix demonstrates that music is more interconnected than genres suggest, offering a more natural and intuitive way to explore and discover sound.