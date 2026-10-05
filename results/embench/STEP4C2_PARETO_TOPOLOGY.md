# Step 4C.2 — Optimized constrained Pareto topology search

## Provenance
- Workflow run: 37362978553
- Job: 111941720407
- Head SHA: 15a944203d6a3e9d6e2cdbcaf6a1081d01d24282
- Artifact: athena-step4c2-optimized (ID 11367518337)
- Artifact digest: sha256:3abf389c3304d9592dce40347a76c148f9920519b289eb7b8500494ee97c3e7b
- Input exact-signature corpus: D=3,C=8, 38 benchmark/optimization pairs, 955 signatures.
- Search: constrained beam search, beam=160, canonicalized under 48 slot relabelings.

## Results
Best retained structural mapped-operation-weight scores:
- K=4: 60,326,059; max added fan-in=1, max added fan-out=1, mux proxy=0.
- K=5: 61,392,292; max added fan-in=1, max added fan-out=1, mux proxy=0. Two Pareto representatives tie.
- K=6: 61,901,125; max added fan-in=2, max added fan-out=1, mux proxy=1.

Marginal K4->K5 = 1,066,233 (+1.767% relative to K4).
Marginal K5->K6 = 508,833 (+0.829% relative to K5).

Canonical K=5 representatives:
1. A0->A1, A1->C0B, A2->C1B, C1A->C0A, C1B->A3
2. A0->C0A, A1->C0B, A2->C1B, C1A->A1, C1B->A3

## Interpretation
K=5 is the current parsimonious sparse-connectivity candidate. It improves structural mapped-operation weight over K=4 without increasing the added-link fan-in/fan-out maxima or mux proxy. K=6 provides a smaller marginal gain and is the first retained Pareto point to incur max added fan-in 2 and mux proxy 1.

The literal endpoint labels are NOT a physical-design conclusion. The K=5 representatives are canonical members of structural equivalence/competition classes under slot relabeling. The architectural evidence supports approximately five selective directed links more strongly than it supports any specific labeled endpoint assignment.

## Limitations
This is constrained beam search, not a proof of global optimality. The score is structural mapped-operation weight, not cycles, IPC, or speedup. External operands, true live-outs, placement/routing, physical wire delay, physical mux cost, area, leakage, and temporal scheduling are excluded.

## Next experiment
Implement canonical K4/K5/K6 structural finalists in the same Nangate45/Yosys/OpenSTA flow used for Step 3C. Measure mapped cell area and unconstrained combinational input-to-output critical delay. Keep the shared pipelined MUL outside the same-cycle combinational topology comparison.
