# ATHENA Step 3A — Paired finite PE-C2 marginals

Provenance: GitHub Actions run 37313083228, job 111773017481, commit da9f0ed5344196fd511f3db6052c0ece4b096347.
Domain: exact D=3,C=8 G_t signatures; C2 motifs exclude MUL. Denominator is all eligible operations represented in the signatures. Values are structural absorption fractions, not speedup/cycles.

| opt | transition | median marginal | Q1 | Q3 | positive benchmarks /19 | maximum |
|---|---|---:|---:|---:|---:|---:|
| O2 | 1->2 | 0.004549507267445661 | 0 | 0.07267601066624421 | 13 | 0.17535608051672458 |
| O2 | 2->3 | 0 | 0 | 0.017443939851045535 | 8 | 0.04822647168759089 |
| O2 | 3->4 | 0 | 0 | 0 | 1 | 0.008125858059145426 |
| O3 | 1->2 | 0.003396063532628641 | 0 | 0.0719547925271943 | 12 | 0.1312723579804811 |
| O3 | 2->3 | 0 | 0 | 0.015955370852766222 | 8 | 0.06563617899024055 |
| O3 | 3->4 | 0 | 0 | 0 | 1 | 0.0077686984288378655 |

Interpretation: a second C2 has positive marginal absorption in 13/19 O2 and 12/19 O3 benchmarks, with Q3 around 7.2 percentage points, although the median paired gain is small because many benchmarks saturate with one. A third C2 has zero median marginal and helps 8/19 benchmarks; a fourth helps only 1/19 and has Q3=0. Thus K=2 is the parsimonious structural candidate. K=3 is a sensitivity/upper candidate; K=4 is not supported as a default by this corpus.

Caveats: this is exact structural motif packing under D=3,C=8, not temporal execution, performance speedup, or a final array multiplicity. PE-C2 timing feasibility remains unresolved.
