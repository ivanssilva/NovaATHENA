# Step 4A — topology evidence and identifiability audit

Status: initiated; this substep defines and audits the evidence required before selecting array width or inter-PE wiring. No topology is selected here.

## Frozen input evidence

- Embench-IoT pinned source revision: `09c2ed8c3b7008c95d08b038de4a3f6dc103ed70`.
- 38 dynamic traces, 19 benchmarks, O2/O3; 121,418,557 total trace rows. Raw traces are retained as workflow artifacts rather than committed to Git history.
- D3,C8 exact per-benchmark signatures in `gt_capacity_benchmark_signature_counts.csv` from validated run `37145305760`, artifact `11282509918`.
- The existing signature `[(op, internal_predecessor_indices), ...]` is adequate for identifying internal RAW edges, forks, joins, and potential inter-PE edges in each candidate Gt.
- Step 3: PE-ALU, two PE-C2 as parsimonious compound-resource hypothesis (three as sensitivity), one shared pipelined MUL (user-supplied L=6–8, II=1).
- Step 3C local Nangate45 mapped evidence: ALU 1.3127 ns, 1286.110 mapped cell area; C2 1.9491 ns, 2561.846 mapped cell area; run `37330687285`, artifact `11354352512`.

## Identifiability finding (first result)

The current exact-signature aggregate retains **internal graph topology and op classes**, but not the register identity of each external input, true future live-outs, cycle timestamps, or the actual dispatch/ROB ready-time context. The `external_inputs` descriptor is only a count; `unconsumed_defs` is local to Gt and is not global liveness. Consequently, this aggregate can support an initial *internal edge-demand* comparison between topology candidates, but cannot by itself establish port counts, exact external mux costs, complete topology, or real throughput.

A defensible topology study must distinguish:
1. local A -> B edges absorbed inside C2;
2. residual producer -> consumer edges crossing PE boundaries;
3. external source and true live-output routing (requires enriched trace extraction or conservative explicit bounds);
4. delayed MUL-result routes, which are not same-cycle ALU edges.

## Step 4A extraction specification

For each distinct D3,C8 signature and each benchmark/optimization occurrence count:
- reconstruct the exact DAG and identify all internal RAW edges;
- enumerate non-overlapping placements of up to K=2 C2 motifs, with K=3 sensitivity, and remaining non-MUL nodes as simple ALU operations;
- exclude MUL from same-cycle C2 placement and represent its outputs as delayed routing demands;
- preserve multiple equally optimal C2 packings when they have different residual edge demands (do not let arbitrary optimizer tie-breaking select topology);
- report residual edges by type: producer/consumer PE type, fanout, convergence, and longest inter-PE dependency chain;
- compare abstract connection classes: no cross-PE edge, selective cross-links, row/column-neighbor links, and unrestricted connectivity as a structural upper bound;
- aggregate occurrence-weighted and benchmark-balanced results separately for O2 and O3;
- retain per-benchmark raw counts and paired topology marginal results, not only global averages.

## Explicit controls

Do not infer PE-ALU count or final topology from C=8 (a candidate-group sensitivity cap). Do not count Gt motif occurrences as actual execution cycles. Do not call structural edge satisfaction, packing, or absorption 'speedup'. Final link selection needs mux area and path-delay synthesis under the same library, plus true external-port/live-out evidence.

## Immediate execution gate

First compute an auditable edge-demand census and alternative optimal C2 packings from exact signatures. Then decide whether existing data suffice for initial topology comparisons or whether trace enrichment is mandatory before committing a concrete wiring scheme.

Scientific chain: pinned trace source -> extraction version -> exact signatures and benchmark occurrence counts -> packing algorithm -> residual edge evidence -> candidate topology -> same-flow area/timing -> later temporal performance model.
