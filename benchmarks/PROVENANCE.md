# Kernel acquisition plan and provenance

Stage 1 is an executable *controlled synthetic* corpus: ten distinct integer algorithm templates, each with three input/repetition variants (30 compiled programs). They are **not** 30 independent real-world applications. This corpus is for pipeline smoke-testing and sensitivity to optimization level, not representative architectural claims.

Stage 2 must acquire actual benchmark suites from pinned upstream revisions, retaining each license and provenance:
- Embench IoT: https://github.com/embench/embench-iot (embedded application diversity).
- PolyBench/C: https://sourceforge.net/projects/polybench/ (linear algebra and data mining; review its Ohio State license before redistribution).
- MiBench: https://github.com/pulp-platform/mibench (automotive, security, telecom etc.; verify each component's licensing).

Do not copy external benchmarks into this public repository until the license of every selected component has been checked. Prefer pinned upstream checkouts at workflow runtime.

The current analyzer is deliberately a **static within-basic-block proxy**; it does not model register renaming, dynamic dispatch, ROB occupancy, branch behavior, or memory aliasing. Its counts are not a substitute for runtime instruction traces. A validated dynamic tracer and a four-topology mapping simulator are required before any claims about utilization, speedup, or real convergence frequency.
