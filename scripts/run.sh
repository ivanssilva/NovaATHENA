#!/usr/bin/env bash
set -euo pipefail
mkdir -p reports
LIB="$PWD/orfs/flow/platforms/nangate45/lib/NangateOpenCellLibrary_typical.lib"
for TOP in athena_4x4 athena_pe6 athena_4x4_1f athena_pe6_1f; do
  echo "=== $TOP ==="
  yosys -Q -T -l "reports/$TOP.log" -p "read_verilog rtl/athena_alu32.v rtl/$TOP.v; hierarchy -check -top $TOP; synth -top $TOP -flatten; dfflibmap -liberty $LIB; abc -liberty $LIB; clean; stat -liberty $LIB; write_verilog -noattr reports/$TOP.mapped.v"
done
python3 scripts/extract.py "$LIB"
