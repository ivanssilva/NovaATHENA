# NovaATHENA — four array topology experiments

This repository contains **combinational, first-pass** Verilog implementations of 4+4, PE6, 4+4-1F and PE6-1F using the same 32-bit integer ALU. The 1F variants support one convergent 2-producer destination.

## Remote run

The GitHub Actions workflow `.github/workflows/nangate45.yml` runs Yosys synthesis against the **Nangate45 Liberty** from the official OpenROAD-flow-scripts repository. Download its `athena-nangate45-synthesis` artifact for mapped Verilog, full Yosys logs and `summary.csv`.

**Scope:** cell-mapped *combinational* synthesis, not full OpenROAD placement/routing. No clock, latches, operand staging, config cache, ROB, generator, physical wire parasitics, STA or measured leakage. The summary reports estimated mapped cell area from Liberty cell footprints only. Timing/leakage and a fair registered interface will be added in the next milestone.

**Architectural limitations:** 4+4 forwards only into the first operand of each C2 ALU; the 1F unit adds a second forwarded operand. PE6 has six hardwired local A→B paths; PE6-1F adds one B input selectable from the other A outputs. Noncommutative operand placement and 4-wide host bandwidth require separate architectural validation. A PE6 B cannot be independently scheduled, despite unused input ports in the wrapper.

Do not treat preliminary gate-equivalent estimates as measured silicon area or leakage.
