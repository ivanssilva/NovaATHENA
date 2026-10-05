# Step 4C.3 — Nangate45 mapped synthesis of sparse topology finalists

## Provenance
Validated run: 37371559514 (run #3), job 111969702075, head SHA 6b6873b5fdc1e1daecb3307db0faa9ef93fcc398.
Artifact: athena-step4c3-synthesis, ID 11370898275, digest sha256:267c812c4ebf508c2da1e7983fff2aa8b0b1b23b0f6257b9fce0b68f68792fff.
Runs #1 (37367896521) and #2 (37371547574) were workflow-development failures and are excluded from scientific evidence. Only run #3 completed the corrected, Step-3C-derived Yosys/Nangate45/OpenSTA flow.

## Results
K4: mapped cell area 9800.770000; unconstrained combinational max input-output path 4.0306 ns.
K5: mapped cell area 9775.234000; path 4.0186 ns.
K6: mapped cell area 9724.162000; path 5.0651 ns.

K4 and K5 are effectively equivalent in this mapped logical experiment; the small area/timing differences must not be interpreted as physical superiority of K5. K6 increases critical delay by about 26.0% relative to K5 while Step 4C.2 showed only +0.829% structural score gain and the first mux-proxy/fan-in penalty.

## Decision
Use K=5 selective directed links as the current parsimonious reference topology, together with 4 simple ALU positions, 2 C2 positions (8 effective combinational ALUs total), and a separate shared pipelined MUL.

## Limitations
Mapped logical cell area and unconstrained combinational timing are not placed/routed physical metrics. Endpoint labels are canonical structural representatives, not final placement. No cycles, IPC, speedup, external operand pressure, true live-outs, or MUL temporal effects are measured here.
