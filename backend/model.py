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

# Accord-to-note-family mapping for boosting notes that belong to
# the perfume's declared accords.  Keys are accord strings (as they
# appear in mainaccord columns); values are sets of note keywords
# that belong to that accord family.
ACCORD_NOTE_MAP = {
    'floral':       {'rose', 'jasmine', 'lily', 'tuberose', 'iris', 'peony', 'violet',
                     'magnolia', 'orange blossom', 'neroli', 'geranium', 'ylang',
                     'freesia', 'osmanthus', 'frangipani', 'lotus', 'cherry blossom',
                     'hibiscus', 'peach blossom', 'almond blossom'},
    'white floral': {'jasmine', 'tuberose', 'lily', 'orange blossom', 'neroli',
                     'magnolia', 'gardenia'},
    'rose':         {'rose', 'bulgarian rose', 'turkish rose', 'rose absolute'},
    'citrus':       {'bergamot', 'lemon', 'orange', 'mandarin', 'grapefruit', 'lime',
                     'yuzu', 'citron', 'blood orange', 'tangerine', 'citruses',
                     'lemon verbena'},
    'woody':        {'cedar', 'sandalwood', 'vetiver', 'guaiac wood', 'patchouli',
                     'agarwood', 'oud', 'birch', 'oakmoss', 'tree moss', 'woody notes',
                     'precious woods', 'exotic woods', 'clearwood', 'australian sandalwood',
                     'pear wood', 'texas cedar', 'white woods', 'woodsy notes', 'blonde woods',
                     'brazilian redwood', 'amberwood'},
    'oud':          {'agarwood', 'oud', 'agarwood (oud)'},
    'amber':        {'amber', 'ambergris', 'labdanum', 'benzoin', 'cistus', 'cistus incanus'},
    'warm spicy':   {'cinnamon', 'clove', 'nutmeg', 'cardamom', 'saffron', 'pepper',
                     'pink pepper', 'black pepper', 'spicy notes', 'caraway'},
    'fresh spicy':  {'ginger', 'pepper', 'pink pepper', 'cardamom', 'clary sage',
                     'artemisia', 'mint'},
    'aromatic':     {'lavender', 'rosemary', 'sage', 'herbal notes', 'clary sage',
                     'artemisia', 'basil'},
    'musky':        {'musk', 'white musk', 'ambrette', 'ambrette (musk mallow)'},
    'powdery':      {'iris', 'violet', 'heliotrope', 'orris', 'aldehydes'},
    'sweet':        {'vanilla', 'tonka bean', 'praline', 'caramel', 'honey',
                     'benzoin', 'heliotrope', 'meringue'},
    'fruity':       {'peach', 'apple', 'pear', 'berry', 'raspberry', 'strawberry',
                     'blackcurrant', 'plum', 'mango', 'pineapple', 'watermelon',
                     'passion fruit', 'fig', 'cherry', 'almond', 'coconut', 'melon',
                     'cranberry', 'red apple', 'green apple', 'guava', 'papaya'},
    'aquatic':      {'sea notes', 'marine', 'ocean', 'water', 'aquatic', 'ozonic notes',
                     'head space waterfall'},
    'ozonic':       {'ozonic notes', 'sea notes', 'marine', 'ozone', 'watermelon'},
    'green':        {'green notes', 'grass', 'violet leaf', 'fig leaf', 'galbanum',
                     'moss', 'oakmoss', 'fern'},
    'leather':      {'leather', 'suede', 'birch tar'},
    'tropical':     {'coconut', 'mango', 'pineapple', 'passion fruit', 'tiare', 'frangipani'},
    'smoky':        {'smoke', 'incense', 'tobacco', 'birch tar', 'vetiver'},
    'earthy':       {'patchouli', 'vetiver', 'oakmoss', 'tree moss', 'moss', 'earth'},
    'mineral':      {'mineral', 'concrete', 'salt', 'ambergris'},
    'nutty':        {'almond', 'walnut', 'hazelnut', 'pistachio'},
    'soapy':        {'musk', 'aldehydes', 'iris', 'violet'},
    'cinnamon':     {'cinnamon'},
    'vanilla':      {'vanilla', 'tonka bean', 'benzoin'},
}


