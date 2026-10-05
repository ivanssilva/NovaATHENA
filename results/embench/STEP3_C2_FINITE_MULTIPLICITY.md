# ATHENA Step 3 — Finite PE-C2 multiplicity

Evidence source: GitHub Actions run 37311443302, job 111767571530, commit 80cba940e6c8d524dd3101586bcc2a8bc7536984.
Input: exact G_t signatures, D=3,C=8. Metric: maximum fraction of eligible operations structurally absorbable into non-overlapping C2 motifs with at most K simultaneous C2 motifs per G_t. This is not speedup or cycle reduction.

| opt | K | median | Q1 | Q3 |
|---|---:|---:|---:|---:|
| O2 | 1 | 0.1757310776329485 | 0.0602317885849295 | 0.3141779504565365 |
| O2 | 2 | 0.20594102897304026 | 0.0602317885849295 | 0.41929648396550706 |
| O2 | 3 | 0.20594102897304026 | 0.0602317885849295 | 0.42844936396016275 |
| O2 | 4 | 0.20594102897304026 | 0.0602317885849295 | 0.42844936396016275 |
| O3 | 1 | 0.17273335797367798 | 0.08070110497532536 | 0.34151211884477584 |
| O3 | 2 | 0.2538380062752056 | 0.10943587767244904 | 0.42847941950601565 |
| O3 | 3 | 0.2697933771279718 | 0.10943587767244904 | 0.42847941950601565 |
| O3 | 4 | 0.2697933771279718 | 0.10943587767244904 | 0.42847941950601565 |

Interpretation: K=2 reaches the O2 median saturation and captures most O3 median opportunity; K=3 adds O3 median absorption, while K=4 adds no median gain over K=3. Differences of medians are descriptive only; a final multiplicity choice should also use benchmark-paired K-to-K marginal distributions before being stated as definitive.
