# Multiplier temporal design assumption for ATHENA

Status: user-supplied architectural design assumption, not yet a measured synthesis result.

For subsequent ATHENA temporal modeling, the intended RISC-V multiplier has:
- latency L_MUL in the approximate range 6-8 cycles;
- pipelined operation;
- initiation interval II_MUL = 1 cycle: successive independent multiplications may start in successive cycles and, after pipeline fill, complete in successive cycles.

Consequences:
1. MUL must not be modeled as a one-cycle combinational operation or folded into a one-cycle C2 motif.
2. Resource-demand analysis must distinguish latency from throughput. A single pipelined multiplier can sustain one new independent multiplication per cycle once filled.
3. Multiple MULs structurally present in a G_t do not by themselves imply that multiple physical multipliers are required.
4. Dependent consumers still wait for the producing MUL latency.
5. A future Verilog implementation of the RISC-V multiplier is expected from the project owner; once available, it should replace this assumed latency with same-flow measured timing/area/leakage evidence where applicable.
