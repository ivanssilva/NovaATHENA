#!/usr/bin/env bash
set -euo pipefail
mkdir -p reports/step4c3
LIB="$PWD/orfs/flow/platforms/nangate45/lib/NangateOpenCellLibrary_typical.lib"
for TOP in athena_top_k4 athena_top_k5 athena_top_k6; do
  yosys -Q -T -l "reports/step4c3/$TOP.log" -p "read_verilog -sv rtl/athena_alu32.v rtl/step4c3_topologies.v; hierarchy -check -top $TOP; synth -top $TOP -flatten; dfflibmap -liberty $LIB; abc -liberty $LIB; clean; stat -liberty $LIB; write_verilog -noattr reports/step4c3/$TOP.mapped.v"
done
rm -rf opensta-src cudd-3.0.0
git clone --depth 1 --recursive https://github.com/The-OpenROAD-Project/OpenSTA.git opensta-src
curl -L -o cudd-3.0.0.tar.gz https://raw.githubusercontent.com/davidkebo/cudd/main/cudd_versions/cudd-3.0.0.tar.gz
tar -xzf cudd-3.0.0.tar.gz && rm cudd-3.0.0.tar.gz
(cd cudd-3.0.0 && ./configure && make -j2)
FLEX_HEADER="$(dpkg -L libfl-dev | grep -m1 '/FlexLexer.h$')"; test -n "$FLEX_HEADER"; FLEX_INCLUDE_DIR="$(dirname "$FLEX_HEADER")"
cmake -S opensta-src -B opensta-src/build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=OFF -DCUDD_DIR="$PWD/cudd-3.0.0" -DFLEX_INCLUDE_DIR="$FLEX_INCLUDE_DIR"
cmake --build opensta-src/build -j2
test -x opensta-src/build/sta
for TOP in athena_top_k4 athena_top_k5 athena_top_k6; do
cat > "reports/step4c3/$TOP.tcl" <<EOF
read_liberty $LIB
read_verilog reports/step4c3/$TOP.mapped.v
link_design $TOP
report_checks -unconstrained -from [all_inputs] -to [all_outputs] -path_delay max -digits 4
EOF
 opensta-src/build/sta "reports/step4c3/$TOP.tcl" | tee "reports/step4c3/$TOP.sta.txt"
 AREA="$(grep -E 'Chip area for module' reports/step4c3/$TOP.log | tail -1 | awk '{print $NF}')"
 DELAY="$(grep -E 'data arrival time' reports/step4c3/$TOP.sta.txt | tail -1 | awk '{print $1}')"
 echo "STEP4C3_RESULT $TOP area $AREA delay_ns $DELAY" | tee -a reports/step4c3/summary.txt
done
test "$(grep -c STEP4C3_RESULT reports/step4c3/summary.txt)" -eq 3
