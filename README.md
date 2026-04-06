How the Recommendation System Works
The core of this project is a content-based recommendation engine that suggests perfumes similar to a user’s favorite, using a combination of perfume notes, main accords, brand tiers, and popularity.
# Perfume Recommendation System

A full-stack web application for content-based perfume recommendations, leveraging modern machine learning and web technologies.

---

## Overview

This project provides personalized perfume recommendations based on user preferences, using a hybrid content-based filtering approach. The system consists of a **FastAPI** backend for data processing and recommendation logic, and a **React + TypeScript** frontend for an interactive user experience.

---

## Technologies Used

### Backend

- **Python 3.10+**
- **FastAPI**: High-performance web framework for building APIs.
- **Uvicorn**: ASGI server for running FastAPI.
- **Pandas, NumPy**: Data manipulation and numerical operations.
- **Scikit-learn**: Machine learning library for TF-IDF vectorization and similarity computation.
- **Pydantic**: Data validation and settings management.
- **CORS Middleware**: Enables secure cross-origin requests from the frontend.

### Frontend

- **React**: Component-based UI library.
- **TypeScript**: Type-safe JavaScript for robust frontend code.
- **Vite**: Fast build tool and development server.
- **Material UI (MUI)** and **Radix UI**: Modern, accessible UI components.
- **Custom CSS**: For additional styling and theming.

---

## System Architecture

```mermaid
graph TD
	A[User] -->|Interacts| B[React Frontend]
	B -->|API Calls| C[FastAPI Backend]
	C -->|Reads/Writes| D[Processed Perfume Data (CSV)]
	C -->|ML| E[Recommendation Engine (TF-IDF, Filtering)]
```

- **Frontend**: Users search for perfumes, select favorites, and receive recommendations.
- **Backend**: Handles API requests, processes data, and computes recommendations using content-based filtering (TF-IDF on notes/accords, brand tier filtering).
- **Data**: Raw perfume data is preprocessed and stored as CSV for efficient access.

---

## Features

- **Search perfumes** by name and brand.
- **Personalized recommendations** based on selected perfumes.
- **Brand tier filtering** (luxury, premium, mainstream, budget).
- **Modern, responsive UI** with real-time search and suggestions.

---

## How the Recommendation System Works

The core of this project is a **content-based recommendation engine** that suggests perfumes similar to a user’s favorite, using a combination of perfume notes, main accords, brand tiers, and popularity.

### 1. Data Representation

- **Perfume Notes**: Each perfume is described by its top, middle, and base notes (e.g., jasmine, vanilla).
- **Main Accords**: Ranked main scent families (e.g., floral, woody) are extracted and weighted.
- **Brand Tier**: Brands are classified into tiers (luxury, premium, mainstream, budget) for filtering.

### 2. Feature Engineering

- **TF-IDF Vectorization**: Each perfume is converted into a weighted vector using TF-IDF (Term Frequency-Inverse Document Frequency) on its notes and accords. This emphasizes unique or rare notes.
- **Position & Accord Weighting**: Top notes, middle notes, and base notes are weighted differently (e.g., top notes may be more important). Main accords are also ranked and weighted.

### 3. Similarity Computation

- **Cosine Similarity**: The system computes the cosine similarity between the user’s selected perfume and all others in the database, based on their feature vectors.

### 4. Popularity & Review Score

- **Popularity Score**: Each perfume’s popularity is calculated using its average rating and the number of reviews (log-scaled).
- **Hybrid Scoring**: The final recommendation score is a weighted combination of similarity (how close the perfumes are in scent profile) and popularity (how well-liked they are).

### 5. Brand Tier Filtering

- By default, recommendations are filtered to the same brand tier as the selected perfume (e.g., luxury perfumes recommend other luxury perfumes).
- Users can adjust this filter to broaden or narrow the results.

### 6. Recommendation Output

- The top N perfumes are returned, each with:
  - Name, brand, rating, review count
  - Similarity score
  - Brand tier

**Summary:**  
The system recommends perfumes by analyzing their scent composition and popularity, ensuring suggestions are both similar in fragrance and reputable among users. Brand tier filtering allows for more personalized and relevant recommendations.

---

## Getting Started

### Backend

1. **Install dependencies**:
	```bash
	pip install -r backend/requirements.txt
	```
2. **Run the backend server**:
	```bash
	uvicorn backend.main:app --reload
	```

### Frontend

1. **Install dependencies**:
	```bash
	cd frontend
	npm install
	```
2. **Start the development server**:
	```bash
	npm run dev
	```

---

## Data Preprocessing

- Raw perfume data (CSV) is cleaned and transformed using `backend/preprocess.py`.
- Processed data is stored in `data/processed/perfumes_processed.csv`.

---

## License

This project is for educational and demonstration purposes.
