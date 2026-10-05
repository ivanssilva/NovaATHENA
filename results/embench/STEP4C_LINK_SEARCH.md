# ATHENA Step 4C — Concrete slot/link structural search

## Provenance
Run 37345940777; job 111884385365; head f577bbb562f2b9138fa735f84371bbe238fd54ce.
Artifact 11360082896; SHA256 4944bc452f928f5a6206d7d3219c14dd9f5e2ef8190d1dc46450e4ec8a68bd8b.
Source exact-signature artifact: run 37145305760. Slice D=3,C=8. Audit: 38 benchmark/optimization pairs, 955 signatures.
Candidate slots: A0-A3 plus C0A/C0B and C1A/C1B; fixed local links C0A->C0B and C1A->C1B. MUL excluded from same-cycle graph.

## Greedy directed-link sequence and weighted gains
Base weighted mapped operation count: 44,519,461.
1 C1B->C0B +9,488,575
2 C1A->A3 +2,171,294
3 A2->C1B +1,873,559
4 A1->C0A +2,273,170
5 A0->A1 +952,528
6 A3->A1 +541,726
7 A1->C0B +184,604
8 A3->C0A +177,221
9 C1A->A2 +126,032
10 C1A->C0A +58,525
11 A1->A2 +34,752
12 A0->C0B +4,520
13 C1B->C1A +0; search saturated under this greedy model.

## Benchmark-balanced mapped-operation-weight fraction
O2 median: base .85222; +1 .98182; +2 .98760; +3 .99843; +4 .999965; +7 1.0.
O3 median: base .85163; +1 .96537; +2 .99656; +3 1.0; +4 1.0.
Q1 remains important: O2 base .60566, +1 .83223, +2 .84203, +3 .89455, +4 .94148, +5 .99543, +7 .999974, +9 1.0. O3 base .58620, +1 .82307, +2 .85804, +3 .89249, +4 .99499, +5 .99862, +7 .999998, +8 1.0.

## Interpretation
The candidate capacity (4 simple ALUs + 2 C2) exhibits rapid structural saturation with a small number of directed links. One added link yields the largest marginal gain. Roughly 3-4 links are enough to make median structural mapped-operation weight essentially complete; 5-8 links are needed to make the lower quartile essentially complete. This argues against a full crossbar as a default.

However, the exact named links are NOT yet physical-design conclusions. Slot labels are symmetric/arbitrary and greedy selection can break symmetry. The metric is weighted structural embeddability, not cycle scheduling. External operand identities, true future live-outs, mux input cost, fanout, routing, timing, and configuration/control cost are excluded. Therefore Step 4C supports the sparsity level of connectivity more strongly than it supports the literal endpoint names.

## Required next check
Before freezing topology, test robustness of the sparse-link conclusion against slot relabeling/alternative equal-gain solutions and explicit mux/fan-in cost, then synthesize the selected sparse topology variants for timing/area.
