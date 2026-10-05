# ATHENA Step 4B — Topology-family structural mapping

## Provenance
- Workflow run: 37343972366
- Job: 111877791028
- Head SHA: fcf43fbc1649e31e3e92e1b0352f4da382ee43da
- Source exact-signature artifact: run 37145305760, artifact 11282509918, SHA256 47d51909ffc17246af9edd2de7bdbf5ab24bc6f2d2536d809cc22f75c2d4af6a
- Step 4B artifact: 11360010816
- Step 4B artifact SHA256: a563d30456964e1a81d7fe41201d06dbfb5f77143d7ea567afaf6d6c2f035431
- Slice: D=3, C=8, K_C2=2; 38 benchmark/optimization pairs.

## Structural capability classes
T0: local PE-C2 edges only.
T1: T0 plus residual non-join producer-consumer chain edges.
T2: T1 plus all residual non-MUL join edges.
T3: unrestricted internal non-MUL DAG upper bound.

These are nested structural capability classes, not yet concrete physical networks.

## Results
O2 non-MUL edges: 6,717,684; local C2 4,348,486; residual chain 1,555,749; residual join 813,449. MUL-temporal edges: 1,707,021.
Benchmark-balanced edge-realizability fractions:
- T0 median 0.6475873753; Q1 0.6000004596; Q3 0.8264753231
- T1 median 0.9797570850; Q1 0.7753827926; Q3 1.0
- T2 median/Q1/Q3 1.0
- T3 median/Q1/Q3 1.0

O3 non-MUL edges: 6,858,696; local C2 4,597,919; residual chain 1,482,569; residual join 778,208. MUL-temporal edges: 1,417,970.
Benchmark-balanced:
- T0 median 0.6453918540; Q1 0.5998835178; Q3 0.8328136441
- T1 median 0.9748310118; Q1 0.8750462217; Q3 1.0
- T2 median/Q1/Q3 1.0
- T3 median/Q1/Q3 1.0

## Interpretation and limitation
Two local C2 resources absorb about two-thirds of non-MUL dependency edges in the median benchmark. Adding generic residual chain capability raises the median structural edge realizability to about 97.5–98%. The remaining class is join/convergence communication.

T2 reaching 1.0 is partly definitional: T2 grants all residual join edges. Therefore this result does NOT prove that a particular selective physical cross-link network realizes all joins, nor that T2 has the same cost/timing as T3. Step 4B identifies which communication classes matter; it does not yet select endpoints, mux sizes, placement, routing, cycles, IPC, or speedup.

Next required experiment: map exact G_t graphs to concrete PE slots and search/minimize the physical endpoint/link set, measuring marginal structural coverage versus link/mux complexity.
