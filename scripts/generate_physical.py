#!/usr/bin/env python3
"""Generate equal registered I/O wrappers and ORFS configs for each topology."""
import re,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
out=root/"physical";out.mkdir(exist_ok=True)
for top in ("athena_4x4","athena_pe6","athena_4x4_1f","athena_pe6_1f"):
 src=(root/"rtl"/(top+".v")).read_text()
 decl=src.split("(",1)[1].split(");",1)[0]
 ports=[]
 # Input/output declarations may contain multiple comma-separated names.
 for m in re.finditer(r'\b(input|output)\s*(\[\d+:\d+\])?\s*([^;]*?)(?=,\s*(?:input|output)\b|$)',decl,re.S):
  direction,width,names=m.groups()
  for name in names.split(","):
   name=name.strip()
   if name:ports.append((direction,width or "",name))
 assert ports and all(re.fullmatch(r"\w+",p[2]) for p in ports),ports
 ins=[p for p in ports if p[0]=="input"];outs=[p for p in ports if p[0]=="output"]
 wrapper=top+"_reg"
 lines=[f"module {wrapper}(input clk, "+", ".join(("input " if d=="input" else "output reg ")+(w+" " if w else "")+n for d,w,n in ports)+");"]
 for _,w,n in ins:lines.append(f"reg {w} q_{n};")
 for _,w,n in outs:lines.append(f"wire {w} w_{n};")
 lines.append("always @(posedge clk) begin")
 for _,w,n in ins:lines.append(f"q_{n} <= {n};")
 for _,w,n in outs:lines.append(f"{n} <= w_{n};")
 lines.append("end")
 lines.append(top+" dut("+", ".join("."+n+"(" + ("q_"+n if d=="input" else "w_"+n)+")" for d,w,n in ports)+");")
 lines.append("endmodule")
 (out/(wrapper+".v")).write_text("\n".join(lines)+"\n")
 (out/(top+".mk")).write_text(f"""export DESIGN_NAME = {wrapper}
export PLATFORM = nangate45
export VERILOG_FILES = /work/rtl/athena_alu32.v /work/rtl/{top}.v /work/physical/{wrapper}.v
export SDC_FILE = /work/physical/constraint.sdc
export CORE_UTILIZATION = 40
export PLACE_DENSITY_LB_ADDON = 0.20
export ABC_AREA = 1
export SYNTH_REPEATABLE_BUILD = 1
export ADDER_MAP_FILE :=
""")
(out/"constraint.sdc").write_text("""create_clock -name clk -period 20 [get_ports clk]
set_input_delay 2 -clock clk [all_inputs -no_clocks]
set_output_delay 2 -clock clk [all_outputs]
""")
print("Generated wrappers for 4 topologies")
