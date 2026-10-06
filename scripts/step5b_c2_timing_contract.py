#!/usr/bin/env python3
"""Step 5B: timing-contract decision for PE-C2.

Uses only already measured unconstrained Nangate45 timing evidence. It does NOT
claim a final processor clock. It derives break-even cycle-reduction thresholds
for a same-cycle C2 interpretation versus a simple-ALU timing reference.

Measured evidence:
 PE-ALU 1.3127 ns
 PE-C2  1.9491 ns
 K5     4.0186 ns (complete synthesized topology wrapper)
"""
alu=1.3127;c2=1.9491;k5=4.0186
for name,t in [('PE_C2',c2),('K5_WRAPPER',k5)]:
 penalty=t/alu
 required=1-1/penalty
 print('STEP5B_TIMING',name,'delay_ns',f'{t:.4f}','vs_alu',f'{penalty:.6f}','required_cycle_reduction_for_break_even',f'{required:.6f}')
print('STEP5B_TIMING PE_ALU delay_ns',f'{alu:.4f}')
print('STEP5B_DECISION same_cycle_C2 cannot be enabled at equal clock from current evidence; any cycle-count experiment must be paired with clock-period sensitivity or constrained synthesis.')
print('STEP5B_INTERPRET PE_C2 requires >32.65% cycle reduction to offset its 1.485x local critical-path ratio if that ratio sets the clock; K5 wrapper would require >67.34% if its unconstrained path set the clock.')
print('STEP5B_CAUTION these are break-even analytical thresholds from mapped combinational timing, not measured application performance and not a final processor frequency.')
