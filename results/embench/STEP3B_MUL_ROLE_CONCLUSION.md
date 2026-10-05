# ATHENA Step 3B — MUL structural-role conclusion

Provenance: GitHub Actions run 37320271678, job 111797269628, commit 397ad2ff5921840166a5568e50b3a2535baa6ea6. D=3,C=8 exact-signature input. Structural evidence only; not speedup/cycle measurement.

Occurrence-weighted role among MUL operations:
| opt | isolated | source | sink | internal |
|---|---:|---:|---:|---:|
| O2 | 0.1606804749 | 0.5090269251 | 0.1886803206 | 0.1416122795 |
| O3 | 0.2046541035 | 0.5550248315 | 0.2194439974 | 0.0208770676 |

Benchmark-balanced role distributions (zeros include benchmarks with no role; only 11/19 benchmarks contain MUL):
- O2 isolated: median 0, Q1 0, Q3 0.1432072994, positive 6/19
- O2 source: median 0, Q1 0, Q3 0.0792458032, positive 6/19
- O2 sink: median 0, Q1 0, Q3 0.0328922032, positive 9/19
- O2 internal: median 0, Q1 0, Q3 0, positive 3/19
- O3 isolated: median 0, Q1 0, Q3 0.3045936080, positive 7/19
- O3 source: median 0, Q1 0, Q3 0.4106266335, positive 7/19
- O3 sink: median 0, Q1 0, Q3 0.0360761923, positive 8/19
- O3 internal: median 0, Q1 0, Q3 0, positive 2/19

Combined with prior Step 3B evidence:
- median MUL share of eligible operations: 0.8355% O2, 1.0155% O3; 11/19 benchmarks use MUL.
- occurrence-weighted P(G_t contains >=2 MUL): 1.2064% O2, 1.8389% O3.
- intended multiplier temporal model is pipelined L_MUL≈6-8 cycles, II_MUL=1 (project-owner design assumption pending RTL validation).

Architectural inference:
1. Broad replication of MUL inside general ALU/C2 PEs is not supported.
2. MUL is most often a producer/source in dynamic occurrence-weighted evidence (50.9% O2, 55.5% O3), so routing its delayed result efficiently to ordinary PEs is more important than embedding MUL into a one-cycle compound PE.
3. Internal-chain MUL is limited, especially O3 (2.09% weighted; positive in 2/19 benchmarks), arguing against a dedicated compound MUL-chain PE.
4. With II=1, structural co-occurrence of multiple independent MULs does not by itself require multiple physical multipliers. A single specialized/shared pipelined multiplier is the principal candidate; two multipliers remain a temporal-performance sensitivity point rather than the default structural choice.
5. Consumers of MUL results must respect L_MUL; no MUL-containing structural motif is evidence for same-cycle execution.

Step 3B conclusion: structurally recommend one specialized/shared pipelined MUL resource as the baseline hypothesis, connected so its outputs can feed ordinary ALU/C2 resources after latency. Final multiplicity remains subject to later temporal scheduling/performance evaluation and eventual synthesis of the supplied Verilog multiplier.
