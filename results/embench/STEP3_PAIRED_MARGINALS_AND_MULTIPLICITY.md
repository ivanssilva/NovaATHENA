# ATHENA Step 3 — Paired marginals and motif multiplicity

Evidence source: GitHub Actions run 37209887034, job 111458734950, commit 9e271a4cd101db695a6048fc8b0a9bc0203c39c1.
Input: validated exact G_t signatures, D=3, C=8.

## Paired marginal absorption

| opt | marginal | median | Q1 | Q3 | benchmarks positive |
|---|---|---:|---:|---:|---:|
| O2 | J given C2 | 0.001983698771668006 | 0.0 | 0.005721711470576826 | 12/19 |
| O2 | C2 given J | 0.17417277629077932 | 0.0602317885849295 | 0.2655857829304277 | 19/19 |
| O3 | J given C2 | 0.0011992003607939016 | 0.0 | 0.007512792282987547 | 11/19 |
| O3 | C2 given J | 0.1979610398679641 | 0.10943587767244904 | 0.31589623428614094 | 18/19 |

These are paired benchmark-level structural absorption marginals, not speedup, IPC, cycle reduction, or complete hardware coverage.

## Simultaneous motif multiplicity

| opt | motif | mean packed motifs/G_t | P(N>=2) | P(N>=3) |
|---|---|---:|---:|---:|
| O2 | C2 | 0.3812348751273055 | 0.07711158877818865 | 0.017955165934984158 |
| O2 | J | 0.05706208422620518 | 0.0027142682707445315 | 0.0 |
| O2 | C2+J | 0.3812348751273055 | 0.07711158877818865 | 0.017955165934984158 |
| O3 | C2 | 0.42478200123194865 | 0.06948218971955718 | 0.01994807107028061 |
| O3 | J | 0.06055364140261487 | 0.00374618787225901 | 0.0 |
| O3 | C2+J | 0.42478200123194865 | 0.06948218971955718 | 0.01994807107028061 |

Caution: the joint C2+J motif-count decomposition is affected by the optimizer tie-breaking and must not be interpreted as a unique architectural multiplicity. C2-only and J-only multiplicities, and operation absorption marginals, are the defensible outputs.

## Current structural inference

PE-C2 is strongly supported as a composite PE candidate. A dedicated PE-J is not supported as an independent PE class by the paired marginal evidence. This remains a structural inference: one-cycle feasibility of PE-C2 requires timing synthesis, and final array composition requires finite-multiplicity analysis.