class PerfumeRecommender:
    """
    Content-based perfume recommendation system using TF-IDF weighted vectors
    with position and accord weighting, plus brand tier filtering.
    """

    def __init__(
        self,
        w_top: float = 3.0,
        w_middle: float = 2.0,
        w_base: float = 1.0,
        accord_boost: float = 2.0,
        alpha: float = 0.7,
        beta: float = 0.3,
        gamma: float = 0.85,          # FIX D: raised from 0.65 → trust similarity more
        min_reviews_default: int = 50, # FIX C: lowered from 100 → less aggressive filtering
    ):
        """
        Initialize recommender with hyperparameters.

        Parameters
        ----------
        w_top, w_middle, w_base : float
            Position weights for note pyramid.
        accord_boost : float
            Multiplicative boost applied to a note whose family matches
            one of the perfume's declared accords.  Replaces the old
            accord_weights list that compared note strings against accord
            strings directly (they are different taxonomies — FIX A).
        alpha, beta : float
            Review score composition (rating vs log-review-count).
        gamma : float
            Similarity weight in final score.  0.85 → 85 % similarity,
            15 % popularity.  Raised from 0.65 so recommendations are
            actually driven by scent similarity.
        min_reviews_default : int
            Default minimum review threshold passed to recommend().
        """
        self.w_top = w_top
        self.w_middle = w_middle
        self.w_base = w_base
        self.accord_boost = accord_boost
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.min_reviews_default = min_reviews_default

        self.note_vocab = {}
        self.idf_values = {}
        self.perfume_vectors = None
        self.normalized_vectors = None
        self.df = None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def format_name(user_input: str) -> str:
        """Convert user input to dataset format: 'No 5' → 'no-5'."""
        return user_input.lower().strip().replace(' ', '-').replace('.', '')

    @staticmethod
    def get_brand_tier(brand: str) -> str:
        """Return the tier classification of a brand."""
        brand_lower = brand.lower().strip()
        for tier, brands in BRAND_TIERS.items():
            if brand_lower in brands:
                return tier
        return 'unknown'

    def _parse_notes(self, notes_str: str) -> List[str]:
        """Parse a comma/semicolon-separated notes string into a list."""
        if pd.isna(notes_str) or notes_str == '':
            return []
        notes = str(notes_str).replace(';', ',').split(',')
        return [note.strip().lower() for note in notes if note.strip()]

    def _note_accord_boost(self, note: str, accords: List[str]) -> float:
        """
        FIX A — Correct accord boosting logic.

        The old code compared note strings directly against accord strings
        (e.g. "rose" in ["floral", "woody"]).  Those are different
        taxonomies and almost never match, so the boost was never applied.

        New approach: look up each declared accord in ACCORD_NOTE_MAP and
        check whether the note belongs to that accord's note family.  If
        it matches any of the perfume's top-ranked accords, apply the
        accord_boost multiplier.
        """
        for accord in accords:
            note_family = ACCORD_NOTE_MAP.get(accord.lower().strip(), set())
            if note in note_family:
                return self.accord_boost
        return 1.0

    def _build_vocabulary(self, df: pd.DataFrame) -> dict:
        """Build global note vocabulary from the dataset."""
        all_notes = set()
        for col in ['top_notes', 'middle_notes', 'base_notes']:
            if col in df.columns:
                for notes_str in df[col].dropna():
                    all_notes.update(self._parse_notes(notes_str))
        return {note: idx for idx, note in enumerate(sorted(all_notes))}

    def _compute_idf(self, df: pd.DataFrame) -> dict:
        """Compute IDF (Inverse Document Frequency) for each note."""
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
            # Smooth IDF to prevent extreme values for very rare notes
            idf[note] = np.log((N + 1) / (df_j + 1)) + 1 if df_j > 0 else 0
        return idf

    def _create_perfume_vector(self, row: pd.Series) -> np.ndarray:
        """
        Create a weighted feature vector for a perfume.

        Weight = w_position × accord_boost × IDF
        """
        d = len(self.note_vocab)
        vector = np.zeros(d)

        accords = []
        if 'main_accords' in row.index and pd.notna(row.get('main_accords', '')):
            accords = self._parse_notes(row['main_accords'])

        note_positions = [
            ('top_notes',    self.w_top),
            ('middle_notes', self.w_middle),
            ('base_notes',   self.w_base),
        ]

        for col, w_position in note_positions:
            if col in row.index and pd.notna(row[col]):
                notes = self._parse_notes(row[col])
                for note in notes:
                    if note in self.note_vocab:
                        idx = self.note_vocab[note]
                        idf = self.idf_values.get(note, 0)
                        # FIX A: use taxonomy-aware boost instead of direct string match
                        w_accord = self._note_accord_boost(note, accords)
                        vector[idx] = w_position * w_accord * idf

        return vector

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def fit(self, df: pd.DataFrame) -> 'PerfumeRecommender':
        """Train the recommendation model."""
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

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def _compute_review_score(self, row: pd.Series) -> float:
        """Compute a normalised popularity score from rating + review count."""
        review_count = row.get('review_count', 0)
        rating = row.get('rating', 0)

        max_reviews = self.df['review_count'].max()
        r_count_norm = np.log(1 + review_count) / np.log(1 + max_reviews) if max_reviews > 0 else 0
        r_avg_norm = rating / 5.0 if rating > 0 else 0

        return self.alpha * r_avg_norm + self.beta * r_count_norm

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def search(
        self,
        perfume_name: str,
        brand: Optional[str] = None,
        top_n: int = 10,
    ) -> pd.DataFrame:
        """
        Search for perfumes in the database.

        Parameters
        ----------
        perfume_name : str
            Perfume name (spaces allowed).
        brand : str, optional
            Brand name to narrow results.
        top_n : int
            Maximum number of results.
        """
        formatted_name = self.format_name(perfume_name)
        mask = self.df['name'].str.contains(formatted_name, case=False, na=False, regex=False)

        if brand:
            formatted_brand = brand.lower().strip()
            mask = mask & self.df['brand_clean'].str.contains(
                formatted_brand, case=False, na=False, regex=False
            )

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
        min_reviews: Optional[int] = None,
    ) -> Tuple[pd.DataFrame, dict]:
        """
        Get perfume recommendations with brand-tier filtering.

        Parameters
        ----------
        perfume_name : str
            Name of the query perfume.
        brand : str, optional
            Brand name to identify the perfume more precisely.
        top_n : int
            Number of recommendations to return.
        same_tier : bool
            If True, restrict candidates to the same brand tier
            (luxury / premium / mainstream / budget).
        min_reviews : int, optional
            Minimum review-count threshold.  Defaults to
            self.min_reviews_default (50).  Automatically relaxed when
            the filtered candidate pool is too small (FIX C).

        Returns
        -------
        (recommendations_df, metadata_dict)
        """
        if min_reviews is None:
            min_reviews = self.min_reviews_default

        # ── 1. Find the query perfume ──────────────────────────────────
        matches = self.search(perfume_name, brand=brand, top_n=20)

        if len(matches) == 0:
            return pd.DataFrame(), {'error': f'Perfume "{perfume_name}" not found'}

        input_perfume_idx = matches.index[0]
        input_perfume = matches.iloc[0]

        metadata = {
            'input_name':    input_perfume['name'],
            'input_brand':   input_perfume['Brand'],
            'input_rating':  float(input_perfume['rating']),
            'input_reviews': int(input_perfume['review_count']),
            'input_tier':    self.get_brand_tier(input_perfume['brand_clean']),
        }

        # ── 2. Compute cosine similarities against all perfumes ────────
        input_vector = self.normalized_vectors[input_perfume_idx]
        nonzero = np.count_nonzero(input_vector)
        print(f"DEBUG: Non-zero dims for '{metadata['input_name']}': {nonzero}")
        if nonzero == 0:
            print("WARNING: Input perfume has no notes in vocabulary. "
                  "Recommendations will be popularity-based only.")

        similarity_scores = self.normalized_vectors @ input_vector

        # ── 3. Build candidate pool (FIX B: applied exactly once) ──────
        candidates = self.df.copy()

        if same_tier and metadata['input_tier'] != 'unknown':
            tier_brands = BRAND_TIERS[metadata['input_tier']]
            candidates = candidates[candidates['brand_clean'].isin(tier_brands)]
            metadata['filtered_by_tier'] = metadata['input_tier']

        # Apply min-reviews filter; FIX C: relax if pool is too small
        candidates_filtered = candidates[candidates['review_count'] >= min_reviews]
        min_pool_size = top_n * 3
        if len(candidates_filtered) < min_pool_size:
            print(
                f"WARNING: Pool too small ({len(candidates_filtered)} perfumes) "
                f"after min_reviews={min_reviews} filter. Relaxing to 10."
            )
            candidates_filtered = candidates[candidates['review_count'] >= 10]
            metadata['relaxed_min_reviews'] = True

        candidates = candidates_filtered
        metadata['min_reviews_used'] = min_reviews
        metadata['candidate_pool_size'] = len(candidates)

        if len(candidates) == 0:
            return pd.DataFrame(), {**metadata, 'error': 'No candidates after filtering'}

        # ── 4. Compute popularity scores for candidates ────────────────
        review_scores = candidates.apply(self._compute_review_score, axis=1).values
        if review_scores.max() > 0:
            review_scores = review_scores / review_scores.max()

        # ── 5. Blend similarity + popularity (FIX D: gamma=0.85) ──────
        candidate_indices = candidates.index.tolist()
        candidate_similarities = similarity_scores[candidate_indices]
        final_scores = self.gamma * candidate_similarities + (1 - self.gamma) * review_scores

        # Exclude the query perfume itself
        input_mask = candidates.index == input_perfume_idx
        final_scores[input_mask] = -1.0

        # ── 6. Rank and return top N ───────────────────────────────────
        top_indices_local = np.argsort(final_scores)[::-1][:top_n]
        top_indices_global = [candidate_indices[i] for i in top_indices_local]

        results = self.df.loc[top_indices_global].copy()
        results['similarity']  = similarity_scores[top_indices_global]
        results['final_score'] = final_scores[top_indices_local]
        results['brand_tier']  = results['brand_clean'].apply(self.get_brand_tier)

        # NOTE: FIX B — the duplicate tier-filter block that was here has
        # been removed.  It re-ran after final_scores was already computed
        # and could corrupt the `candidates` variable used upstream.

        metadata['recommendations_count'] = len(results)
        metadata['avg_similarity'] = float(results['similarity'].mean())

        return results, metadata

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, filepath: str) -> None:
        """Save the trained model to disk."""
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
        print(f"Model saved to {filepath}")

    @staticmethod
    def load(filepath: str) -> 'PerfumeRecommender':
        """Load a trained model from disk."""
        with open(filepath, 'rb') as f:
            model = pickle.load(f)
        print(f"Model loaded from {filepath}")
        return model


# Compatibility export: preserve the experimental implementation above while
# directing existing ``from model import PerfumeRecommender`` callers to the
# single audited engine used by the API.
try:
    from .recommendation_engine import (
        BRAND_TIERS,
        MODEL_VERSION,
        NOTE_ALIASES,
        PerfumeRecommender,
        RecommendationConfig,
        normalize_note,
        normalize_perfume,
        parse_notes,
    )
except ImportError:
    from recommendation_engine import (
        BRAND_TIERS,
        MODEL_VERSION,
        NOTE_ALIASES,
        PerfumeRecommender,
        RecommendationConfig,
        normalize_note,
        normalize_perfume,
        parse_notes,
    )
