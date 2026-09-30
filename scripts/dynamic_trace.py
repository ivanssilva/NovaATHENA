#!/usr/bin/env python3
"""Reconstruct RV32 instruction streams from QEMU -d in_asm,exec,nochain logs."""
import csv
import pathlib
import re
import sys

src, dest = map(pathlib.Path, sys.argv[1:3])
blocks = {}
trace = []
current = None

for line in src.open(errors="replace"):
    if re.match(r"^IN:\\s*(?:.*)?$", line):
        if current:
            blocks[current[0][0]] = current
        current = []
        continue
    # QEMU logs encode machine words between guest PC and mnemonic.
    m = re.match(r"^0x([0-9a-fA-F]+):\\s+(?:[0-9a-fA-F]{4,8}\\s+)+([a-zA-Z][\\w.]*)\\s*(.*)", line)
    if current is not None and m:
        current.append((int(m[1], 16), m[2], m[3].split("#")[0].strip()))
        continue
    # [flags/guest_PC/...] is emitted for every translated-block execution.
    t = re.search(r"Trace\\s+\\d+:.*?\\[([0-9a-fA-F]+)/([0-9a-fA-F]+)/", line)
    if t:
        trace.append(int(t[2], 16))
    if current is not None and not line.strip():
        if current:
            blocks[current[0][0]] = current
        current = None

if current:
    blocks[current[0][0]] = current

missing = sum(pc not in blocks for pc in trace)
count = 0
with dest.open("w", newline="") as output:
    writer = csv.writer(output)
    writer.writerow(("seq", "pc", "op", "args", "tb_start"))
    for tb_pc in trace:
        for pc, op, args in blocks.get(tb_pc, ()):
            writer.writerow((count, hex(pc), op, args, hex(tb_pc)))
            count += 1

print(f"{src.name}: TBs={len(trace)}, instructions={count}, missing_TBs={missing}")
if missing or not trace or not count:
    print("DEBUG: first 35 lines of QEMU log:")
    print("\\n".join(src.read_text(errors="replace").splitlines()[:35]))
    sys.exit(2)
