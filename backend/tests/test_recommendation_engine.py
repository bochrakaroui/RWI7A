import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import issparse

from backend.recommendation_engine import (
    PerfumeRecommender,
    RecommendationConfig,
    normalize_note,
    parse_notes,
)


def synthetic_perfumes() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"name": "perfume-a", "Brand": "brand-a", "top_notes": "bergamot",
             "middle_notes": "lavender", "base_notes": "vanilla, cedar",
             "rating": 1.0, "review_count": 0},
            {"name": "perfume-b", "Brand": "brand-b", "top_notes": "bergamot",
             "middle_notes": "lavender", "base_notes": "vanilla, cedar",
             "rating": 1.0, "review_count": 0},
            {"name": "perfume-b", "Brand": "brand-b", "top_notes": "bergamot",
             "middle_notes": "lavender", "base_notes": "vanilla, cedar",
             "rating": 5.0, "review_count": 10000},
            {"name": "perfume-c", "Brand": "brand-c", "top_notes": "bergamot",
             "middle_notes": "", "base_notes": "vanilla",
             "rating": 1.0, "review_count": 0},
            {"name": "perfume-d", "Brand": "brand-d", "top_notes": "rose",
             "middle_notes": "tuberose", "base_notes": "jasmine",
             "rating": 5.0, "review_count": 10000},
            {"name": "perfume-e", "Brand": "brand-e", "top_notes": "leather",
             "middle_notes": "smoke", "base_notes": "tobacco",
             "rating": 5.0, "review_count": 10000},
            {"name": "perfume-f", "Brand": "brand-f", "top_notes": "vanilla, cedar",
             "middle_notes": "lavender", "base_notes": "bergamot",
             "rating": 5.0, "review_count": 10000},
        ],
        index=[10, 20, 30, 40, 50, 60, 70],
    )


class RecommendationEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model = PerfumeRecommender().fit(synthetic_perfumes())

    def test_logical_ranking_and_invariants(self) -> None:
        results, metadata = self.model.recommend("perfume-a", perfume_id=0, top_n=5)
        names = results["name"].tolist()

        self.assertEqual(names[0], "perfume-b")
        self.assertLess(names.index("perfume-c"), len(names))
        self.assertNotIn("perfume-a", names)
        self.assertEqual(names.count("perfume-b"), 1)
        self.assertNotIn("perfume-d", names)
        self.assertNotIn("perfume-e", names)
        self.assertLessEqual(len(results), 5)
        self.assertTrue(np.all(np.diff(results["similarity"].to_numpy()) <= 0))
        self.assertAlmostEqual(results.iloc[0]["similarity"], 1.0, places=6)
        self.assertEqual(metadata["input_id"], 0)

    def test_popularity_does_not_change_scent_score(self) -> None:
        results, _ = self.model.recommend("perfume-a", perfume_id=0, top_n=5)
        identical = results[results["name"] == "perfume-b"].iloc[0]
        unrelated_names = {"perfume-d", "perfume-e"}
        self.assertAlmostEqual(identical["similarity"], 1.0, places=6)
        self.assertTrue(unrelated_names.isdisjoint(results["name"]))

    def test_same_pyramid_beats_reversed_pyramid(self) -> None:
        scores = self.model.calculate_similarity(0)
        self.assertGreater(scores["pyramid"][1], scores["pyramid"][6])
        self.assertGreater(scores["final"][1], scores["final"][6])

    def test_exact_name_is_not_retargeted_to_popular_substring(self) -> None:
        df = pd.DataFrame([
            {"name": "sauvage", "Brand": "dior", "top_notes": "bergamot",
             "middle_notes": "pepper", "base_notes": "ambroxan", "rating": 1, "review_count": 1},
            {"name": "sauvage-elixir", "Brand": "dior", "top_notes": "cinnamon",
             "middle_notes": "lavender", "base_notes": "licorice", "rating": 5, "review_count": 99999},
            {"name": "bergamot-peer", "Brand": "other", "top_notes": "bergamot",
             "middle_notes": "pepper", "base_notes": "ambroxan", "rating": 1, "review_count": 0},
        ])
        model = PerfumeRecommender().fit(df)
        search = model.search("sauvage", "dior")
        self.assertEqual(search.iloc[0]["name"], "sauvage")
        _, metadata = model.recommend("sauvage", "dior", top_n=1)
        self.assertEqual(metadata["input_name"], "sauvage")

    def test_record_ids_align_after_non_default_input_index(self) -> None:
        self.assertTrue(np.array_equal(self.model.df["record_id"], np.arange(len(self.model.df))))
        self.assertEqual(self.model.df.iloc[3]["source_index"], 40)
        self.assertEqual(self.model.perfume_vectors.shape[0], len(self.model.df))
        self.assertTrue(issparse(self.model.perfume_vectors))

    def test_multiword_notes_and_parenthetical_commas_are_preserved(self) -> None:
        self.assertEqual(parse_notes("pink pepper, cedar"), ["pink pepper", "cedar"])
        self.assertEqual(
            parse_notes("arbutus (madrona, bearberry tree), musk"),
            ["arbutus madrona bearberry tree", "musk"],
        )
        self.assertIn("pink pepper", PerfumeRecommender().fit(pd.DataFrame([
            {"name": "x", "Brand": "x", "top_notes": "pink pepper",
             "middle_notes": "iris", "base_notes": "musk"}
        ])).note_vocab)

    def test_conservative_aliases(self) -> None:
        self.assertEqual(normalize_note("Cedarwood"), "cedar")
        self.assertEqual(normalize_note("Virginian Cedar"), "virginia cedar")
        self.assertEqual(normalize_note("Agarwood (Oud)"), "oud")
        self.assertEqual(normalize_note("Madagascar Vanilla"), "madagascar vanilla")

    def test_common_notes_have_lower_idf(self) -> None:
        self.assertLess(self.model.idf_values["bergamot"], self.model.idf_values["tobacco"])

    def test_accord_is_only_a_small_tiebreaker(self) -> None:
        df = pd.DataFrame([
            {"name": "query", "Brand": "a", "top_notes": "bergamot",
             "middle_notes": "iris", "base_notes": "vanilla", "main_accords": "floral"},
            {"name": "same-accord", "Brand": "b", "top_notes": "bergamot",
             "middle_notes": "iris", "base_notes": "vanilla", "main_accords": "floral"},
            {"name": "other-accord", "Brand": "c", "top_notes": "bergamot",
             "middle_notes": "iris", "base_notes": "vanilla", "main_accords": "woody"},
        ])
        model = PerfumeRecommender().fit(df)
        results, _ = model.recommend("query", perfume_id=0, top_n=2)
        self.assertEqual(results["name"].tolist(), ["same-accord", "other-accord"])
        self.assertAlmostEqual(results.iloc[1]["similarity"], 0.95, places=6)

    def test_configuration_and_persistence(self) -> None:
        config = RecommendationConfig()
        self.assertLess(config.top_weight, config.middle_weight)
        self.assertLess(config.middle_weight, config.base_weight)
        self.assertAlmostEqual(sum(config.score_weights.values()), 1.0)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.pkl"
            self.model.save(path)
            loaded = PerfumeRecommender.load(path)
            self.assertEqual(loaded.diagnostics()["vector_shape"], self.model.diagnostics()["vector_shape"])


if __name__ == "__main__":
    unittest.main()
