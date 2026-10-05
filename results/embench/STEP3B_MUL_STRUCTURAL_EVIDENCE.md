# ATHENA Step 3B — MUL structural evidence

Provenance: GitHub Actions run 37316675774, job 111785045283, commit 3c6e5722803c663c64e6ce02ead8cc2e440615bf. Validated exact-signature input from run 37145305760. Artifact 11347344286, digest sha256:fd7aff3c2817bd2d77014de62034c2ce08ad2a87589d4eb065d981c6df38ec0b.

Domain: D=3,C=8 candidate G_t signatures. Results below are structural statistics, not cycle/performance measurements.

Benchmark-balanced results (19 benchmarks per optimization):
| opt | metric | median | Q1 | Q3 | benchmarks > 0 |
|---|---|---:|---:|---:|---:|
| O2 | MUL / eligible ops | 0.0083550415 | 0 | 0.0599824989 | 11/19 |
| O2 | G_t containing MUL | 0.0172947847 | 0 | 0.1371057626 | 11/19 |
| O3 | MUL / eligible ops | 0.0101554665 | 0 | 0.0608234374 | 11/19 |
| O3 | G_t containing MUL | 0.0172874991 | 0 | 0.1401945123 | 11/19 |

Occurrence-weighted G_t MUL multiplicity:
| opt | P(MUL>=1) | P(MUL>=2) | P(MUL>=3) |
|---|---:|---:|---:|
| O2 | 0.1285982040 | 0.0120643937 | 0.0062109901 |
| O3 | 0.1243008700 | 0.0183885430 | 0.0115424895 |

Interpretation:
- Typical benchmark MUL fraction is about 0.84% (O2) and 1.02% (O3); Q1=0 and only 11/19 benchmarks contain MUL, so demand is strongly benchmark-dependent.
- Although occurrence-weighted P(G_t has >=1 MUL) is ~12.4-12.9%, simultaneous demand for >=2 MUL is only ~1.2% O2 and ~1.8% O3 of G_t occurrences; >=3 is still smaller.
- These data do not support replicating multipliers broadly across general PEs.
- Current parsimonious hypothesis is a small specialized/shared multi-cycle MUL resource, initially one instance, with sensitivity to two instances. This is not yet a final choice because temporal overlap depends on latency and initiation interval.
- User-supplied design expectation: a Radix-4 Booth/Wallace multiplier is intended to complete in roughly 6-8 cycles. Treat this as a design assumption/range to validate, not as a measured result. Therefore MUL-containing structural chains must not be interpreted as one-cycle compound PEs.
- The current script generated per-benchmark structural roles (isolated/source/sink/internal) in the artifact CSV, but those role aggregates were not printed to the job log. They should be summarized in a follow-up analysis before Step 3B is declared complete.

Limitations: D and C are structural extraction parameters; these statistics do not include temporal occupancy, memory/control effects, multiplier II, configuration overhead, or speedup.
