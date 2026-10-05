#!/usr/bin/env bash
set -euo pipefail
mkdir -p reports/step3c
LIB="$PWD/orfs/flow/platforms/nangate45/lib/NangateOpenCellLibrary_typical.lib"
for TOP in athena_pe_alu athena_pe_c2; do
  yosys -Q -T -l "reports/step3c/$TOP.log" -p "read_verilog rtl/athena_alu32.v rtl/step3c_pe.v; hierarchy -check -top $TOP; synth -top $TOP -flatten; dfflibmap -liberty $LIB; abc -liberty $LIB; clean; stat -liberty $LIB; write_verilog -noattr reports/step3c/$TOP.mapped.v"
done
# Use OpenSTA if available to measure combinational input-to-output critical delay.
sudo apt-get update -qq
sudo apt-get install -y opensta
python3 - <<'PY'
from pathlib import Path
for top in ('athena_pe_alu','athena_pe_c2'):
    p=Path(f'reports/step3c/{top}.sdc')
    p.write_text('set_input_delay 0 [all_inputs]\nset_output_delay 0 [all_outputs]\n')
PY
for TOP in athena_pe_alu athena_pe_c2; do
cat > "reports/step3c/$TOP.tcl" <<EOF
read_liberty $LIB
read_verilog reports/step3c/$TOP.mapped.v
link_design $TOP
read_sdc reports/step3c/$TOP.sdc
report_checks -path_delay max -digits 4
report_design_area
EOF
  sta "reports/step3c/$TOP.tcl" | tee "reports/step3c/$TOP.sta.txt"
done
