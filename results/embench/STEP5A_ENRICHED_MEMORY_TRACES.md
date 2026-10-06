# Definitive enriched memory traces — Step 5A closure

Date: 2026-10-06

## Provenance
Embench commit: 09c2ed8c3b7008c95d08b038de4a3f6dc103ed70. Immutable structural traces: run 36850448602. Enrichment workflow: .github/workflows/embench-memory-trace.yml; code: plugins/memtrace.c and scripts/merge_memory_trace.py. Definitive run: 37529136813; head 1233ccf7e540429547ac8e906e787903099462a2; job 112493693348.

## Method
The same pinned Embench source is rebuilt for RV32IM in the controlled bare-metal runtime. The QEMU plugin records R/W, virtual effective address, physical address when available, size and I/O classification. Events are correlated to the immutable structural trace by dynamic PC occurrence order and retain the original sequence identity.

## Definitive audit
38 traces. Each has exactly one missing structural memory operation and zero extras. In all 38 cases the missing operation is PC 0x8000003c, `sw t1,0(t0)`, explicitly classified as `terminal_harness_store`.

Aggregate: 29,294,677 structural memory operations; 38 excluded terminal stores; 29,294,639 captured effective accesses; 19,969,641 reads; 9,324,998 writes; sizes: 4 B=15,827,981, 2 B=2,460,199, 1 B=11,006,459; I/O-marked=38.

Artifact: ID 11443229130, `athena-embench-memory-traces`, 170,019,090 bytes, sha256:d280e692a16e1d45aa50ce9cd089779bba4025f387fbd060f6f3e6384ad76095, expiry 2027-01-04.

## Interpretation and limitations
The effective-address gap identified by Step 5A is closed, enabling later reproducible cache/memory modeling. I/O-marked accesses must not automatically be treated as cacheable. These are architectural dynamic traces, not measured OoO events: rename tags, ROB/RS occupancy, speculative squash events, issue/commit timestamps and cache outcomes are absent and require an explicit temporal model. Branch next-PC remains reconstructable from the dynamic sequence.

## Status
Step 5A trace enrichment is CLOSED and validated. It does not alter structural evidence from Steps 1–4.
