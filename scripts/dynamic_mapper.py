#!/usr/bin/env python3
"""Exploratory dynamic RAW-window mapper, not Tomasulo cycle-accurate speedup.
Producer identity uses latest register writer; instruction windows do not cross control flow.
All supported ops are single-cycle abstract ALUs; MUL and memory excluded.
"""
import csv,glob,os,collections
os.makedirs("dynamic-results",exist_ok=True)
rr={'add','sub','and','or','xor','sll','srl','sra','slt','sltu'}
ri={'addi','andi','ori','xori','slli','srli','srai','slti','sltiu'}
branches={'beq','bne','blt','bge','bltu','bgeu','jal','jalr','ecall','ebreak'}
def parse(path):
 rows=list(csv.DictReader(open(path)))
 last={};nodes=[];groups=[];current=[];converge=0;diverge=0;chains=0;outdegree=collections.Counter()
 for r in rows:
  op=r['op'].lower();parts=[p.strip() for p in r['args'].split(',')]
  if op in branches:
   if current:groups.append(current);current=[]
   last={};continue
  if op not in rr|ri or len(parts)<3:continue
  dest=parts[0];sources=parts[1:3] if op in rr else parts[1:2]
  deps=set(last[s] for s in sources if s!='zero' and s in last)
  idx=len(nodes);depth=1+max((nodes[p]['depth'] for p in deps),default=0)
  node={'idx':idx,'deps':deps,'depth':depth,'op':op}
  nodes.append(node);current.append(node)
  if len(deps)>=2:converge+=1
  if depth>=3:chains+=1
  for p in deps:outdegree[p]+=1
  if dest!='zero':last[dest]=idx
 if current:groups.append(current)
 diverge=sum(x>=2 for x in outdegree.values())
 return rows,nodes,groups,converge,diverge,chains
def map_group(group,kind,window=16):
 # Conservative graph packing: ready nodes from first bounded prefix of the remaining sequence.
 # Each config can contain 4+4: 4 A then 4 B; PE6: 6 A and up to 6 dependent B.
 # B 1F may consume 2 A results; baseline B may consume only 1.
 remaining=list(group);configs=0;mapped=0;fused=0;occupied=0
 n=6 if kind.startswith('pe6') else 4
 allow2=kind.endswith('1f')
 while remaining:
  cand=remaining[:window];available={x['idx']:x for x in cand};a=[];b=[];chosen=set();onef=0
  for node in cand:
   internal=node['deps']&available.keys()
   if not internal and len(a)<n:a.append(node);chosen.add(node['idx'])
  for node in cand:
   if node['idx'] in chosen:continue
   internal=node['deps']&available.keys()
   within=internal&{x['idx'] for x in a}
   # Reject unresolved in-window deps and out-of-window deps (assume preexisting input values).
   if internal-within:continue
   if not within or len(b)>=n:continue
   if len(within)==2 and (not allow2 or onef):continue
   if len(within)>2:continue
   if kind.startswith('pe6'):
    # PE6 B must be paired with a local A. First fit a unique producer.
    used={x[1] for x in b}
    possible=[p for p in within if p not in used]
    if not possible:continue
    local=possible[0]
    if len(within)==2 and not allow2:continue
    b.append((node,local))
   else:b.append((node,next(iter(within))))
   chosen.add(node['idx'])
   if len(within)==2:onef+=1;fused+=1
  if not chosen:
   chosen.add(remaining[0]['idx'])
  remaining=[x for x in remaining if x['idx'] not in chosen]
  configs+=1;mapped+=len(chosen);occupied+=len(a)+len(b)
 return configs,mapped,fused,occupied
out=[]
for path in sorted(glob.glob('dynamic-results/*.trace.csv')):
 rows,nodes,groups,conv,div,chain=parse(path)
 for kind in ('4x4','4x4_1f','pe6','pe6_1f'):
  vals=[map_group(g,kind) for g in groups]
  out.append(dict(kernel=os.path.basename(path).replace('.trace.csv',''),topology=kind,executed_instructions=len(rows),eligible_alu_ops=len(nodes),convergent_nodes=conv,divergent_nodes=div,depth_ge3=chain,configurations=sum(v[0] for v in vals),mapped_ops=sum(v[1] for v in vals),fused_2producer=sum(v[2] for v in vals),mean_ops_per_configuration=round(sum(v[3] for v in vals)/max(1,sum(v[0] for v in vals)),3)))
if not out:raise SystemExit('No dynamic traces')
with open('dynamic-results/dynamic_summary.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
print('Wrote',len(out),'kernel/topology combinations')
