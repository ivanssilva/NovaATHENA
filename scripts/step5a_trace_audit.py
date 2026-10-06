#!/usr/bin/env python3
"""ATHENA Step 5A: audit validated Embench traces for temporal-model fields.
Audits what is actually present/reconstructable; does not invent cycle data. This audit gates the temporal simulator.
"""
import csv,glob,os,re,collections
paths=sorted(glob.glob('embench-results/*_O*.trace.csv')); assert len(paths)==38
CTRL={'beq','bne','blt','bge','bltu','bgeu','beqz','bnez','bltz','bgez','blez','bgtz','bgt','ble','bgtu','bleu','j','jal','jalr','jr','ret'}
MEM={'lb','lh','lw','lbu','lhu','sb','sh','sw'}
MUL={'mul','mulh','mulhu','mulhsu'}
DIV={'div','divu','rem','remu'}
regpat=re.compile(r'\b(?:x(?:[12]?\d|3[01])|zero|ra|sp|gp|tp|t[0-6]|s(?:[0-9]|1[01])|fp|a[0-7])\b')
tot=collections.Counter(); per=[]
schemas=set();badseq=badpc=badtb=0; pc_trans=ctrl_with_next=0; mem_addr_explicit=0
for p in paths:
 name=os.path.basename(p).replace('.trace.csv',''); b,o=name.rsplit('_',1)
 with open(p,newline='') as f:
  r=csv.DictReader(f); schemas.add(tuple(r.fieldnames or [])); rows=list(r)
 n=len(rows); c=collections.Counter()
 prevseq=-1
 for i,x in enumerate(rows):
  seq=x.get('seq','');pc=x.get('pc','');tb=x.get('tb_start','');op=x.get('op','').lower();args=x.get('args','')
  try:
   si=int(seq); assert si==prevseq+1;prevseq=si
  except: badseq+=1
  try:int(pc,16)
  except:badpc+=1
  try:int(tb,16)
  except:badtb+=1
  c['instructions']+=1;c['control']+=op in CTRL;c['memory']+=op in MEM;c['mul']+=op in MUL;c['divrem']+=op in DIV
  if op in MEM:
   # Trace has assembly addressing expression, not effective runtime address.
   if re.search(r'0x[0-9a-fA-F]+\s*\(',args): mem_addr_explicit+=1
  if i+1<n:
   pc_trans+=1
   if op in CTRL:ctrl_with_next+=1
 per.append((b,o,c['instructions'],c['control'],c['memory'],c['mul'],c['divrem']))
 tot.update(c)
print('STEP5A_AUDIT traces',len(paths),'pairs',len(per),'schemas',len(schemas),'bad_seq',badseq,'bad_pc',badpc,'bad_tb_start',badtb,flush=True)
for s in schemas:print('STEP5A_SCHEMA',','.join(s),flush=True)
print('STEP5A_TOTAL instructions',tot['instructions'],'control',tot['control'],'memory',tot['memory'],'mul',tot['mul'],'divrem',tot['divrem'],flush=True)
print('STEP5A_FIELDS seq=present pc=present op=present args=present tb_start=present dynamic_effective_address=absent cycle_timestamp=absent branch_outcome=not_explicit squash_event=absent cache_event=absent rename_tag=absent rob_event=absent',flush=True)
print('STEP5A_RECONSTRUCT control_next_pc=possible_from_dynamic_sequence raw_arch_register_producer=possible_from_sequence region_identity=possible_from_pc_and_gt_mapping effective_memory_address=not_reconstructable_without_register_values_or_new_instrumentation',flush=True)
print('STEP5A_CONTROL transitions',pc_trans,'control_with_observed_next',ctrl_with_next,flush=True)
with open('step5a_trace_audit.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['benchmark','opt','instructions','control_ops','memory_ops','mul_ops','divrem_ops']);w.writerows(per)
print('STEP5A_LIMIT temporal host simulation requiring memory/cache timing, speculative branch/squash events, ROB/RS occupancy or exact issue/commit times cannot be directly measured from current trace fields; those require explicit model assumptions and/or regenerated instrumentation.',flush=True)
