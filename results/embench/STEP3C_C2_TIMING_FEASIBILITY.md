# Step 3C — PE-C2 temporal feasibility

## Purpose

This substep tests whether the structurally motivated two-operation PE-C2 (local configurable A -> B chain) is technologically plausible as one combinational block. It does **not** by itself establish a processor clock period, cycle-level speedup, or post-route timing.

## Provenance

- Repository: `ivanssilva/NovaATHENA`
- Definitive measured run: GitHub Actions run `37330687285`, run number 13
- Head commit: `b87bf60a1882603531611108c1c40ddfae9163d8`
- Workflow: `.github/workflows/step3c-timing.yml`
- RTL under test: `rtl/athena_alu32.v`, `rtl/step3c_pe.v`
- Measurement script: `scripts/step3c_timing.sh`
- Standard-cell library: `NangateOpenCellLibrary_typical.lib`, obtained from OpenROAD-flow-scripts Nangate45 platform by the workflow
- Logic synthesis/mapping: Yosys/ABC as installed on the Ubuntu 24.04 GitHub runner
- Static timing analysis: OpenSTA 3.1.0, source SHA `d1e43c6f9f`
- Required OpenSTA dependency: CUDD 3.0.0
- Artifact: `11354352512`, `athena-step3c-pe-timing`
- Artifact digest: `sha256:a2247376ad6376d6de925f34b9666670acb9d013fde43f1c027ff973426fa8f9`

## Method

Both PE variants were flattened, synthesized and technology-mapped against the same Nangate45 typical Liberty library.

- `athena_pe_alu`: one configurable 32-bit ATHENA ALU.
- `athena_pe_c2`: two configurable 32-bit ATHENA ALUs in a local A -> B chain, with the local output bypass present in the Step 3C RTL.

Because these are combinational blocks, OpenSTA directly reports the maximum unconstrained input-to-output path:

`report_checks -unconstrained -from [all_inputs] -to [all_outputs] -path_delay max`

No artificial sequential clock constraint is used in this intrinsic local-PE comparison.

Mapped area is taken from Yosys `stat -liberty`. Timing is taken from OpenSTA.

## Results

| Structure | Mapped cell area | Max combinational path | Critical path endpoints |
|---|---:|---:|---|
| PE-ALU | 1286.110 | 1.3127 ns | `b[3] -> y[31]` |
| PE-C2 | 2561.846 | 1.9491 ns | `op0[0] -> y1[31]` |

Derived ratios:

- Timing ratio: `T_C2/T_ALU = 1.9491/1.3127 = 1.4848` (approximately 1.485).
- Area ratio: `A_C2/A_ALU = 2561.846/1286.110 = 1.9919` (approximately 1.992).

Thus the mapped PE-C2 has about 48.5% more intrinsic combinational delay and about 1.99x the mapped cell area of PE-ALU.

For reference only, twice the independently mapped PE-ALU delay is 2.6254 ns; the jointly synthesized C2 delay is 1.9491 ns. This comparison indicates that the mapped compound block must not be modeled simply as `2*T_ALU`.

## Interpretation

The result upgrades PE-C2 from a purely structural depth-2 motif to a technology-mapped local compound-PE candidate. Under the tested RTL/library/mapping conditions, the A -> B compound path is 1.9491 ns.

This result does **not** establish that PE-C2 executes two operations in one cycle for every ATHENA implementation. That statement requires an explicit ATHENA target clock period and, ultimately, implementation-level timing. Intrinsically, the tested local PE-C2 would fit a period no shorter than 1.9491 ns before accounting for additional architectural routing, placement/parasitics, margins, and other system constraints.

## Limitations

1. These are technology-mapped logical delays, not placed-and-routed delays.
2. Inter-PE topology/routing and its parasitics are not included.
3. The Step 3C PE-C2 represents local A -> B connectivity and local bypass; it is not a full final-array routing network.
4. No processor/ATHENA target period is declared by this experiment.
5. The Nangate45 typical-library result is a comparative technology point, not a silicon sign-off result.
6. Area is mapped standard-cell area from Yosys/Liberty, not physical core area.
7. This experiment does not measure IPC, cycles, benchmark performance, or speedup.

## Step 3C decision

The intrinsic local temporal-feasibility test supports retaining PE-C2 in the candidate heterogeneous PE set. Its final one-cycle use remains conditional on the target period and later physical/topology timing.

Combined with the preceding Step 3 evidence, the parsimonious architecture hypothesis carried forward is:

`{ PE-ALU, 2 x PE-C2, 1 x shared pipelined MUL }`

where the two PE-C2 instances are the current structurally supported compound-resource multiplicity candidate (with three retained as a sensitivity point), and the multiplier remains a specialized shared pipelined resource with the user-supplied design assumption `L_MUL = 6-8 cycles`, `II_MUL = 1` until its RTL is synthesized and temporally validated.

Dedicated PE-J is not retained as an independent PE class because its paired marginal structural absorption after C2 is very small. Convergence may still be revisited as selective routing/augmentation.

## Step 3 status

**Step 3 is complete at the PE-type derivation level.** The selected set is provisional with respect to later topology, physical timing, array-wide capacity, and temporal performance modeling. No structural metric in Step 3 is interpreted as speedup.
