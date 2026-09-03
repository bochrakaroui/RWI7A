"""Sparse, note-primary perfume recommendation engine."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
import pickle
import re
import unicodedata
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.preprocessing import normalize


MODEL_VERSION = 4
NOTE_COLUMNS = ("top_notes", "middle_notes", "base_notes")
POSITION_NAMES = ("top", "middle", "base")

# Retained as an explicit compatibility filter. It is off by default and
# never contributes to similarity.
BRAND_TIERS = {
    "luxury": ["chanel", "dior", "hermes", "guerlain", "tom-ford", "creed",
               "ysl", "givenchy", "cartier", "bvlgari", "armani-prive",
               "louis-vuitton", "bottega-veneta", "maison-francis-kurkdjian"],
    "premium": ["versace", "prada", "armani", "burberry", "valentino",
                "dolce-gabbana", "carolina-herrera", "mont-blanc", "hugo-boss",
                "jimmy-choo", "ralph-lauren", "calvin-klein"],
    "mainstream": ["estee-lauder", "clinique", "lancome", "elizabeth-arden",
                   "guess", "davidoff", "lacoste", "jean-paul-gaultier"],
    "budget": ["avon", "coty", "jovan", "milton-lloyd", "adidas", "nike",
               "body-shop", "bath-body-works"],
}


@dataclass(frozen=True)
class RecommendationConfig:
    """All recommendation weights live in one validated configuration."""

    top_weight: float = 1.0
    middle_weight: float = 1.25
    base_weight: float = 1.5
    family_feature_weight: float = 0.30
    cosine_weight: float = 0.65
    overlap_weight: float = 0.20
    pyramid_weight: float = 0.10
    accord_weight: float = 0.05
    default_min_reviews: int = 0

    def __post_init__(self) -> None:
        if any(value <= 0 for value in self.position_weights.values()):
            raise ValueError("Pyramid position weights must be positive")
        if not 0 <= self.family_feature_weight <= 1:
            raise ValueError("family_feature_weight must be between 0 and 1")
        if any(value < 0 for value in self.score_weights.values()):
            raise ValueError("Similarity component weights cannot be negative")
        if not np.isclose(sum(self.score_weights.values()), 1.0):
            raise ValueError("Similarity component weights must sum to 1")
        if self.default_min_reviews < 0:
            raise ValueError("default_min_reviews cannot be negative")

    @property
    def position_weights(self) -> Dict[str, float]:
        return {"top": self.top_weight, "middle": self.middle_weight, "base": self.base_weight}

    @property
    def score_weights(self) -> Dict[str, float]:
        return {"cosine": self.cosine_weight,
                "overlap": self.overlap_weight,
                "pyramid": self.pyramid_weight,
                "accord": self.accord_weight}


# Only high-confidence equivalences and spelling corrections are collapsed.
# Original CSV fields remain untouched for display.
NOTE_ALIASES = {
    "agarwood": "oud",
    "agarwood oud": "oud",
    "ambrette musk mallow": "ambrette",
    "cardamon": "cardamom",
    "cedarwood": "cedar",
    "citruses": "citrus notes",
    "hiacynth": "hyacinth",
    "mandarin": "mandarin orange",
    "musk mallow": "ambrette",
    "olibanum": "frankincense",
    "tonka": "tonka bean",
    "virginian cedar": "virginia cedar",
    "woodsy notes": "woody notes",
}

# Variants retain their exact feature and share only a weak parent feature.
# Word boundaries prevent false matches such as rose/tuberose and rose/rosewood.
PARENT_NOTE_CONCEPTS = {
    "bergamot", "cedar", "iris", "jasmine", "lavender", "musk", "oud",
    "patchouli", "rose", "sandalwood", "vanilla", "vetiver",
}


def normalize_note(note: object) -> str:
    """Return a conservative canonical note name without changing display data."""

    if note is None or pd.isna(note):
        return ""
    value = unicodedata.normalize("NFKC", str(note)).casefold().strip()
    value = value.replace("?", "'").replace("&", " and ")
    value = re.sub(r"[\u2010-\u2015-]+", " ", value)
    value = value.replace("/", " ")
    value = re.sub(r"[()\[\]{}.,:]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip(" '\t\r\n")
    return NOTE_ALIASES.get(value, value)


def parse_notes(notes_value: object) -> List[str]:
    """Split comma/semicolon note lists, ignoring delimiters in parentheses."""

    if notes_value is None or pd.isna(notes_value):
        return []
    text = str(notes_value).strip()
    if not text:
        return []

    parts: List[str] = []
    current: List[str] = []
    depth = 0
    for character in text:
        if character in "([{" :
            depth += 1
        elif character in ")]}":
            depth = max(0, depth - 1)
        if character in ",;" and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(character)
    parts.append("".join(current))

    normalized: List[str] = []
    seen = set()
    for part in parts:
        note = normalize_note(part)
        if note and note not in seen:
            normalized.append(note)
            seen.add(note)
    return normalized


def normalize_perfume(row: Mapping[str, object]) -> Dict[str, Tuple[str, ...]]:
    """Build a separate normalized top/middle/base representation."""

    return {
        position: tuple(parse_notes(row.get(column, "")))
        for position, column in zip(POSITION_NAMES, NOTE_COLUMNS)
    }


def _parent_concepts(note: str) -> Tuple[str, ...]:
    words = set(note.split())
    return tuple(sorted(parent for parent in PARENT_NOTE_CONCEPTS if parent in words and note != parent))


def _weighted_jaccard(
    weighted_matrix: csr_matrix,
    row_weight_sums: np.ndarray,
    query_index: int,
) -> np.ndarray:
    query = weighted_matrix.getrow(query_index).copy()
    query.data[:] = 1.0
    intersections = (weighted_matrix @ query.T).toarray().ravel()
    unions = row_weight_sums + row_weight_sums[query_index] - intersections
    return np.divide(
        intersections,
        unions,
        out=np.zeros_like(intersections, dtype=np.float64),
        where=unions > 0,
    )


class PerfumeRecommender:
    """Fit-once sparse TF-IDF index with explainable hybrid note scoring."""

    def __init__(self, config: Optional[RecommendationConfig] = None) -> None:
        self.config = config or RecommendationConfig()
        self.model_version = MODEL_VERSION
        self.df: Optional[pd.DataFrame] = None
        self.normalized_profiles: List[Dict[str, Tuple[str, ...]]] = []
        self.normalized_accords: List[Tuple[str, ...]] = []
        self.identity_keys: List[Tuple[str, str]] = []

        self.note_vocab: Dict[str, int] = {}
        self.feature_vocab: Dict[str, int] = {}
        self.pyramid_vocab: Dict[str, int] = {}
        self.accord_vocab: Dict[str, int] = {}
        self.idf_values: Dict[str, float] = {}
        self.feature_idf_values: Dict[str, float] = {}
        self.note_doc_frequency: Dict[str, int] = {}

        self.perfume_vectors: Optional[csr_matrix] = None
        self.normalized_vectors: Optional[csr_matrix] = None
        self.note_presence_matrix: Optional[csr_matrix] = None
        self.pyramid_presence_matrix: Optional[csr_matrix] = None
        self.accord_presence_matrix: Optional[csr_matrix] = None
        self.note_weight_sums = np.array([], dtype=np.float64)
        self.pyramid_weight_sums = np.array([], dtype=np.float64)
        self.accord_weight_sums = np.array([], dtype=np.float64)
        self.vector_nonzero_mask = np.array([], dtype=bool)

    @staticmethod
    def format_name(user_input: str) -> str:
        return str(user_input).casefold().strip().replace(" ", "-").replace(".", "")

    @staticmethod
    def get_brand_tier(brand: str) -> str:
        brand_lower = str(brand).casefold().strip()
        for tier, brands in BRAND_TIERS.items():
            if brand_lower in brands:
                return tier
        return "unknown"

    # Backward-compatible private name used by older scripts.
    _parse_notes = staticmethod(parse_notes)

    def build_perfume_features(
        self,
        profile: Mapping[str, Sequence[str]],
    ) -> Dict[str, float]:
        """Build weighted term frequencies while preserving note identity."""

        features: Dict[str, float] = {}
        for position in POSITION_NAMES:
            position_weight = self.config.position_weights[position]
            for note in profile[position]:
                feature = f"note::{note}"
                features[feature] = max(features.get(feature, 0.0), position_weight)
                for parent in _parent_concepts(note):
                    family_feature = f"family::{parent}"
                    family_weight = position_weight * self.config.family_feature_weight
                    features[family_feature] = max(features.get(family_feature, 0.0), family_weight)
        return features

    def fit(self, df: pd.DataFrame) -> "PerfumeRecommender":
        """Normalize once, fit global IDF once, and create reusable sparse indices."""

        required = ("name", "Brand", *NOTE_COLUMNS)
        missing = [column for column in required if column not in df.columns]
        if missing:
            raise ValueError(f"Missing required perfume columns: {missing}")
        if df.empty:
            raise ValueError("Cannot fit the recommender on an empty dataset")

        prepared = df.copy().reset_index(drop=False).rename(columns={"index": "source_index"})
        prepared["record_id"] = np.arange(len(prepared), dtype=np.int64)
        if "brand_clean" not in prepared:
            prepared["brand_clean"] = prepared["Brand"].fillna("").astype(str).str.casefold().str.strip()
        for column in ("rating", "review_count"):
            if column not in prepared:
                prepared[column] = 0
            prepared[column] = pd.to_numeric(prepared[column], errors="coerce").fillna(0)
        prepared["review_count"] = prepared["review_count"].clip(lower=0).astype(np.int64)

        self.df = prepared
        records = prepared.to_dict("records")
        self.normalized_profiles = [normalize_perfume(row) for row in records]
        self.normalized_accords = [tuple(parse_notes(row.get("main_accords", ""))) for row in records]
        self.identity_keys = [
            (self.format_name(row["name"]), str(row["Brand"]).casefold().strip())
            for row in records
        ]

        self.build_vector_index()
        self._validate_index()
        return self

    def build_vector_index(self) -> None:
        """Fit vocabulary/IDF over the full corpus and cache sparse matrices."""

        if self.df is None:
            raise RuntimeError("No dataset has been fitted")
        document_count = len(self.df)
        perfume_features = [self.build_perfume_features(profile) for profile in self.normalized_profiles]

        note_documents: Counter[str] = Counter()
        feature_documents: Counter[str] = Counter()
        pyramid_documents: Counter[str] = Counter()
        accord_documents: Counter[str] = Counter()
        for profile, features, accords in zip(
            self.normalized_profiles, perfume_features, self.normalized_accords
        ):
            notes = {note for position in POSITION_NAMES for note in profile[position]}
            note_documents.update(notes)
            feature_documents.update(features)
            pyramid_documents.update(
                f"{position}::{note}"
                for position in POSITION_NAMES
                for note in profile[position]
            )
            accord_documents.update(set(accords))

        self.note_vocab = {note: index for index, note in enumerate(sorted(note_documents))}
        self.feature_vocab = {feature: index for index, feature in enumerate(sorted(feature_documents))}
        self.pyramid_vocab = {feature: index for index, feature in enumerate(sorted(pyramid_documents))}
        self.accord_vocab = {accord: index for index, accord in enumerate(sorted(accord_documents))}
        self.note_doc_frequency = dict(note_documents)
        self.idf_values = {
            note: float(np.log((document_count + 1) / (frequency + 1)) + 1)
            for note, frequency in note_documents.items()
        }
        self.feature_idf_values = {
            feature: float(np.log((document_count + 1) / (frequency + 1)) + 1)
            for feature, frequency in feature_documents.items()
        }

        vector_rows: List[int] = []
        vector_columns: List[int] = []
        vector_data: List[float] = []
        note_rows: List[int] = []
        note_columns: List[int] = []
        note_data: List[float] = []
        pyramid_rows: List[int] = []
        pyramid_columns: List[int] = []
        pyramid_data: List[float] = []
        accord_rows: List[int] = []
        accord_columns: List[int] = []

        for row_index, (profile, features, accords) in enumerate(
            zip(self.normalized_profiles, perfume_features, self.normalized_accords)
        ):
            for feature, term_weight in features.items():
                vector_rows.append(row_index)
                vector_columns.append(self.feature_vocab[feature])
                vector_data.append(term_weight * self.feature_idf_values[feature])

            row_notes = {note for position in POSITION_NAMES for note in profile[position]}
            for note in row_notes:
                note_rows.append(row_index)
                note_columns.append(self.note_vocab[note])
                note_data.append(self.idf_values[note])

            for position in POSITION_NAMES:
                position_weight = self.config.position_weights[position]
                for note in profile[position]:
                    feature = f"{position}::{note}"
                    pyramid_rows.append(row_index)
                    pyramid_columns.append(self.pyramid_vocab[feature])
                    pyramid_data.append(position_weight * self.idf_values[note])
            for accord in accords:
                accord_rows.append(row_index)
                accord_columns.append(self.accord_vocab[accord])

        self.perfume_vectors = csr_matrix(
            (vector_data, (vector_rows, vector_columns)),
            shape=(document_count, len(self.feature_vocab)),
            dtype=np.float32,
        )
        self.normalized_vectors = normalize(self.perfume_vectors, norm="l2", axis=1, copy=True)
        self.note_presence_matrix = csr_matrix(
            (note_data, (note_rows, note_columns)),
            shape=(document_count, len(self.note_vocab)),
            dtype=np.float32,
        )
        self.pyramid_presence_matrix = csr_matrix(
            (pyramid_data, (pyramid_rows, pyramid_columns)),
            shape=(document_count, len(self.pyramid_vocab)),
            dtype=np.float32,
        )
        self.accord_presence_matrix = csr_matrix(
            (np.ones(len(accord_rows), dtype=np.float32), (accord_rows, accord_columns)),
            shape=(document_count, len(self.accord_vocab)),
            dtype=np.float32,
        )
        self.note_weight_sums = np.asarray(self.note_presence_matrix.sum(axis=1)).ravel()
        self.pyramid_weight_sums = np.asarray(self.pyramid_presence_matrix.sum(axis=1)).ravel()
        self.accord_weight_sums = np.asarray(self.accord_presence_matrix.sum(axis=1)).ravel()
        self.vector_nonzero_mask = self.perfume_vectors.getnnz(axis=1) > 0

    def _validate_index(self) -> None:
        """Fail fast if record IDs, rows, dimensions, ordering, or values drift."""

        if self.df is None or self.perfume_vectors is None or self.normalized_vectors is None:
            raise RuntimeError("Vector index is incomplete")
        expected_rows = len(self.df)
        expected_ids = np.arange(expected_rows, dtype=np.int64)
        if not isinstance(self.df.index, pd.RangeIndex):
            raise AssertionError("Fitted DataFrame index must be a RangeIndex")
        if not np.array_equal(self.df["record_id"].to_numpy(), expected_ids):
            raise AssertionError("Vector rows and perfume record IDs are misaligned")
        matrices = (self.perfume_vectors, self.normalized_vectors,
                    self.note_presence_matrix, self.pyramid_presence_matrix,
                    self.accord_presence_matrix)
        if any(matrix is None or matrix.shape[0] != expected_rows for matrix in matrices):
            raise AssertionError("A feature matrix has the wrong row count")
        if self.perfume_vectors.shape[1] != len(self.feature_vocab):
            raise AssertionError("Feature vocabulary and vector dimensions differ")
        if not np.isfinite(self.perfume_vectors.data).all() or (self.perfume_vectors.data < 0).any():
            raise AssertionError("Feature vectors contain invalid values")

    def search(
        self,
        perfume_name: str,
        brand: Optional[str] = None,
        top_n: int = 10,
    ) -> pd.DataFrame:
        """Search names, prioritizing exact identity and returning stable IDs."""

        if self.df is None:
            raise RuntimeError("Recommender has not been fitted")
        formatted_name = self.format_name(perfume_name)
        names = self.df["name"].fillna("").astype(str).str.casefold()
        mask = names.str.contains(formatted_name, regex=False)

        formatted_brand = None
        if brand:
            formatted_brand = str(brand).casefold().strip()
            brands = self.df["brand_clean"].fillna("").astype(str).str.casefold()
            exact_brand = brands.eq(formatted_brand)
            mask &= exact_brand if (mask & exact_brand).any() else brands.str.contains(formatted_brand, regex=False)

        results = self.df.loc[mask].copy()
        if results.empty:
            return pd.DataFrame()
        results["_exact_name"] = results["name"].fillna("").astype(str).str.casefold().eq(formatted_name)
        results["_exact_brand"] = (
            results["brand_clean"].fillna("").astype(str).str.casefold().eq(formatted_brand)
            if formatted_brand else True
        )
        results["_popularity"] = results["rating"] * np.log1p(results["review_count"])
        results["_identity_key"] = [self.identity_keys[index] for index in results.index]
        results = (
            results.sort_values(
                ["_exact_name", "_exact_brand", "_popularity", "record_id"],
                ascending=[False, False, False, True],
                kind="mergesort",
            )
            .drop_duplicates("_identity_key", keep="first")
            .head(top_n)
        )
        return results[["record_id", "name", "Brand", "rating", "review_count", "brand_clean"]]

    def _resolve_query_index(
        self,
        perfume_name: str,
        brand: Optional[str],
        perfume_id: Optional[int],
    ) -> Optional[int]:
        if self.df is None:
            raise RuntimeError("Recommender has not been fitted")
        if perfume_id is not None:
            try:
                record_id = int(perfume_id)
            except (TypeError, ValueError):
                return None
            if 0 <= record_id < len(self.df):
                return record_id
            return None
        matches = self.search(perfume_name, brand=brand, top_n=1)
        return None if matches.empty else int(matches.iloc[0]["record_id"])

    def calculate_similarity(self, query_index: int) -> Dict[str, np.ndarray]:
        """Calculate all normalized similarity components and the final score."""

        if self.normalized_vectors is None:
            raise RuntimeError("Recommender has not been fitted")
        cosine = (self.normalized_vectors @ self.normalized_vectors.getrow(query_index).T).toarray().ravel()
        overlap = _weighted_jaccard(self.note_presence_matrix, self.note_weight_sums, query_index)
        pyramid = _weighted_jaccard(
            self.pyramid_presence_matrix, self.pyramid_weight_sums, query_index
        )
        accord = _weighted_jaccard(
            self.accord_presence_matrix, self.accord_weight_sums, query_index
        )
        weights = self.config.score_weights
        final = (
            weights["cosine"] * cosine
            + weights["overlap"] * overlap
            + weights["pyramid"] * pyramid
            + weights["accord"] * accord
        )
        # Do not cap a perfect note match below 1 when the query has no
        # optional accord metadata; redistribute only that unavailable weight.
        active_weight = 1.0
        if self.accord_weight_sums[query_index] == 0:
            active_weight -= weights["accord"]
        final = final / active_weight
        components = {"cosine": cosine, "overlap": overlap, "pyramid": pyramid,
                      "accord": accord, "final": final}
        for key, values in components.items():
            components[key] = np.clip(np.nan_to_num(values, nan=0.0, posinf=0.0, neginf=0.0), 0.0, 1.0)
        return components

    def get_common_notes(self, top_n: int = 20) -> List[Dict[str, object]]:
        """Return perfume-level note frequency for audit/evaluation output."""

        total = len(self.df) if self.df is not None else 0
        return [
            {"note": note, "perfume_count": count, "share": count / total if total else 0.0}
            for note, count in sorted(
                self.note_doc_frequency.items(), key=lambda item: (-item[1], item[0])
            )[:top_n]
        ]

    def rank_candidates(
        self,
        query_index: int,
        top_n: int = 5,
        same_tier: bool = False,
        min_reviews: Optional[int] = None,
    ) -> pd.DataFrame:
        """Apply explicit filters, remove duplicate identities, and rank descending."""

        if self.df is None:
            raise RuntimeError("Recommender has not been fitted")
        if min_reviews is None:
            min_reviews = self.config.default_min_reviews
        if min_reviews < 0:
            raise ValueError("min_reviews cannot be negative")

        scores = self.calculate_similarity(query_index)
        candidate_mask = self.vector_nonzero_mask & (scores["final"] > 0)
        query_identity = self.identity_keys[query_index]
        candidate_mask &= np.array(
            [identity != query_identity for identity in self.identity_keys], dtype=bool
        )
        candidate_mask &= self.df["review_count"].to_numpy() >= min_reviews

        query_tier = self.get_brand_tier(self.df.iloc[query_index]["brand_clean"])
        if same_tier and query_tier != "unknown":
            candidate_mask &= np.array(
                [self.get_brand_tier(brand) == query_tier for brand in self.df["brand_clean"]],
                dtype=bool,
            )

        indices = np.flatnonzero(candidate_mask)
        if not len(indices):
            return pd.DataFrame()
        results = self.df.iloc[indices].copy()
        results["cosine_similarity"] = scores["cosine"][indices]
        results["note_overlap_score"] = scores["overlap"][indices]
        results["pyramid_score"] = scores["pyramid"][indices]
        results["accord_similarity"] = scores["accord"][indices]
        results["final_score"] = scores["final"][indices]
        results["similarity"] = results["final_score"]
        results["brand_tier"] = results["brand_clean"].apply(self.get_brand_tier)
        results["_identity_key"] = [self.identity_keys[index] for index in indices]
        results = (
            results.sort_values(
                ["final_score", "cosine_similarity", "note_overlap_score",
                 "pyramid_score", "accord_similarity", "review_count", "record_id"],
                ascending=[False, False, False, False, False, False, True],
                kind="mergesort",
            )
            .drop_duplicates("_identity_key", keep="first")
            .head(top_n)
            .drop(columns=["_identity_key"])
        )
        return results

    @staticmethod
    def _all_notes(profile: Mapping[str, Sequence[str]]) -> set[str]:
        return {note for position in POSITION_NAMES for note in profile[position]}

    @staticmethod
    def _note_concepts(note: str) -> set[str]:
        concepts = set(_parent_concepts(note))
        if note in PARENT_NOTE_CONCEPTS:
            concepts.add(note)
        return concepts

    def explain_pair(self, query_index: int, candidate_index: int, row: pd.Series) -> Dict[str, object]:
        """Explain every score using normalized notes while leaving UI text unchanged."""

        query_profile = self.normalized_profiles[query_index]
        candidate_profile = self.normalized_profiles[candidate_index]
        query_accords = set(self.normalized_accords[query_index])
        candidate_accords = set(self.normalized_accords[candidate_index])
        query_notes = self._all_notes(query_profile)
        candidate_notes = self._all_notes(candidate_profile)
        shared = query_notes & candidate_notes

        related = set()
        for query_note in query_notes - shared:
            query_concepts = self._note_concepts(query_note)
            if not query_concepts:
                continue
            for candidate_note in candidate_notes - shared:
                common_concepts = query_concepts & self._note_concepts(candidate_note)
                for concept in common_concepts:
                    related.add(f"{query_note} ~ {candidate_note} ({concept})")

        same_position = {
            position: sorted(set(query_profile[position]) & set(candidate_profile[position]))
            for position in POSITION_NAMES
        }
        return {
            "perfume_id": int(candidate_index),
            "name": str(row["name"]),
            "brand": str(row["Brand"]),
            "cosine_similarity": float(row["cosine_similarity"]),
            "note_overlap_score": float(row["note_overlap_score"]),
            "pyramid_score": float(row["pyramid_score"]),
            "accord_similarity": float(row["accord_similarity"]),
            "final_score": float(row["final_score"]),
            "shared_notes": sorted(shared),
            "shared_note_percentage": 100.0 * len(shared) / len(query_notes) if query_notes else 0.0,
            "same_position_shared_notes": same_position,
            "shared_accords": sorted(query_accords & candidate_accords),
            "related_note_variants": sorted(related),
            "unique_query_notes": sorted(query_notes - shared),
            "unique_recommendation_notes": sorted(candidate_notes - shared),
        }

    def recommend(
        self,
        perfume_name: str,
        brand: Optional[str] = None,
        top_n: int = 5,
        same_tier: bool = False,
        min_reviews: Optional[int] = None,
        perfume_id: Optional[int] = None,
    ) -> Tuple[pd.DataFrame, dict]:
        """Return up to ``top_n`` genuinely similar, explainable perfumes."""

        if self.df is None:
            raise RuntimeError("Recommender has not been fitted")
        query_index = self._resolve_query_index(perfume_name, brand, perfume_id)
        if query_index is None:
            return pd.DataFrame(), {"error": f'Perfume "{perfume_name}" not found'}
        query_row = self.df.iloc[query_index]
        query_profile = self.normalized_profiles[query_index]
        query_notes = sorted(self._all_notes(query_profile))
        if not self.vector_nonzero_mask[query_index] or not query_notes:
            return pd.DataFrame(), {
                "error": f'Perfume "{query_row["name"]}" has no usable fragrance notes'
            }

        results = self.rank_candidates(
            query_index=query_index,
            top_n=top_n,
            same_tier=same_tier,
            min_reviews=min_reviews,
        )
        if results.empty:
            return pd.DataFrame(), {
                "error": "No note-overlapping candidates remain after the requested filters"
            }

        explanations = [
            self.explain_pair(query_index, int(candidate_index), row)
            for candidate_index, row in results.iterrows()
        ]
        score_weights = self.config.score_weights
        metadata = {
            "input_id": int(query_index),
            "input_name": str(query_row["name"]),
            "input_brand": str(query_row["Brand"]),
            "input_rating": float(query_row["rating"]),
            "input_reviews": int(query_row["review_count"]),
            "input_tier": self.get_brand_tier(query_row["brand_clean"]),
            "input_notes": query_notes,
            "input_note_pyramid": {
                position: list(query_profile[position]) for position in POSITION_NAMES
            },
            "recommendations_count": len(results),
            "avg_similarity": float(results["similarity"].mean()),
            "same_tier_filter": bool(same_tier),
            "min_reviews_filter": int(
                self.config.default_min_reviews if min_reviews is None else min_reviews
            ),
            "score_weights": score_weights,
            "position_weights": self.config.position_weights,
            "similarity_formula": (
                f'{score_weights["cosine"]:.2f} * cosine_similarity + '
                f'{score_weights["overlap"]:.2f} * idf_weighted_note_overlap + '
                f'{score_weights["pyramid"]:.2f} * same_position_pyramid_overlap + '
                f'{score_weights["accord"]:.2f} * main_accord_overlap'
            ),
            "explanations": explanations,
        }
        return results, metadata

    def get_similar_perfumes(self, *args, **kwargs) -> Tuple[pd.DataFrame, dict]:
        """Descriptive alias for ``recommend`` used by evaluation code."""

        return self.recommend(*args, **kwargs)

    def save(self, filepath: str | Path) -> None:
        """Atomically persist plain state without a fragile module-qualified class."""

        self._validate_index()
        target = Path(filepath)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(target.suffix + ".tmp")
        state = self.__dict__.copy()
        state.pop("config", None)
        artifact = {
            "format": "perfume-recommender-state",
            "model_version": MODEL_VERSION,
            "config": asdict(self.config),
            "state": state,
        }
        with temporary.open("wb") as handle:
            pickle.dump(artifact, handle, protocol=pickle.HIGHEST_PROTOCOL)
        temporary.replace(target)

    @staticmethod
    def load(filepath: str | Path) -> "PerfumeRecommender":
        """Load only a compatible, validated model cache."""

        try:
            with Path(filepath).open("rb") as handle:
                artifact = pickle.load(handle)
        except (ModuleNotFoundError, AttributeError, pickle.UnpicklingError) as error:
            raise ValueError("Cached model uses an incompatible serialization") from error
        if not isinstance(artifact, dict) or artifact.get("format") != "perfume-recommender-state":
            raise ValueError("Cached model uses an incompatible artifact format")
        if artifact.get("model_version") != MODEL_VERSION:
            raise ValueError("Cached recommendation model version is stale")
        try:
            model = PerfumeRecommender(RecommendationConfig(**artifact["config"]))
            model.__dict__.update(artifact["state"])
        except (KeyError, TypeError) as error:
            raise ValueError("Cached recommendation artifact is incomplete") from error
        model.model_version = MODEL_VERSION
        model._validate_index()
        return model

    def diagnostics(self) -> Dict[str, object]:
        """Return compact index/configuration facts for health checks and tests."""

        self._validate_index()
        return {
            "model_version": self.model_version,
            "perfume_count": len(self.df),
            "note_vocabulary_size": len(self.note_vocab),
            "feature_vocabulary_size": len(self.feature_vocab),
            "accord_vocabulary_size": len(self.accord_vocab),
            "vector_shape": list(self.perfume_vectors.shape),
            "vector_nonzero_values": int(self.perfume_vectors.nnz),
            "sparse_storage_bytes": int(
                self.perfume_vectors.data.nbytes
                + self.perfume_vectors.indices.nbytes
                + self.perfume_vectors.indptr.nbytes
            ),
            "config": asdict(self.config),
        }
