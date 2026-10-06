# ATHENA — Step 4D.3 Joint Structural Capacity

## Status
COMPLETE — joint validation of the current heterogeneous-array candidate.

## Provenance
- Repository: ivanssilva/NovaATHENA
- Script: scripts/step4d3_joint_capacity.py
- Trigger head: d011792cdb28bc35db57df03a102876788f59f36
- Run: 37493155282
- Job: 112370798532
- Artifact: athena-step4d3-joint-capacity
- Artifact ID: 11427532268
- Digest: sha256:823e37a26d73d86cd23885bde343a48667c9c559327aed24edb524c339cb263b
- Audit: 38 traces, 38 benchmark/optimization pairs, unknown_occurrences=0, unknown_forms=0, 956 backbone signatures.
- Population: definitive G_t(D=3,C=8); DIV/DIVU/REM/REMU are known liveness barriers and ATHENA-ineligible.

## Architecture tested
Current structural reference candidate:
- 4 PE-ALU
- 2 PE-C2 (two local ALUs A->B with bypass)
- 5 selective links (K5 sparse topology)
- base interface 5-in/4-out
- sensitivity 6-in/4-out
- one shared pipelined MUL is part of the architectural hypothesis, but MUL temporal realization is deliberately not claimed by this structural test (assumption L_MUL=6--8 cycles, II=1).

The K5 logical representative used is one Pareto-equivalent endpoint labeling from Step 4C.2. Endpoint labels are not physical-layout evidence.

## Definitive joint results
For MUL-free G_t, `nomul_exact` imposes the K5 topology and interface jointly.

| Opt | Interface | G_t median | G_t Q1 | op median | op Q1 |
|---|---|---:|---:|---:|---:|
| O2 | 5-in/4-out | 0.986980793 | 0.909882593 | 0.963128970 | 0.823070197 |
| O2 | 6-in/4-out | 0.986980793 | 0.909882593 | 0.963128970 | 0.823070197 |
| O3 | 5-in/4-out | 0.999791279 | 0.753117724 | 0.999400400 | 0.389929490 |
| O3 | 6-in/4-out | 0.999853505 | 0.753117724 | 0.999466031 | 0.389929490 |

For all G_t, `all_backbone` removes MUL nodes and evaluates the remaining backbone. It is an upper structural indicator pending temporal MUL scheduling, not full-array realizability.

| Opt | Interface | backbone G_t median | backbone G_t Q1 | backbone op median | backbone op Q1 |
|---|---|---:|---:|---:|---:|
| O2 | 5-in/4-out | 0.987216157 | 0.852063191 | 0.963745088 | 0.666573298 |
| O2 | 6-in/4-out | 0.987216157 | 0.856660097 | 0.963745088 | 0.675417288 |
| O3 | 5-in/4-out | 0.984648128 | 0.576512863 | 0.953999122 | 0.335433688 |
| O3 | 6-in/4-out | 0.999853505 | 0.839839586 | 0.999466031 | 0.654909290 |

Median fraction of G_t containing MUL: O2=0.017294785; O3=0.017287499.

## Decision
The structural derivation is closed with the current reference hypothesis:

**4 PE-ALU + 2 PE-C2 + 5 selective links + 5-in/4-out + 1 shared pipelined MUL**

with **6-in/4-out retained as sensitivity** and no DIV/REM hardware in current ATHENA.

The high benchmark-balanced medians support this sparse heterogeneous structure, but Q1 values show important benchmark heterogeneity. Article claims must report dispersion and must not summarize the result simply as “~99% coverage”.

## Boundary of this evidence
This is structural realizability, not temporal execution and not speedup. It excludes clock/frequency effects, memory, configuration discovery/cache behavior, branch/squash effects, physical routing, and the temporal scheduling of MUL. Those belong to the next temporal-performance stage.
