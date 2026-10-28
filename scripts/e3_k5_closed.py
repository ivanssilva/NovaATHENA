#!/usr/bin/env python3
"""E3 closed conservative K5 structural analysis. Fixed 38 frozen traces.
Within retrospective BB windows, split at every noneligible instruction (including
control/memory). This deliberately does NOT claim cross-barrier acceleration.
"""
import csv,glob,os,json,hashlib,collections,re
from pathlib import Path
RR={'add','sub','and','or','xor','sll','srl','sra','slt','sltu'}
RI={'addi','andi','ori','xori','slli','srli','srai','slti','sltiu'}
MUL={'mul','mulh','mulhu','mulhsu'}
BR={'beq','bne','blt','bge','bltu','bgeu','jal','jalr','j','jr','ret','call','tail','c.j','c.jal','c.jr','c.jalr','c.beqz','c.bnez','ecall','ebreak','mret','sret'}
A={'zero':'x0','ra':'x1','sp':'x2','gp':'x3','tp':'x4','t0':'x5','t1':'x6','t2':'x7','s0':'x8','fp':'x8','s1':'x9','a0':'x10','a1':'x11','a2':'x12','a3':'x13','a4':'x14','a5':'x15','a6':'x16','a7':'x17','s2':'x18','s3':'x19','s4':'x20','s5':'x21','s6':'x22','s7':'x23','s8':'x24','s9':'x25','s10':'x26','s11':'x27','t3':'x28','t4':'x29','t5':'x30','t6':'x31'}
def n(x):return A.get(x.strip(),x.strip())
S=('A0','A1','A2','A3','C0A','C0B','C1A','C1B')
LINKS={('C0A','C0B'),('C1A','C1B'),('A0','A1'),('A1','C0B'),('A2','C1B'),('C1A','C0A'),('C1B','A3')}
cache={}
def embed(sig):
 if sig in cache:return cache[sig]
 if len(sig)>8:return False
 edges=[(d,j) for j,ds in enumerate(sig) for d in ds]
 order=sorted(range(len(sig)),key=lambda u:-sum(u in e for e in edges))
 assign={};used=set()
 def rec(k):
  if k==len(sig):return True
  u=order[k]
  for slot in S:
   if slot in used:continue
   if any((slot,assign[b]) not in LINKS for a,b in edges if a==u and b in assign):continue
   if any((assign[a],slot) not in LINKS for a,b in edges if b==u and a in assign):continue
   assign[u]=slot;used.add(slot)
   if rec(k+1):return True
   used.remove(slot);del assign[u]
  return False
 z=rec(0);cache[sig]=z;return z
def elig(r):
 op=r['op'].lower().strip();args=[n(x) for x in r['args'].split(',')]
 if op in RR and len(args)>=3:return args[0],args[1:3]
 if op in RI and len(args)>=2:return args[0],args[1:2]
 return None
def evaluate(nodes):
 last={};deps=[];depth=[];livein=set();defs=[]
 for i,(d,src) in enumerate(nodes):
  ps=tuple(sorted(set(last[x] for x in src if x!='x0' and x in last)))
  for x in src:
   if x!='x0' and x not in last:livein.add(x)
  deps.append(ps);depth.append(1+max((depth[p] for p in ps),default=0))
  if d!='x0':last[d]=i;defs.append(d)
 # liveouts are a conservative upper bound: every distinct written register
 # may be observable later, since complete backward liveness is not modeled.
 out=len(set(defs))
 if len(nodes)>8:return 'capacity'
 if max(depth,default=0)>3:return 'depth'
 if len(livein)>5:return 'inputs'
 if out>4:return 'outputs_conservative'
 if not embed(tuple(deps)):return 'topology'
 return 'mapped_conservative'
