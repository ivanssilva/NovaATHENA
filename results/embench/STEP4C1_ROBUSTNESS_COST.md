# ATHENA Step 4C.1 — Sparse-topology robustness and cost audit

## Provenance
Run 37348884328; job 111894403760; head 3520b7c81acde9e605353988514c004e5aac0089.
Artifact 11361427357; SHA256 7b19aac72d66f55a278e75d94842624c36bcc87071801cdb221392beb439efdf.
Audit: 38 benchmark/optimization pairs, 955 signatures, 48 slot relabelings.

## Prefix cost results
Cost tuple = (added directed links, max added fan-in, max added fan-out, mux-input proxy).
1: C1B->C0B, gain 9,488,575, score 54,008,036, cost (1,1,1,0)
2: +C1A->A3, gain 2,171,294, score 56,179,330, cost (2,1,1,0)
3: +A2->C1B, gain 1,873,559, score 58,052,889, cost (3,1,1,0)
4: +A1->C0A, gain 2,273,170, score 60,326,059, cost (4,1,1,0)
5: +A0->A1, gain 952,528, score 61,278,587, cost (5,1,1,0)
6: +A3->A1, gain 541,726, score 61,820,313, cost (6,2,1,1)
7: +A1->C0B, gain 184,604, score 62,004,917, cost (7,2,2,2)
8: +A3->C0A, gain 177,221, score 62,182,138, cost (8,2,2,3)

All 48 relabelings preserve the cost tuple at each prefix. Unique labeled forms grow to 48 by prefix 4, confirming that literal slot names are not architectural evidence.

## Interpretation
The strongest cost knee is at five added links: prefixes 1-5 maintain max added fan-in=1, max added fan-out=1 and mux-input proxy=0 under this network-only proxy. The sixth link is the first to create destination fan-in 2 and a positive mux-input penalty. Combined with Step 4C benchmark-balanced coverage (O2 Q1 99.54%, O3 Q1 99.86% at five links), five added links is the current parsimonious sparse-connectivity candidate.

This does not freeze the literal endpoint labels. Relabeling demonstrates symmetry of cost, not uniqueness or global optimality. Alternative non-isomorphic equal/better-score networks were not exhaustively searched. Also, the mux proxy excludes ordinary external operand selection, local C2 input muxing, placement/routing and timing.

## Decision gate
Before physical synthesis, perform a small constrained alternative-topology search around K=4,5,6 that optimizes structural score with explicit fan-in/fan-out penalty and deduplicates isomorphic solutions. If K=5 remains on the Pareto frontier, synthesize canonical K=4/5/6 finalists in Nangate45.
