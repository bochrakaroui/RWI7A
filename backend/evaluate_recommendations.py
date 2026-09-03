"""Manual actual-dataset evaluation for the perfume recommender.

Run from the repository root:
    .venv/Scripts/python.exe backend/evaluate_recommendations.py
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Iterable, Tuple

import numpy as np
import pandas as pd

try:
    from .recommendation_engine import PerfumeRecommender
except ImportError:
    from recommendation_engine import PerfumeRecommender


ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = ROOT / "data" / "processed" / "perfumes_processed.csv"
MODEL_PATH = ROOT / "data" / "processed" / "model_v2.pkl"
DEFAULT_QUERIES = (
    ("dior", "sauvage"),
    ("yves-saint-laurent", "black-opium"),
    ("chanel", "chanel-no-5-eau-de-parfum"),
    ("lancome", "la-vie-est-belle"),
    ("creed", "aventus"),
    ("guerlain", "shalimar-eau-de-parfum"),
)


def load_or_build_model(rebuild: bool = False) -> PerfumeRecommender:
    if not rebuild:
        try:
            return PerfumeRecommender.load(MODEL_PATH)
        except (FileNotFoundError, ValueError, AttributeError, EOFError):
            pass
    model = PerfumeRecommender().fit(pd.read_csv(DATASET_PATH))
    model.save(MODEL_PATH)
    return model


def parse_query_specs(specs: Iterable[str]) -> Tuple[Tuple[str | None, str], ...]:
    parsed = []
    for spec in specs:
        if ":" in spec:
            brand, name = spec.split(":", 1)
            parsed.append((brand or None, name))
        else:
            parsed.append((None, spec))
    return tuple(parsed)


def assert_recommendation_invariants(
    model: PerfumeRecommender,
    query_id: int,
    results: pd.DataFrame,
    top_n: int,
) -> None:
    assert len(results) <= top_n
    assert query_id not in set(results["record_id"].astype(int))
    identities = [model.identity_keys[index] for index in results["record_id"].astype(int)]
    assert len(identities) == len(set(identities))
    scores = results["similarity"].to_numpy(dtype=float)
    assert np.isfinite(scores).all()
    assert ((0 <= scores) & (scores <= 1)).all()
    assert np.all(np.diff(scores) <= 1e-12)
    assert np.array_equal(
        results["record_id"].astype(int).to_numpy(),
        results.index.astype(int).to_numpy(),
    )


def evaluate_query(
    model: PerfumeRecommender,
    brand: str | None,
    name: str,
    top_n: int,
) -> None:
    matches = model.search(name, brand=brand, top_n=1)
    if matches.empty:
        print(f"\nNOT FOUND: {brand or '*'} / {name}")
        return
    query_id = int(matches.iloc[0]["record_id"])
    results, metadata = model.recommend(
        name,
        brand=brand,
        perfume_id=query_id,
        top_n=top_n,
        same_tier=False,
        min_reviews=0,
    )
    if "error" in metadata:
        print(f"\nERROR: {metadata['error']}")
        return

    assert_recommendation_invariants(model, query_id, results, top_n)
    print("\n" + "=" * 88)
    print(f"QUERY: {metadata['input_name']} | {metadata['input_brand']} | id={query_id}")
    for position, notes in metadata["input_note_pyramid"].items():
        print(f"  {position:6}: {', '.join(notes)}")
    print(f"FORMULA: {metadata['similarity_formula']}")

    for rank, explanation in enumerate(metadata["explanations"], start=1):
        print(
            f"{rank}. {explanation['name']} | {explanation['brand']} | "
            f"score={explanation['final_score']:.4f} "
            f"cos={explanation['cosine_similarity']:.4f} "
            f"overlap={explanation['note_overlap_score']:.4f} "
            f"pyramid={explanation['pyramid_score']:.4f} "
            f"accord={explanation['accord_similarity']:.4f} "
            f"query-note-coverage={explanation['shared_note_percentage']:.1f}%"
        )
        print(f"   shared: {', '.join(explanation['shared_notes']) or '(related variants only)'}")
        related = explanation["related_note_variants"]
        if related:
            print(f"   related variants: {', '.join(related)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("queries", nargs="*", help="Perfume names or brand:name pairs")
    parser.add_argument("--top-n", type=int, default=5)
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.top_n <= 20:
        parser.error("--top-n must be between 1 and 20")

    model = load_or_build_model(rebuild=args.rebuild)
    diagnostics = model.diagnostics()
    print("INDEX:", diagnostics)
    print("\nMOST COMMON NORMALIZED NOTES")
    for item in model.get_common_notes(20):
        print(
            f"  {item['note']:<24} {item['perfume_count']:>6} perfumes "
            f"({item['share']:.2%})"
        )

    query_specs = parse_query_specs(args.queries) if args.queries else DEFAULT_QUERIES
    for brand, name in query_specs:
        evaluate_query(model, brand, name, args.top_n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
