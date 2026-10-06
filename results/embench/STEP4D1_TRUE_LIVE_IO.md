# Step 4D.1 — Definitive true live-in/live-out reconstruction

## Provenance
- Embench-IoT pinned revision: `09c2ed8c3b7008c95d08b038de4a3f6dc103ed70`.
- Definitive workflow run: `37453473962` (run #3).
- Head commit: `aa4b4ac6a56b9fba0558fb809c65380b6838784c`.
- Artifact: `athena-step4d1-refined`, ID `11409425657`.
- Digest: `sha256:a663559907933b4285e94355e34cc4677f83e052949bc50b245d9cb3f8a17de7`.
- Population: complete reconstructed G_t with D=3, C=8 under the definitive RV32I/M semantic classifier.

## Method
Architectural-register use/def semantics are decoded for all instruction forms observed in the 38 O2/O3 traces. Backward use-before-next-def liveness determines whether the last definition of an architectural register inside a G_t is a true future live-out. Live-ins are unique source registers consumed before a group-local definition. x0 is excluded.

The preceding unknown-opcode audit (run `37453221655`) identified 22 remaining opcodes/pseudoinstructions. Their semantics were added before this definitive run.

## Audit
`unknown_occurrences = 0`; `unknown_forms = 0`.

Thus every instruction form encountered in the analyzed traces has explicit use/def treatment.

## Benchmark-balanced CDFs
Values are medians of per-benchmark fractions, not pooled dynamic fractions.

| cap | O2 live-ins | O3 live-ins | O2 live-outs | O3 live-outs |
|---:|---:|---:|---:|---:|
|1|0.163888340|0.208089007|0.427094363|0.472945237|
|2|0.509603466|0.586105851|0.759005227|0.835967786|
|3|0.851099568|0.848581557|0.913407913|0.942230680|
|4|0.951088808|0.948734555|0.996827645|0.996538004|
|5|0.999636659|0.998591917|0.999864638|0.999911995|
|6|1.000000000|0.999985825|1.000000000|0.999997820|

## Interpretation
Four live-outs already cover about 99.65–99.68% of groups at the benchmark-balanced median. Live-ins show a stronger 4-to-5-port knee: about 94.87–95.11% at four and 99.86–99.96% at five. Step 4D.2 must evaluate the *joint* input/output feasibility rather than multiplying marginal CDFs.

## Limitations
This is architectural-register-level dynamic liveness reconstructed from sequential traces. It is a structural interface requirement, not a physical-register/rename timing model, cycle schedule, IPC, or speedup measurement.

## Decision
Step 4D.1 is complete. Step 4D.2 sizes the interface using joint live-in/live-out distributions from this definitive artifact.
