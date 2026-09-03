"""
FastAPI Backend for Perfume Recommender
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from pathlib import Path
import os
import pickle
import pandas as pd

try:
    from .recommendation_engine import BRAND_TIERS, PerfumeRecommender
except ImportError:  # Supports `python -m uvicorn main:app` from backend/.
    from recommendation_engine import BRAND_TIERS, PerfumeRecommender


BACKEND_DIR = Path(__file__).resolve().parent
DATA_DIR = BACKEND_DIR.parent / "data" / "processed"
DATASET_PATH = DATA_DIR / "perfumes_processed.csv"
MODEL_PATH = DATA_DIR / "model_v2.pkl"
FRONTEND_ORIGINS = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").split(",")
    if origin.strip()
]

# Initialize FastAPI app
app = FastAPI(
    title="Perfume Recommendation API",
    description="Content-based perfume recommendations using TF-IDF and hybrid ranking",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instance
recommender: Optional[PerfumeRecommender] = None


# Request/Response models
class SearchRequest(BaseModel):
    query: str = Field(..., description="Perfume name to search for")
    brand: Optional[str] = Field(None, description="Brand name to filter by")
    top_n: int = Field(10, ge=1, le=50, description="Number of results")


class RecommendRequest(BaseModel):
    perfume_name: str = Field(..., description="Name of perfume you like")
    brand: Optional[str] = Field(None, description="Brand of the perfume")
    perfume_id: Optional[int] = Field(None, ge=0, description="Stable ID returned by search")
    top_n: int = Field(5, ge=1, le=20, description="Number of recommendations")
    same_tier: bool = Field(False, description="Optionally filter by the same brand tier")
    min_reviews: int = Field(0, ge=0, description="Optional minimum review count")


class PerfumeInfo(BaseModel):
    perfume_id: Optional[int] = None
    name: str
    brand: str
    rating: float
    review_count: int
    similarity: Optional[float] = None
    cosine_similarity: Optional[float] = None
    note_overlap_score: Optional[float] = None
    pyramid_score: Optional[float] = None
    accord_similarity: Optional[float] = None
    brand_tier: Optional[str] = None


class SearchResponse(BaseModel):
    results: List[PerfumeInfo]
    count: int


class RecommendationResponse(BaseModel):
    input: PerfumeInfo
    recommendations: List[PerfumeInfo]
    metadata: dict


# Startup/Shutdown events
@app.on_event("startup")
async def startup_event():
    """Load model and data on startup"""
    global recommender
    
    print("Loading model...")
    try:
        recommender = PerfumeRecommender.load(MODEL_PATH)
    except (FileNotFoundError, ValueError, AttributeError, EOFError, pickle.UnpicklingError) as error:
        print(f"Building recommendation index ({error})...")
        df = pd.read_csv(DATASET_PATH)
        recommender = PerfumeRecommender()
        recommender.fit(df)
        recommender.save(MODEL_PATH)
    
    print("Model ready")


# Health check
@app.get("/")
async def root():
    return {
        "message": "Perfume Recommendation API",
        "status": "active",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": recommender is not None,
        "total_perfumes": len(recommender.df) if recommender else 0,
        "recommendation_index": recommender.diagnostics() if recommender else None,
    }


# Search endpoint
@app.post("/search", response_model=SearchResponse)
async def search_perfumes(request: SearchRequest):
    """Search for perfumes by name and/or brand"""
    if recommender is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    results_df = recommender.search(
        perfume_name=request.query,
        brand=request.brand,
        top_n=request.top_n
    )
    
    if len(results_df) == 0:
        return SearchResponse(results=[], count=0)
    
    results = [
        PerfumeInfo(
            perfume_id=int(row['record_id']),
            name=row['name'],
            brand=row['Brand'],
            rating=float(row['rating']),
            review_count=int(row['review_count'])
        )
        for _, row in results_df.iterrows()
    ]
    
    return SearchResponse(results=results, count=len(results))


# Recommendation endpoint
@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendRequest):
    """Get personalized perfume recommendations"""
    if recommender is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    results_df, metadata = recommender.recommend(
        perfume_name=request.perfume_name,
        brand=request.brand,
        perfume_id=request.perfume_id,
        top_n=request.top_n,
        same_tier=request.same_tier,
        min_reviews=request.min_reviews
    )
    
    if 'error' in metadata:
        raise HTTPException(status_code=404, detail=metadata['error'])
    
    # Input perfume info
    input_perfume = PerfumeInfo(
        perfume_id=metadata['input_id'],
        name=metadata['input_name'],
        brand=metadata['input_brand'],
        rating=metadata['input_rating'],
        review_count=metadata['input_reviews'],
        brand_tier=metadata['input_tier']
    )
    
    # Recommendations
    recommendations = [
        PerfumeInfo(
            perfume_id=int(row['record_id']),
            name=row['name'],
            brand=row['Brand'],
            rating=float(row['rating']),
            review_count=int(row['review_count']),
            similarity=float(row['similarity']),
            cosine_similarity=float(row['cosine_similarity']),
            note_overlap_score=float(row['note_overlap_score']),
            pyramid_score=float(row['pyramid_score']),
            accord_similarity=float(row['accord_similarity']),
            brand_tier=row['brand_tier']
        )
        for _, row in results_df.iterrows()
    ]
    
    return RecommendationResponse(
        input=input_perfume,
        recommendations=recommendations,
        metadata=metadata
    )


# Get brands list
@app.get("/brands")
async def get_brands():
    """Get list of available brands"""
    if recommender is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    brands = recommender.df['Brand'].unique().tolist()
    brands.sort()
    
    return {
        "brands": brands,
        "count": len(brands)
    }


# Get brand tiers
@app.get("/tiers")
async def get_brand_tiers():
    """Get brand tier classification"""
    return BRAND_TIERS


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
