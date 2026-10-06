# ATHENA — Step 4D.2 Definitive Interface Sizing

## Status
COMPLETE — definitive rerun after separating known ISA semantics from ATHENA eligibility.

## Provenance
- Repository: ivanssilva/NovaATHENA
- Definitive Step 4D.1 source run: 37481863207
- Step 4D.1 head: ca466502c643edc3b235606e3595eba20da02bde
- Step 4D.2 run: 37492067105
- Step 4D.2 head: bd447b341e6b72fafd3f9aa4440b4f399d793fff
- Job: 112367068878
- Artifact: athena-step4d2-interface
- Artifact ID: 11426475150
- Digest: sha256:20ca71ba23701faa3d19d7337c7f9bd23372a44dba8fdc54b85cea5925af4284
- Audit: 38 benchmark/optimization pairs; 1271 aggregate rows.
- Population: definitive G_t(D=3,C=8); DIV/DIVU/REM/REMU have known use/def semantics but are ATHENA-ineligible and delimit regions.

## Metric
Joint structural feasibility:
P(N_live-in <= N_in AND N_live-out <= N_out).
Also operation-weighted fraction inside G_t. Values below are benchmark-balanced medians and Q1, not pooled fractions and not performance/speedup.

## Definitive results
| Opt | Interface | group median | group Q1 | op median | op Q1 |
|---|---|---:|---:|---:|---:|
| O2 | 4-in/4-out | 0.948189703 | 0.477364592 | 0.855280234 | 0.249989433 |
| O2 | 5-in/4-out | 0.996827843 | 0.880862348 | 0.991024817 | 0.744619605 |
| O2 | 6-in/4-out | 0.996827843 | 0.883091151 | 0.991024817 | 0.748917619 |
| O2 | 5-in/5-out | 0.999601037 | 0.907441457 | 0.998876814 | 0.778812486 |
| O3 | 4-in/4-out | 0.945699616 | 0.469874805 | 0.850695327 | 0.229592156 |
| O3 | 5-in/4-out | 0.984648128 | 0.706936381 | 0.953725307 | 0.493363872 |
| O3 | 6-in/4-out | 0.996538239 | 0.874744215 | 0.990243957 | 0.693091575 |
| O3 | 5-in/5-out | 0.998503912 | 0.715577824 | 0.997028233 | 0.532092966 |

## Architectural decision
Base interface candidate: **5 live inputs / 4 live outputs**.
Sensitivity variant: **6 live inputs / 4 live outputs**, because O3 dispersion shows a meaningful sixth-input effect.
A fifth output is not justified as the base interface by the observed marginal benefit.

## Scientific interpretation and limitations
The fifth input is substantially more valuable than the fifth output. The 5-in/4-out point is the parsimonious base, while 6-in/4-out is retained for sensitivity. These are structural interface-coverage measurements only. They do not include cycles, frequency, memory, configuration/cache overhead, branch/squash behavior, physical routing, or temporal MUL scheduling, and must not be called speedup.
