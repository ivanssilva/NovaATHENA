# ATHENA Experimental Register

This file is the persistent decision/evidence register for the NovaATHENA evaluation.
Conversation text is explanatory context; accepted experimental claims must be traceable
to repository code, a GitHub Actions run/artifact, and an entry in this register.

## Registration levels

1. **Implementation** — scripts and workflows, identified by commit SHA.
2. **Evidence** — GitHub Actions run, logs, CSV/artifacts, and explicit invariants.
3. **Decision** — accepted/rejected interpretation, with reason and scope.

A run being green is not sufficient by itself for scientific acceptance.

## Step 5B — C2 temporal model

### Scientific question

Separate the cycle-count effect of increasing the scheduling capacity from four to
eight positions from the additional effect of up to two C2 producer-consumer
same-cycle fusions.

Models:

- H4: four-position structural reference.
- W8: eight-position reference without C2 fusion.
- C2: eight positions plus at most two producer-consumer C2 fusions per cycle.

Primary invariant:

    C_C2 <= C_W8 <= C_H4

The ratios H4/C2 and W8/C2 are structural-temporal cycle-count ratios. They are
**not physical speedup** until clock-period/frequency effects are incorporated.

### Rejected/diagnostic run 37613097807

Head SHA: 1d20e34cad03570c35f5546b0640f3d7704e377f
Artifact: athena-step5b-c2-corrected (artifact 11478802073)

The corpus completed and produced 38 paired traces, satisfying the ordering
invariant and reporting 9,794,944 fusions. However, this run is **not accepted as
definitive evidence** because one analytical microcase failed while the workflow
continued.

Failed check:

    three_chains_pair_limit: observed cycles=2, fusions=2;
    original expected cycles=2, fusions=3.

Root cause of the apparent microcase failure: the expected fusion count was
over-constrained. With three independent producer-consumer chains and only two
C2 pairs, all three producers are ready at cycle start. Two producer-consumer
pairs may fuse in cycle 1, while the third producer may execute normally in that
same cycle. Its consumer is then ready in cycle 2. Therefore the minimum remains
two cycles and only two same-cycle fusions are required by this scheduling policy.
Fusion count is policy-dependent diagnostic information; cycle count is the
primary metric.

A separate workflow defect was also found: piping Python through `tee` without
`set -o pipefail` hid the nonzero Python exit status.

The numerical corpus output from this run is retained for diagnosis but must not
be cited as the final Step 5B result.

### Corrections

- 15d198d3ccafdd303310b13ad113b92e3bdacfde
  Corrects the analytical expectation for the three-chain/two-C2 case to
  cycles=2, fusions=2 and documents the scheduling rationale.
- 641412a0a3c56031ab0989bd0fce2ab1b8546268
  Adds `set -o pipefail` to validation and corpus pipelines so validation
  failures stop the job.

### Acceptance criteria for the definitive Step 5B run

The run is accepted only if all of the following hold:

1. all eight analytical C2 microcases pass;
2. corpus execution occurs only after validation succeeds;
3. exactly 38 Embench traces are processed (19 benchmarks x O2/O3);
4. C_C2 <= C_W8 <= C_H4 holds for every trace;
5. C2 total fusion count is nonzero;
6. O2 and O3 summary records are emitted;
7. logs and CSV are preserved as a GitHub Actions artifact;
8. the accepted run ID, head SHA, artifact ID/digest, aggregate results, and
   interpretation are recorded here.

### Accepted definitive run

Primary run: **37628255296** (workflow run #6, event `issues`)  
Head SHA: **e49e4fa6d4ba7604dcd798d3b8927c13bc93f882**  
Job: **112815528197**, conclusion: **success**  
Artifact: **athena-step5b-c2-corrected**, artifact **11484823579**  
Artifact digest: **sha256:4bf21fd309bcd3aad8799fbb8a697c28296ae92ecdeaa3b5e02640f5d7a5c80c**

Independent redundant run #5 (push), run **37628236226**, also completed successfully
from the same head SHA and produced the same aggregate results.

Validation: all 8 analytical C2 microcases passed, including
`three_chains_pair_limit = cycles 2, fusions 2`.

Corpus audit:

    STEP5B_C2_AUDIT traces 38 pairs 38 invariant_c2_le_w8_le_h4 yes total_fusions 9794944

Aggregate cycle-count ratios:

- O2 H4/C2: median 1.200063515; Q1 1.082523223; Q3 1.432253688; aggregate 1.290409192.
- O2 W8/C2: median 1.139083536; Q1 1.079635779; Q3 1.346312341; aggregate 1.241703037.
- O3 H4/C2: median 1.254122611; Q1 1.116009178; Q3 1.432285315; aggregate 1.348669304.
- O3 W8/C2: median 1.138149045; Q1 1.116007543; Q3 1.356116272; aggregate 1.295018880.

Interpretation: under the corrected optimistic same-cycle C2 model, widening from
H4 to W8 contributes part of the cycle-count reduction, while C2 provides a
substantial additional reduction on this corpus. Relative to W8, the aggregate
cycle-count gain from C2 is about 1.242x for O2 and 1.295x for O3. Relative to H4,
the complete H4-to-C2 structural-temporal gain is about 1.290x for O2 and 1.349x
for O3. These values remain structural-temporal cycle-count bounds, not physical
speedups; clock-period/frequency effects must be evaluated separately.

### Status

**ACCEPTED — Step 5B definitive corrected result.**
