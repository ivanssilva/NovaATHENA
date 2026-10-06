#!/usr/bin/env python3
"""Step 5B contract audit: idealized compute-only temporal bound.
This step freezes assumptions and reports trace-derived scheduling inputs.
It deliberately does NOT call a structural proxy speedup.
"""
import csv,glob,os,collections,statistics
paths=sorted(glob.glob('embench-results/*_O*.trace.csv')); assert len(paths)==38
ALU={'add','sub','and','or','xor','sll','srl','sra','slt','sltu','addi','andi','ori','xori','slli','srli','srai','slti','sltiu'}
MUL={'mul','mulh','mulhu','mulhsu'}; DIV={'div','divu','rem','remu'}
MEM={'lb','lh','lw','lbu','lhu','sb','sh','sw'}
CTRL={'beq','bne','blt','bge','bltu','bgeu','beqz','bnez','bltz','bgez','blez','bgtz','bgt','ble','bgtu','bleu','j','jal','jalr','jr','ret'}
tot=collections.Counter(); per=[]
for p in paths:
 b,o=os.path.basename(p).replace('.trace.csv','').rsplit('_',1);c=collections.Counter()
 for r in csv.DictReader(open(p)):
  op=r['op'].lower();c['instructions']+=1;c['alu']+=op in ALU;c['mul']+=op in MUL;c['divrem']+=op in DIV;c['memory']+=op in MEM;c['control']+=op in CTRL
 per.append((b,o,*[c[k] for k in ('instructions','alu','mul','divrem','memory','control')]));tot.update(c)
with open('step5b_trace_inputs.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['benchmark','opt','instructions','alu','mul','divrem','memory','control']);w.writerows(per)
print('STEP5B_AUDIT traces',len(paths),'pairs',len(per),flush=True)
print('STEP5B_INPUT instructions',tot['instructions'],'alu',tot['alu'],'mul',tot['mul'],'divrem',tot['divrem'],'memory',tot['memory'],'control',tot['control'],flush=True)
print('STEP5B_CONTRACT baseline_issue_width=4 athena=4PE_ALU+2PE_C2+K5+5IN+4OUT+1MUL_pipeline equal_clock=yes memory_stalls=zero branch_mispredict=zero config_overhead=zero mul_temporal_latency=deferred divrem_on_host=yes',flush=True)
print('STEP5B_SEMANTICS equal-clock compute-only temporal bound; not final application speedup; enriched addresses are intentionally deferred to Step5C memory/cache layer.',flush=True)
print('STEP5B_LIMIT current architectural traces do not contain ROB/RS occupancy or measured issue/commit timestamps; any OoO scheduler must therefore be an explicit model, not presented as measured hardware behavior.',flush=True)
