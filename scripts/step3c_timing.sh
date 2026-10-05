#!/usr/bin/env bash
set -euo pipefail
mkdir -p reports/step3c
LIB="$PWD/orfs/flow/platforms/nangate45/lib/NangateOpenCellLibrary_typical.lib"
for TOP in athena_pe_alu athena_pe_c2; do
  yosys -Q -T -l "reports/step3c/$TOP.log" -p "read_verilog rtl/athena_alu32.v rtl/step3c_pe.v; hierarchy -check -top $TOP; synth -top $TOP -flatten; dfflibmap -liberty $LIB; abc -liberty $LIB; clean; stat -liberty $LIB; write_verilog -noattr reports/step3c/$TOP.mapped.v"
done
# Use OpenSTA if available to measure combinational input-to-output critical delay.
rm -rf opensta-src cudd-3.0.0
git clone --depth 1 --recursive https://github.com/The-OpenROAD-Project/OpenSTA.git opensta-src
curl -L -o cudd-3.0.0.tar.gz https://raw.githubusercontent.com/davidkebo/cudd/main/cudd_versions/cudd-3.0.0.tar.gz
tar -xzf cudd-3.0.0.tar.gz
rm cudd-3.0.0.tar.gz
(cd cudd-3.0.0 && ./configure && make -j2)
cmake -S opensta-src -B opensta-src/build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=OFF -DCUDD_DIR="$PWD/cudd-3.0.0" -DFLEX_INCLUDE_DIR=/usr/include
cmake --build opensta-src/build -j2
test -x opensta-src/build/sta
python3 - <<'PY'
from pathlib import Path
for top in ('athena_pe_alu','athena_pe_c2'):
    p=Path(f'reports/step3c/{top}.sdc')
    p.write_text('set_input_delay 0 [all_inputs]\\nset_output_delay 0 [all_outputs]\\n')
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
  opensta-src/build/sta "reports/step3c/$TOP.tcl" | tee "reports/step3c/$TOP.sta.txt"
done
