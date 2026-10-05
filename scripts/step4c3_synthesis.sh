#!/usr/bin/env bash
set -euo pipefail
LIB="$1"; mkdir -p step4c3_out
for TOP in athena_top_k4 athena_top_k5 athena_top_k6; do
 yosys -p "read_verilog rtl/athena_alu32.v rtl/step4c3_topologies.v; hierarchy -top $TOP; proc; opt; techmap; opt; dfflibmap -liberty $LIB; abc -liberty $LIB; clean; stat -liberty $LIB; write_verilog step4c3_out/$TOP.mapped.v" | tee step4c3_out/$TOP.yosys.log
 AREA=$(grep -E 'Chip area for module' step4c3_out/$TOP.yosys.log | tail -1 | awk '{print $NF}')
 cat > step4c3_out/$TOP.sta.tcl <<EOF
read_liberty $LIB
read_verilog step4c3_out/$TOP.mapped.v
link_design $TOP
report_checks -unconstrained -from [all_inputs] -to [all_outputs] -path_delay max -digits 4
EOF
 sta step4c3_out/$TOP.sta.tcl | tee step4c3_out/$TOP.sta.log
 DELAY=$(grep -E 'data arrival time' step4c3_out/$TOP.sta.log | tail -1 | awk '{print $1}')
 echo "STEP4C3_RESULT $TOP area $AREA delay_ns $DELAY"
done
