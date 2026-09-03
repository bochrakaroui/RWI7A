# Recommendation pipeline audit

This document records the observed system and data problems before the recommendation architecture was changed.

## Existing end-to-end flow

1. `data/raw/fra_cleaned.csv` is read by `backend/preprocess.py` with a semicolon delimiter.
2. The preprocessor renames perfume and note columns, combines five `mainaccord` columns, converts ratings/review counts, and writes `data/processed/perfumes_processed.csv`.
3. At API startup, `backend/main.py` loads `data/processed/model.pkl`, or fits `PerfumeRecommender` on the processed CSV if the cache is absent.
4. The frontend searches `/search`, retains only perfume name/brand/rating/review count, and posts name plus brand to `/recommend`.
5. `recommend()` searches for the perfume again, takes the most popular substring match, reads the vector row using the DataFrame index, calculates cosine similarity against every dense vector, filters by brand tier and review count, blends scent similarity with popularity, and returns the top rows.
6. The API returns `similarity`; the frontend renders it as a percentage match.

## Data observations

- Processed shape: 24,063 rows and 20 columns.
- Relevant fields: `name`, `Brand`, `top_notes`, `middle_notes`, `base_notes`, five ranked main accords, rating, review count, and URL.
- The source distinguishes top, middle/heart, and base notes.
- No row has an empty top, middle, or base field in the current processed file.
- There are 1,671 distinct raw/lowercase note strings.
- There are 217 repeated `(name, Brand)` rows and five repeated name/brand/note profiles beyond the first occurrence.
- Some repeated names are not true duplicates. For example, the two `acqua-di-gio` records describe different gender/year/profile products. Name plus brand is therefore not a safe record identifier.
- Five note fields repeat a note within the same field.
- Case is already consistently lowercase, but spelling and concept variants remain separate. Examples include `cedarwood`/`cedar`, `virginian cedar`/`virginia cedar`, `tonka`/`tonka bean`, and `agarwood`/`agarwood (oud)`/`oud`.
- Specific ingredients such as `madagascar vanilla` and generic `vanilla` are separate. They should be related conservatively, not collapsed into the same display value.
- The comma splitter corrupts the rare note `arbutus (madrona, bearberry tree)` into two tokens because it does not respect parentheses.
- Multi-word notes such as `pink pepper` are otherwise kept as one manual-vocabulary feature; the system is not using a word tokenizer that splits them.

## Note frequency

The most common notes by perfume-level document frequency are:

| Note | Perfumes | Share |
| --- | ---: | ---: |
| musk | 10,951 | 45.51% |
| bergamot | 8,612 | 35.79% |
| sandalwood | 8,009 | 33.28% |
| amber | 7,686 | 31.94% |
| jasmine | 7,673 | 31.89% |
| patchouli | 7,208 | 29.95% |
| vanilla | 6,666 | 27.70% |
| rose | 6,134 | 25.49% |
| cedar | 5,582 | 23.20% |

IDF is appropriate for preventing these notes from dominating. The current implementation attempts IDF, but increments document frequency separately for each pyramid column. A perfume containing a note in more than one position is counted more than once, so the statistic is not perfume-level document frequency.

## Root causes in the existing recommender

1. **Wrong query record can be selected.** Recommendation lookup uses substring matching and popularity sorting. A request for Dior `sauvage` was observed to resolve to `sauvage-elixir`, changing the query profile before similarity was calculated.
2. **No stable search-to-recommend identifier.** The API sends only name and brand despite repeated name/brand pairs in the data.
3. **Commercial metadata changes scent ranking.** Brand-tier filtering is enabled by default and popularity contributes to the final score. Both conflict with note-primary cross-brand recommendations.
4. **Pyramid weights emphasize the opening.** The current defaults are top 3.0, middle 2.0, base 1.0, the reverse of the intended sustained-character prior.
5. **IDF is counted incorrectly.** A note can be counted up to three times per perfume.
6. **Repeated-position notes overwrite.** Vector assignment uses `=`; if a note occurs in several positions, the last position silently replaces earlier contributions.
7. **Normalization is too shallow.** Lowercasing and trimming do not reconcile safe aliases, punctuation, or spelling variants.
8. **Parenthetical commas are parsed incorrectly.** This creates features that are not fragrance notes.
9. **Whole-profile overlap is not measured.** Cosine alone is blended with popularity; there is no explicit reward for broad informative overlap or same-position agreement.
10. **Missing-note behavior is unsafe.** A zero vector can produce popularity-driven recommendations rather than a clear failure.
11. **Duplicate handling is incomplete.** Only the selected row index is excluded; same-identity duplicate records and repeated recommendation identities can remain.
12. **Index correctness is assumed.** Matrix row access uses DataFrame labels. It works only while the input retains the exact default RangeIndex.
13. **The matrix is unnecessarily dense.** Two dense 24,063 by 1,671 arrays are persisted, producing an approximately 651 MB model cache.
14. **The cache has no schema/model version check.** Code changes can load a stale pickled index with incompatible semantics.
15. **Debug output is insufficient.** It prints only nonzero dimension count, not shared/query-only/candidate-only notes or score components.

## Minimal replacement design

- Preserve original note text in the DataFrame and build separate normalized profiles.
- Parse delimiters outside parentheses, normalize Unicode/case/punctuation, and apply only conservative exact aliases.
- Keep specific variants distinct while adding low-weight parent concepts (for example, `madagascar vanilla` is still distinct but weakly related to `vanilla`).
- Fit one global sparse TF-IDF index. Compare pyramid weights empirically and keep them configurable.
- Compute perfume-level smoothed IDF exactly once from the complete corpus.
- Rank primarily with note-derived cosine, IDF-weighted whole-profile Jaccard, and same-position pyramid overlap; retain only a small empirically validated accord component.
- Default brand-tier and review filters off. Retain them only as explicit optional API filters for compatibility.
- Pass a stable row ID from search to recommendation and reset the fitted DataFrame index so vector row IDs are explicit and asserted.
- Exclude the query identity, discard invalid/zero-note candidates, and deduplicate returned identities.
- Cache sparse matrices with a model version marker and rebuild stale caches.
- Provide per-result explanations and standalone actual-dataset evaluation output.

## Empirical configuration result

A reproducible sample of 50 query perfumes (250 Top-5 pairs per configuration, seed `20260902`) compared full-query note coverage, same-position coverage, base-note retention, and main-accord Jaccard:

| Pyramid weights (top/heart/base) | Full coverage | Same-position | Base retention | Accord Jaccard |
| --- | ---: | ---: | ---: | ---: |
| Old 3/2/1 | 49.94% | 39.70% | 32.82% | 36.71% |
| Initial 1/1.5/2 | 52.04% | 40.87% | 55.07% | 37.47% |
| Selected 1/1.25/1.5 | **54.50%** | **41.53%** | 52.24% | **39.14%** |
| Strong base 1/1.5/2.5 | 51.07% | 40.61% | **60.72%** | 37.99% |

The selected weights gave the best whole-profile balance instead of maximizing base overlap alone. On the same 250 pairs, the note hybrid improved over cosine-only from 52.00% to 54.50% full coverage, 38.05% to 41.53% same-position coverage, and 48.18% to 52.24% base retention. Adding a 5% accord component modestly improved all four audit metrics, so it was retained while notes still account for 95% of the final score.
