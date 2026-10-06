# ATHENA — Structural Derivation Closure and Temporal Evaluation Plan

## Structural reference architecture (closed for temporal evaluation)
Evidence chain:
traces -> G_t(D=3,C=8) -> PE evidence -> sparse topology -> true live I/O -> joint structural validation.

Reference candidate:
- 4 PE-ALU
- 2 PE-C2
- 5 selective links (K5)
- 5 live inputs / 4 live outputs
- 1 shared pipelined multiplier
- MUL design assumption: latency 6--8 cycles, initiation interval 1; latency sensitivity is mandatory until RTL timing/latency is fixed.
- 6-in/4-out retained as interface sensitivity.
- DIV/DIVU/REM/REMU: semantics known for dependence/liveness, but unsupported by current ATHENA and region barriers.

This closes structural derivation; changes to these parameters after this point are sensitivity experiments or a new architecture revision, not silent retuning.

## Next scientific stage: temporal performance model

### Goal
Estimate execution time/cycles of ATHENA and a 4-wide OoO superscalar baseline under explicit, reproducible assumptions. Only this stage may support a speedup claim.

### Step 5A — temporal-model contract and trace requirements
Before computing performance, define and audit the event model shared by both sides.

Required dynamic information:
1. dynamic instruction sequence and PC;
2. operation class and architectural source/destination registers;
3. true RAW producer identity;
4. control-flow/branch boundaries and squash information where available;
5. memory operations and addresses where available;
6. candidate ATHENA region identity/configuration-cache key;
7. mapping of region operations to PE/slot and live-in/live-out interface demand.

The current reconstructed traces are sufficient for structural RAW analysis but must be audited for PC, memory-address and control-event fidelity before they are used as a cycle-performance trace.

### 4-wide OoO baseline contract
The simulator must explicitly parameterize:
- fetch/decode/rename/dispatch width;
- issue width = 4;
- commit width;
- ROB and RS capacities;
- integer FU counts and latencies;
- pipelined MUL latency/II;
- DIV/REM latency if present in the host;
- load/store resources and latency;
- branch prediction/penalty model;
- cache/memory latency model.

No baseline number is to be inferred from structural G_t coverage.

### ATHENA temporal contract
Model:
- region discovery/availability;
- configuration-cache hit/miss and configuration overhead;
- live-in acquisition;
- PE scheduling respecting K5 links;
- PE-C2 combinational feasibility under a declared target period;
- shared MUL with L=6,7,8 sensitivity and II=1;
- live-out publication/writeback;
- branch/squash invalidation;
- memory operations remaining on host unless an explicit ATHENA memory interface is introduced.

### Step 5B — idealized compute-only temporal bound
After 5A audit, first run an intentionally idealized model:
- perfect configuration availability;
- no memory stalls;
- no branch misprediction;
- same target clock assumption stated explicitly;
- compare 4-wide host issue constraints against ATHENA region scheduling.
This gives an upper compute-only temporal bound, not final application speedup.

### Step 5C — progressively realistic temporal model
Add, in controlled layers:
1. MUL latency;
2. control boundaries/squashes;
3. configuration cache/discovery overhead;
4. memory/cache effects;
5. frequency/critical-path effect.

Report each layer separately so the source of gain/loss is explainable.

### Step 5D — final benchmark comparison
Per benchmark and O2/O3 report:
- host cycles;
- ATHENA cycles;
- IPC/operations per cycle where meaningful;
- execution-time ratio including clock period;
- geometric mean only if the aggregation choice is explicitly justified;
- median/dispersion and sensitivity to MUL latency, interface 5/4 vs 6/4, and key host parameters.

## Reproducibility rule
Every temporal result must preserve source trace revision, simulator commit, parameter file, raw per-benchmark output, aggregate output, audit, interpretation, and limitations.

## Immediate action
Execute Step 5A first: audit the definitive Embench traces for the fields needed by the temporal model. Do not invent unavailable memory/control information. The audit decides which temporal layers can be measured directly and which require explicit modeled assumptions or trace regeneration.
