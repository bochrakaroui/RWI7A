"""
Perfume Recommendation Engine
Core recommendation model with brand tier filtering
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import normalize
import pickle
from typing import List, Optional, Tuple


# Brand tier classification
BRAND_TIERS = {
    'luxury': [
        'chanel', 'dior', 'hermes', 'guerlain', 'tom-ford', 'creed', 
        'ysl', 'givenchy', 'cartier', 'bvlgari', 'armani-prive',
        'louis-vuitton', 'bottega-veneta', 'maison-francis-kurkdjian'
    ],
    'premium': [
        'versace', 'prada', 'armani', 'burberry', 'valentino',
        'dolce-gabbana', 'carolina-herrera', 'mont-blanc', 'hugo-boss',
        'jimmy-choo', 'ralph-lauren', 'calvin-klein'
    ],
    'mainstream': [
        'estee-lauder', 'clinique', 'lancome', 'elizabeth-arden',
        'guess', 'davidoff', 'lacoste', 'jean-paul-gaultier'
    ],
    'budget': [
        'avon', 'coty', 'jovan', 'milton-lloyd', 'adidas', 'nike',
        'body-shop', 'bath-body-works'
    ]
}


class PerfumeRecommender:
    """
    Content-based perfume recommendation system using TF-IDF weighted vectors
    with position and accord weighting, plus brand tier filtering
    """
    
    def __init__(
        self,
        w_top: float = 3.0,
        w_middle: float = 2.0,
        w_base: float = 1.0,
        accord_weights: List[float] = [5, 4, 3, 2, 1],
        alpha: float = 0.7,
        beta: float = 0.3,
        gamma: float = 0.65
    ):
        """
        Initialize recommender with hyperparameters
        
        Parameters:
        -----------
        w_top, w_middle, w_base : float
            Position weights for note pyramid
        accord_weights : list
            Weights for ranked accords [1st, 2nd, 3rd, 4th, 5th]
        alpha, beta : float
            Review score composition (rating vs review count)
        gamma : float
            Similarity weight in final score (0.65 = 65% similarity, 35% popularity)
        """
        self.w_top = w_top
        self.w_middle = w_middle
        self.w_base = w_base
        self.accord_weights = accord_weights
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        
        self.note_vocab = {}
        self.idf_values = {}
        self.perfume_vectors = None
        self.normalized_vectors = None
        self.df = None
        
    @staticmethod
    def format_name(user_input: str) -> str:
        """Convert user input to dataset format: 'No 5' -> 'no-5'"""
        return user_input.lower().strip().replace(' ', '-').replace('.', '')
    
    @staticmethod
    def get_brand_tier(brand: str) -> str:
        """Get the tier classification of a brand"""
        brand_lower = brand.lower().strip()
        for tier, brands in BRAND_TIERS.items():
            if brand_lower in brands:
                return tier
        return 'unknown'
    
    def _parse_notes(self, notes_str: str) -> List[str]:
        """Parse comma-separated notes string"""
        if pd.isna(notes_str) or notes_str == '':
            return []
        notes = str(notes_str).replace(';', ',').split(',')
        return [note.strip().lower() for note in notes if note.strip()]
    
    def _build_vocabulary(self, df: pd.DataFrame) -> dict:
        """Build global note vocabulary from dataset"""
        all_notes = set()
        for col in ['top_notes', 'middle_notes', 'base_notes']:
            if col in df.columns:
                for notes_str in df[col].dropna():
                    all_notes.update(self._parse_notes(notes_str))
        return {note: idx for idx, note in enumerate(sorted(all_notes))}
    
    def _compute_idf(self, df: pd.DataFrame) -> dict:
        """Compute IDF (Inverse Document Frequency) for each note"""
        N = len(df)
        note_doc_count = {note: 0 for note in self.note_vocab}
        
        for col in ['top_notes', 'middle_notes', 'base_notes']:
            if col in df.columns:
                for notes_str in df[col].dropna():
                    notes = set(self._parse_notes(notes_str))
                    for note in notes:
                        if note in note_doc_count:
                            note_doc_count[note] += 1
        
        idf = {}
        for note, df_j in note_doc_count.items():
            idf[note] = np.log(N / df_j) if df_j > 0 else 0
        
        return idf
    
    def _create_perfume_vector(self, row: pd.Series) -> np.ndarray:
        """Create weighted feature vector for a perfume"""
        d = len(self.note_vocab)
        vector = np.zeros(d)
        
        note_positions = [
            ('top_notes', self.w_top),
            ('middle_notes', self.w_middle),
            ('base_notes', self.w_base)
        ]
        
        for col, w_position in note_positions:
            if col in row.index and pd.notna(row[col]):
                notes = self._parse_notes(row[col])
                for note in notes:
                    if note in self.note_vocab:
                        idx = self.note_vocab[note]
                        idf = self.idf_values.get(note, 0)
                        
                        w_accord = 1.0
                        if 'main_accords' in row.index and pd.notna(row['main_accords']):
                            accords = self._parse_notes(row['main_accords'])
                            if note in accords:
                                accord_rank = accords.index(note)
                                if accord_rank < len(self.accord_weights):
                                    w_accord = self.accord_weights[accord_rank]
                        
                        vector[idx] = w_position * w_accord * idf
        
        return vector
    
    def fit(self, df: pd.DataFrame):
        """Train the recommendation model"""
        print("Training model...")
        
        self.df = df.copy()
        self.note_vocab = self._build_vocabulary(self.df)
        self.idf_values = self._compute_idf(self.df)
        
        print(f"Building vectors for {len(self.df)} perfumes...")
        vectors = [self._create_perfume_vector(row) for _, row in self.df.iterrows()]
        self.perfume_vectors = np.array(vectors)
        self.normalized_vectors = normalize(self.perfume_vectors, norm='l2', axis=1)
        
        print(f"Model trained: {len(self.note_vocab)} unique notes")
        return self
    
    def _compute_review_score(self, row: pd.Series) -> float:
        """Compute normalized review-based score"""
        review_count = row.get('review_count', 0)
        rating = row.get('rating', 0)
        
        max_reviews = self.df['review_count'].max()
        r_count_norm = np.log(1 + review_count) / np.log(1 + max_reviews) if max_reviews > 0 else 0
        r_avg_norm = rating / 5.0 if rating > 0 else 0
        
        return self.alpha * r_avg_norm + self.beta * r_count_norm
    
    def search(
        self,
        perfume_name: str,
        brand: Optional[str] = None,
        top_n: int = 10
    ) -> pd.DataFrame:
        """
        Search for perfumes in database
        
        Parameters:
        -----------
        perfume_name : str
            Perfume name (spaces allowed)
        brand : str, optional
            Brand name
        top_n : int
            Number of results
        """
        formatted_name = self.format_name(perfume_name)
        
        mask = self.df['name'].str.contains(formatted_name, case=False, na=False, regex=False)
        
        if brand:
            formatted_brand = brand.lower().strip()
            mask = mask & self.df['brand_clean'].str.contains(formatted_brand, case=False, na=False, regex=False)
        
        results = self.df[mask].copy()
        
        if len(results) == 0:
            return pd.DataFrame()
        
        results['popularity'] = results['rating'] * np.log1p(results['review_count'])
        results = results.sort_values('popularity', ascending=False).head(top_n)
        
        return results[['name', 'Brand', 'rating', 'review_count', 'brand_clean']]
    
    def recommend(
        self,
        perfume_name: str,
        brand: Optional[str] = None,
        top_n: int = 5,
        same_tier: bool = True,
        min_reviews: int = 100
    ) -> Tuple[pd.DataFrame, dict]:
        """
        Get perfume recommendations with brand tier filtering
        
        Parameters:
        -----------
        perfume_name : str
            Name of perfume
        brand : str, optional
            Brand name
        top_n : int
            Number of recommendations
        same_tier : bool
            Filter to same brand tier (luxury/premium/mainstream/budget)
        min_reviews : int
            Minimum review count threshold
            
        Returns:
        --------
        (recommendations_df, metadata_dict)
        """
        # Search for input perfume
        matches = self.search(perfume_name, brand=brand, top_n=20)
        
        if len(matches) == 0:
            return pd.DataFrame(), {'error': f'Perfume "{perfume_name}" not found'}
        
        # Get best match
        input_perfume_idx = matches.index[0]
        input_perfume = matches.iloc[0]
        
        metadata = {
            'input_name': input_perfume['name'],
            'input_brand': input_perfume['Brand'],
            'input_rating': float(input_perfume['rating']),
            'input_reviews': int(input_perfume['review_count']),
            'input_tier': self.get_brand_tier(input_perfume['brand_clean'])
        }
        
        # Get input vector
        input_vector = self.normalized_vectors[input_perfume_idx]
        
        # Compute similarity scores
        similarity_scores = self.normalized_vectors @ input_vector
        
        # Filter candidates
        candidates = self.df.copy()
        
        # Filter by brand tier if requested
        if same_tier and metadata['input_tier'] != 'unknown':
            tier_brands = BRAND_TIERS[metadata['input_tier']]
            candidates = candidates[candidates['brand_clean'].isin(tier_brands)]
            metadata['filtered_by_tier'] = metadata['input_tier']
        
        # Filter by minimum reviews
        candidates = candidates[candidates['review_count'] >= min_reviews]
        metadata['min_reviews'] = min_reviews
        
        # Compute review scores
        review_scores = candidates.apply(self._compute_review_score, axis=1).values
        if review_scores.max() > 0:
            review_scores = review_scores / review_scores.max()
        
        # Final scores
        candidate_indices = candidates.index.tolist()
        candidate_similarities = similarity_scores[candidate_indices]
        final_scores = self.gamma * candidate_similarities + (1 - self.gamma) * review_scores
        
        # Exclude input perfume
        input_mask = candidates.index == input_perfume_idx
        final_scores[input_mask] = -1
        
        # Get top N
        top_indices_local = np.argsort(final_scores)[::-1][:top_n]
        top_indices_global = [candidate_indices[i] for i in top_indices_local]
        
        # Build results
        results = self.df.loc[top_indices_global].copy()
        results['similarity'] = similarity_scores[top_indices_global]
        results['final_score'] = final_scores[top_indices_local]
        results['brand_tier'] = results['brand_clean'].apply(self.get_brand_tier)
        
        metadata['recommendations_count'] = len(results)
        metadata['avg_similarity'] = float(results['similarity'].mean())
        
        return results, metadata
    
    def save(self, filepath: str):
        """Save trained model to disk"""
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
        print(f"Model saved to {filepath}")
    
    @staticmethod
    def load(filepath: str):
        """Load trained model from disk"""
        with open(filepath, 'rb') as f:
            model = pickle.load(f)
        print(f"Model loaded from {filepath}")
        return model