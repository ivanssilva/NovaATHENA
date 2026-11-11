# Handover — NovaATHENA E7, 2026-11-11

## Scientific objective
V4 IEEE Portuguese paper on *limits of utilization* of transparent CGRA coupled to OoO4 host. Avoid claims of measured speedup or measured OoO events from committed architectural traces. Issue #21 is the editorial/experimental contract.

## Frozen input and prior results
38 Embench RV32IM traces (19 O2 + 19 O3), artifact `athena-embench-structural` from Actions run 36850448602. Census run 43031044033 SUCCESS: 121,418,629 dynamic instructions, 57 distinct opcode mnemonics, artifact `novaathena-e7-1-opcode-census` (opcodes.csv, operand_shapes.csv, manifest).
E1–E6 prior results retained. E2 retrospective RAW was methodologically flawed because it tracked eligible ALU writers only, ignoring intervening ineligible writers. E7.1 must correct this, with no fabricated OoO rename/ROB observations.

## E7.1 status
`scripts/e7_1_raw_dependency_audit.py` decodes all inventoried mnemonic classes and reconstructs RAW from every register writer; records cross-BB counts, 38 per-trace hashes, summary. **Two internal tracking maps use the same decoder**: equality is a consistency check, NOT independent validation of true OoO rename or precision/recall. Tests include store-base alias, jalr 3-operand, seqz, neg, CSR, branch aliases. Memory-base normalization fixed in commit 9a7130e7. Standalone `--self-test` added in ab44e61e.
Previous E7.1 runs #22–#25 failed on unsupported instructions; issue #27 run 43033362110 failed *before processing traces* on a directed `sw zero,0(t0)` alias assertion. That bug has since been fixed.
Standalone preflight workflow `.github/workflows/e7-1-preflight.yml` was created, but its initial push run 43036976317 failed with zero jobs (workflow configuration issue); issue #28 did not launch its job. **Do not rely on this standalone workflow.**
The known-working E7.1 full workflow `.github/workflows/e7-1-raw-dependencies.yml` was just updated in commit c36cb38cd07bf03ed1f0bdde6d730739815d44b6 to run `python3 scripts/e7_1_raw_dependency_audit.py --self-test` **before downloading traces**, then full processing. Trigger by creating issue with exact title `[RUN] NovaATHENA E7.1`. Inspect logs and artifacts before claiming scientific success. E7.1 COMPLETED SUCCESSFULLY: run 43041784105, 38/38 traces, 121,418,629 dynamic instructions; artifact `novaathena-e7-1` contains per_trace.csv, manifest.json, log, commit and run ID. Counts cover all register RAW edges, not solely eligible CGRA candidate edges; E2 comparison requires aligned definitions. E7.2 pilot requested in issue #31, synthetic only.

## Nangate45 synthesis
Runs 43036543149 and 43036952315 FAILED during apt installation of Yosys, due to `Temporary failure resolving azure.archive.ubuntu.com`. No RTL synthesis or area results from these runs. This is independent of E7.1. Consider an environment with preinstalled Yosys or network retry, without altering scientific RTL.

## V4 plan and stop rules
E7.1: one successful 38-trace full-writer RAW pass, documented limits and E2 comparison, then close; avoid endless refinement. E7.2: speculative learning vs commit-only, safe publication, branch squash/ROB wrap microcases, incorrect publication must be zero, but do not claim measured OoO speculation without actual event traces. E7.3 finite LearnQ/ControlQ capacity and backpressure; E7.4 only if genuine temporal events available. Retain manifest, code SHA, run ID, trace hashes, failures, caveats. Prefer minimizing campaign scope and user burden.

## Key links
- E7 protocol: https://github.com/ivanssilva/NovaATHENA/issues/21
- Opcode census success: https://github.com/ivanssilva/NovaATHENA/actions/runs/43031044033
- E7.1 last full failed run: https://github.com/ivanssilva/NovaATHENA/actions/runs/43033362110
- Standalone preflight issue: https://github.com/ivanssilva/NovaATHENA/issues/28
- Nangate45 failure: https://github.com/ivanssilva/NovaATHENA/actions/runs/43036952315

## Next concrete actions
1. Retrieve E7.1 artifact from successful run 43041784105, consolidate full-writer RAW and cross-BB counts; compare to E2 only with aligned denominator.
2. Inspect E7.2 synthetic publication pilot issue #31 and its workflow results; six directed cases, safe publication vs deliberately unsafe control. These are functional microcases, not measured OoO execution.
3. Audit availability of real dispatch/rename/commit/resolve/squash event traces before extending E7.2 to real-event measurement.
4. Proceed to E7.3 only after E7.2 limitations are explicitly documented.
