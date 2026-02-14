"""
FastAPI Backend for Perfume Recommender
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import pandas as pd
from model import PerfumeRecommender

# Initialize FastAPI app
app = FastAPI(
    title="Perfume Recommendation API",
    description="Content-based perfume recommendations using TF-IDF and hybrid ranking",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
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
    top_n: int = Field(5, ge=1, le=20, description="Number of recommendations")
    same_tier: bool = Field(True, description="Filter by same brand tier")
    min_reviews: int = Field(100, ge=0, description="Minimum review count")


class PerfumeInfo(BaseModel):
    name: str
    brand: str
    rating: float
    review_count: int
    similarity: Optional[float] = None
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
        # Try to load pre-trained model
        recommender = PerfumeRecommender.load('../data/processed/model.pkl')
    except FileNotFoundError:
        # If not found, load data and train
        print("Pre-trained model not found, loading data...")
        df = pd.read_csv('../data/processed/perfumes_processed.csv')
        recommender = PerfumeRecommender()
        recommender.fit(df)
        recommender.save('../data/processed/model.pkl')
    
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
        "total_perfumes": len(recommender.df) if recommender else 0
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
        top_n=request.top_n,
        same_tier=request.same_tier,
        min_reviews=request.min_reviews
    )
    
    if 'error' in metadata:
        raise HTTPException(status_code=404, detail=metadata['error'])
    
    # Input perfume info
    input_perfume = PerfumeInfo(
        name=metadata['input_name'],
        brand=metadata['input_brand'],
        rating=metadata['input_rating'],
        review_count=metadata['input_reviews'],
        brand_tier=metadata['input_tier']
    )
    
    # Recommendations
    recommendations = [
        PerfumeInfo(
            name=row['name'],
            brand=row['Brand'],
            rating=float(row['rating']),
            review_count=int(row['review_count']),
            similarity=float(row['similarity']),
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
    from model import BRAND_TIERS
    return BRAND_TIERS


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)