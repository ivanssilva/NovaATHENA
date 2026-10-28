#!/usr/bin/env python3
"""E1 closed: basic-block characterization on the frozen Embench structural traces.
No superblock construction, no mapping, no synthesis, no cycle-speedup claims.
"""
import csv,glob,os,json,hashlib,collections,statistics,datetime
from pathlib import Path
BR={'beq','bne','blt','bge','bltu','bgeu','jal','jalr','j','jr','ret','call','tail','c.j','c.jal','c.jr','c.jalr','c.beqz','c.bnez','ecall','ebreak','mret','sret'}
COND={'beq','bne','blt','bge','bltu','bgeu','c.beqz','c.bnez'}
RR={'add','sub','and','or','xor','sll','srl','sra','slt','sltu','mul','mulh','mulhu','mulhsu'}
RI={'addi','andi','ori','xori','slli','srli','srai','slti','sltiu'}
ALIASES={'zero':'x0','ra':'x1','sp':'x2','gp':'x3','tp':'x4','t0':'x5','t1':'x6','t2':'x7','s0':'x8','fp':'x8','s1':'x9','a0':'x10','a1':'x11','a2':'x12','a3':'x13','a4':'x14','a5':'x15','a6':'x16','a7':'x17','s2':'x18','s3':'x19','s4':'x20','s5':'x21','s6':'x22','s7':'x23','s8':'x24','s9':'x25','s10':'x26','s11':'x27','t3':'x28','t4':'x29','t5':'x30','t6':'x31'}
def norm(s):return ALIASES.get(s.strip(),s.strip())
def dec(r):
 op=r['op'].lower().strip()
 a=[norm(v) for v in r['args'].split(',')]
 if op in RR and len(a)>=3:return (a[0],a[1:3])
 if op in RI and len(a)>=2:return (a[0],a[1:2])
 return None
def metrics(bb):
 last={}; depths={}; edges=0; maxdepth=0; eligible=0; livein=set()
 for r in bb:
  z=dec(r)
  if z is None:continue
  eligible+=1;d,src=z;deps=[last[x] for x in src if x!='x0' and x in last]
  for x in src:
   if x!='x0' and x not in last:livein.add(x)
  edges+=len(deps);depth=1+max(deps,default=0);maxdepth=max(maxdepth,depth)
  if d!='x0':last[d]=depth
 return eligible,edges,maxdepth,len(livein)
def pct(values,q):
 if not values:return 0
 v=sorted(values);return v[min(len(v)-1,int((len(v)-1)*q))]
paths=sorted(set(glob.glob('structural/*_O*.trace.csv')+glob.glob('structural/**/*.trace.csv',recursive=True)))
assert len(paths)==38,('expected 38 frozen traces',len(paths))
Path('e1-results').mkdir(exist_ok=True)
summary=[];hist=collections.Counter();top=[];audit=[];global_bb=0;global_ins=0
for path in paths:
 name=Path(path).name.removesuffix('.trace.csv');benchmark,opt=name.rsplit('_',1)
 sha=hashlib.sha256(Path(path).read_bytes()).hexdigest()
 lengths=[];eligible_tot=edges_tot=cond=bb_count=0;blocks=collections.Counter()
 current=[];prev=None;trace_rows=0
 def flush():
  nonlocal bb_count,eligible_tot,edges_tot,global_bb
  if not current:return
  bb_count+=1;global_bb+=1
  e,edges,depth,lin=metrics(current);eligible_tot+=e;edges_tot+=edges
  n=len(current);lengths.append(n);hist[(opt,n)]+=1
  start=current[0]['pc'];blocks[(start,n,e,depth,lin)]+=1
 with open(path,newline='') as f:
  reader=csv.DictReader(f)
  assert {'pc','op','args'}.issubset(reader.fieldnames),reader.fieldnames
  for r in reader:
   trace_rows+=1;pc=int(r['pc'],0)
   if prev is not None:
    ppc=int(prev['pc'],0)
    if prev['op'].lower().strip() in BR or pc!=ppc+4:
     flush();current=[]
   current.append(r)
   if r['op'].lower().strip() in COND:cond+=1
   prev=r
 flush()
 assert trace_rows>0 and sum(lengths)==trace_rows,(name,trace_rows,sum(lengths))
 global_ins+=trace_rows
 summary.append(dict(benchmark=benchmark,opt=opt,instructions=trace_rows,dynamic_blocks=bb_count,mean_bb_length=f'{statistics.mean(lengths):.8f}',median_bb_length=statistics.median(lengths),p90_bb_length=pct(lengths,.9),p99_bb_length=pct(lengths,.99),max_bb_length=max(lengths),eligible_alu_ops=eligible_tot,intra_bb_raw_edges=edges_tot,conditional_branches=cond,trace_sha256=sha))
 audit.append((name,trace_rows,bb_count,sha))
 for (pc,n,e,depth,lin),cnt in blocks.most_common(50):
  top.append(dict(benchmark=benchmark,opt=opt,start_pc=pc,length=n,eligible_alu_ops=e,raw_depth=depth,distinct_external_source_registers=lin,occurrences=cnt))
 print('E1_TRACE',name,'instructions',trace_rows,'blocks',bb_count,'eligible',eligible_tot,'RAW_edges',edges_tot,flush=True)
def write(name,rows,fields):
 with open('e1-results/'+name,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
write('e1_per_trace.csv',summary,list(summary[0]))
write('e1_length_histogram.csv',[dict(opt=k[0],length=k[1],dynamic_blocks=v) for k,v in sorted(hist.items())],['opt','length','dynamic_blocks'])
write('e1_top50_blocks_per_trace.csv',top,list(top[0]))
manifest=dict(experiment='E1-basic-block-only',contract='dynamic executed instruction stream; split after control and on non-sequential next PC',limits=['no superblocks','no prediction','no static CFG','no full register liveness','no CGRA mapping','no OoO cycle model','no synthesis'],corpus='Embench RV32IM ILP32 O2/O3; 19 benchmarks 38 traces',source_run=36850448602,source_artifact='athena-embench-structural',traces=audit,totals=dict(traces=len(paths),instructions=global_ins,blocks=global_bb))
Path('e1-results/manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
Path('e1-results/README.md').write_text('# E1 closed characterization\n\nDynamic BB boundaries: after control opcode or at non-sequential next PC (assumes 32-bit RV32IM instructions). Intra-BB RAW edges and depth are register-name based, not a full OoO model. Top50 is by exact (start PC,length,eligible,depth,external source register count), not a static CFG. No live-out claims. Source trace SHA256s are in manifest.json.\n')
assert len(summary)==38 and len({x['benchmark'] for x in summary})==19
print('E1_AUDIT_PASS traces',len(summary),'instructions',global_ins,'blocks',global_bb,flush=True)