paths=sorted(set(glob.glob('structural/*_O*.trace.csv')+glob.glob('structural/**/*.trace.csv',recursive=True)))
assert len(paths)==38,len(paths)
Path('e3-results').mkdir(exist_ok=True)
out=[];audits=[]
for path in paths:
 name=Path(path).name.removesuffix('.trace.csv');bench,opt=name.rsplit('_',1)
 counters={k:collections.Counter() for k in (1,2,4,8)}
 windows={k:[] for k in (1,2,4,8)}
 bb=[];prev=None;nrows=0;nbb=0
 def process(window,k):
  c=counters[k];c['windows']+=1;c['BBs']+=len(window)
  region=[r for i,block in enumerate(window) for r in (([{'op':'__bb_boundary__','pc':'0','args':''}] if i else [])+block)]
  c['instructions']+=sum(len(block) for block in window)
  island=[]
  def flush():
   if not island:return
   status=evaluate(island);c['islands']+=1;c['eligible_ops']+=len(island)
   c[status+'_islands']+=1;c[status+'_ops']+=len(island)
   island.clear()
  for r in region:
   q=elig(r)
   if q:island.append(q)
   else:
    flush();c['barriers']+=1
    if r['op'].lower().strip() in MUL:c['mul_barriers']+=1
  flush()
 def addbb():
  global nbb
  if not bb:return
  nbb+=1
  for k in (1,2,4,8):
   windows[k].append(bb[:])
   if len(windows[k])==k:process(windows[k],k);windows[k].clear()
 with open(path,newline='') as f:
  reader=csv.DictReader(f);assert {'pc','op','args'}.issubset(reader.fieldnames)
  for r in reader:
   nrows+=1;pc=int(r['pc'],0)
   if prev is not None and (prev['op'].lower().strip() in BR or pc!=int(prev['pc'],0)+4):
    addbb();bb=[]
   bb.append(r);prev=r
 addbb()
 for k in (1,2,4,8):
  if windows[k]:process(windows[k],k)
  c=counters[k];assert c['BBs']==nbb and c['instructions']==nrows,(name,k,c,nbb,nrows)
  out.append(dict(benchmark=bench,opt=opt,group_BBs=k,**{x:c[x] for x in ('windows','BBs','instructions','barriers','mul_barriers','islands','eligible_ops','mapped_conservative_islands','mapped_conservative_ops','capacity_islands','capacity_ops','depth_islands','depth_ops','inputs_islands','inputs_ops','outputs_conservative_islands','outputs_conservative_ops','topology_islands','topology_ops')}))
 audits.append(dict(trace=name,sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),instructions=nrows,blocks=nbb))
 print('E3_TRACE',name,'rows',nrows,'blocks',nbb,'mapped_ops_k8',counters[8]['mapped_conservative_ops'],flush=True)
with open('e3-results/e3_per_trace.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
with open('e3-results/e3_aggregate.csv','w',newline='') as f:
 cols=list(out[0]);w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
 for opt in ('O2','O3'):
  for k in (1,2,4,8):
   rr=[r for r in out if r['opt']==opt and r['group_BBs']==k]
   w.writerow(dict(benchmark='ALL',opt=opt,group_BBs=k,**{key:sum(r[key] for r in rr) for key in cols[3:]}))
assert len(out)==152 and len(audits)==38
for r in out:
 assert r['eligible_ops']==sum(r[x+'_ops'] for x in ('mapped_conservative','capacity','depth','inputs','outputs_conservative','topology'))
# Because every BB ends with a control barrier or a PC discontinuity,
# grouping must not change the arithmetic islands or their mapping.
for (bench,opt),rr in __import__('itertools').groupby(sorted(out,key=lambda r:(r['benchmark'],r['opt'],r['group_BBs'])),lambda r:(r['benchmark'],r['opt'])):
 v=list(rr);assert len(v)==4
 assert len({r['mapped_conservative_ops'] for r in v})==1,(bench,opt)
manifest=dict(experiment='E3-closed-conservative-K5',source_run=36850448602,source_artifact='athena-embench-structural',group_sizes=[1,2,4,8],trace_audit=audits,architecture=dict(K=5,slots=8,max_depth=3,liveins=5,conservative_distinct_destinations=4),method='Retrospective BB grouping; strict splitting at every noneligible instruction; K5 mapper from step4d3_joint_capacity; no cross-control or memory execution; no MUL timing',limits=['Every distinct written register counted as potentially live-out (conservative, not precise liveness)','No mapping across memory/control/unsupported instructions','No superblock execution, prediction, speedup, synthesis','K5 graph topology ignores physical timing','If group size has no effect, this is a scientific negative result under strict barriers'])
Path('e3-results/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
Path('e3-results/README.md').write_text('# E3 closed — conservative structural bound\n\nSame 38 frozen traces. K5 fixed links, 8 slots, depth 3, five live-ins and conservative four distinct destination registers. Every noneligible instruction is a hard barrier, including memory, control, MUL and unsupported instructions. Therefore BB grouping cannot introduce cross-branch fusion in this baseline. No real superblock is modeled. This negative control explicitly tests whether changing retrospective window size alone helps under unchanged host barriers. Do not present this as a full E3 superblock feasibility result.\n')
print('E3_AUDIT_PASS traces 38 rows 152 signatures',len(cache),flush=True)
