#!/usr/bin/env python3
"""ATHENA Step 4D.3: joint structural-capacity validation.
Definitive G_t(D=3,C=8) semantics: DIV/REM known but ineligible.
Tests the K5 sparse non-MUL backbone jointly with 5-in/4-out base interface
and 6-in/4-out sensitivity. MUL-containing groups are reported separately
because the shared pipelined multiplier is temporal (L=6--8, II=1), not a
same-cycle combinational slot. Structural evidence only; not speedup. DIV/REM remain recognized liveness barriers.
"""
import csv,glob,os,re,collections,statistics,json
RR={'add','sub','and','or','xor','sll','srl','sra','slt','sltu','mul','mulh','mulhu','mulhsu'}
RI={'addi','andi','ori','xori','slli','srli','srai','slti','sltiu'}
EL=RR|RI; D=3; C=8
ALIASES={'zero':'x0','ra':'x1','sp':'x2','gp':'x3','tp':'x4','t0':'x5','t1':'x6','t2':'x7','s0':'x8','fp':'x8','s1':'x9','a0':'x10','a1':'x11','a2':'x12','a3':'x13','a4':'x14','a5':'x15','a6':'x16','a7':'x17','s2':'x18','s3':'x19','s4':'x20','s5':'x21','s6':'x22','s7':'x23','s8':'x24','s9':'x25','s10':'x26','s11':'x27','t3':'x28','t4':'x29','t5':'x30','t6':'x31'}
REG=re.compile(r'^(?:x(?:[12]?\\d|3[01])|zero|ra|sp|gp|tp|t[0-6]|s(?:[0-9]|1[01])|fp|a[0-7])$')
def n(x): return ALIASES.get(x.strip(),x.strip())
def regs(x): return [n(z) for z in re.findall(r'\\b(?:x(?:[12]?\\d|3[01])|zero|ra|sp|gp|tp|t[0-6]|s(?:[0-9]|1[01])|fp|a[0-7])\\b',x)]
def elig(op,a):
 if op not in EL or len(a)<2:return None
 return n(a[0]),[n(x) for x in (a[1:3] if op in RR else a[1:2])]
def usedef(op,a):
 A=[n(x) for x in a]
 if op in RR or op in RI:
  q=elig(op,A); return set(q[1]),({q[0]} if q[0]!='x0' else set())
 if op in {'div','divu','rem','remu'} and len(A)>=3:return set(x for x in A[1:3] if x!='x0'),({A[0]} if A[0]!='x0' else set())
 if op in {'lui','auipc'} and A:return set(),({A[0]} if A[0]!='x0' else set())
 if op in {'lb','lh','lw','lbu','lhu'} and A:return set(regs(','.join(A[1:]))),({A[0]} if A[0]!='x0' else set())
 if op in {'sb','sh','sw'} and A:return set(regs(','.join(A))),set()
 if op in {'beq','bne','blt','bge','bltu','bgeu'}:return set(x for x in A[:2] if REG.match(x) and x!='x0'),set()
 if op=='jal' and A:
  if len(A)>=2 and REG.match(A[0]):return set(),({A[0]} if A[0]!='x0' else set())
  return set(),{'x1'}
 if op=='jalr' and A:
  d=A[0] if REG.match(A[0]) else 'x1';u=set(regs(','.join(A[1:] if REG.match(A[0]) else A)));return u,({d} if d!='x0' else set())
 if op=='mv' and len(A)>=2:return ({A[1]} if A[1]!='x0' else set()),({A[0]} if A[0]!='x0' else set())
 if op in {'not','neg','snez','seqz'} and len(A)>=2:return ({A[1]} if A[1]!='x0' else set()),({A[0]} if A[0]!='x0' else set())
 if op in {'bnez','beqz','bltz','bgez','blez','bgtz'} and A:return ({A[0]} if A[0]!='x0' else set()),set()
 if op in {'bgt','ble','bgtu','bleu'} and len(A)>=2:return set(x for x in A[:2] if REG.match(x) and x!='x0'),set()
 if op=='j':return set(),set()
 if op=='ret':return {'x1'},set()
 if op=='jr' and A:return ({A[0]} if A[0]!='x0' else set()),set()
 if op=='csrrs' and A:
  u=set()
  if len(A)>=3 and REG.match(A[2]) and A[2]!='x0':u.add(A[2])
  d={A[0]} if REG.match(A[0]) and A[0]!='x0' else set();return u,d
 if op in {'ecall','ebreak','fence','fence.i','nop'}:return set(),set()
 return set(x for x in regs(','.join(A)) if x!='x0'),set()
class G:
 def __init__(self):self.reset()
 def reset(self):self.nodes=[];self.w={};self.dep=[];self.ext=set();self.defs=[]
 def prospective(self,src):
  ds=tuple(sorted(set(self.w[x] for x in src if x!='x0' and x in self.w)));return ds,1+max((self.dep[i] for i in ds),default=0)
 def add(self,op,dst,src,ds,d,idx):
  for x in src:
   if x!='x0' and x not in self.w:self.ext.add(x)
  i=len(self.nodes);self.nodes.append((op,ds));self.dep.append(d)
  if dst!='x0':self.w[dst]=i;self.defs.append((dst,idx))
# K5 Pareto representative 1 from Step 4C.2 plus fixed C2 links
S=('A0','A1','A2','A3','C0A','C0B','C1A','C1B')
LINKS={('C0A','C0B'),('C1A','C1B'),('A0','A1'),('A1','C0B'),('A2','C1B'),('C1A','C0A'),('C1B','A3')}
embcache={}
def backbone_signature(nodes):
 keep=[i for i,(op,ds) in enumerate(nodes) if not op.startswith('mul')]
 rem={x:i for i,x in enumerate(keep)}
 return tuple((nodes[x][0],tuple(rem[d] for d in nodes[x][1] if d in rem)) for x in keep)
def emb(sig):
 if sig in embcache:return embcache[sig]
 if len(sig)>8:embcache[sig]=False;return False
 ed=[(d,j) for j,(_,ds) in enumerate(sig) for d in ds]
 order=sorted(range(len(sig)),key=lambda u:-sum(u in e for e in ed));ass={};used=set()
 def rec(k):
  if k==len(sig):return True
  u=order[k]
  for sl in S:
   if sl in used:continue
   ok=True
   for a,b in ed:
    if a==u and b in ass and (sl,ass[b]) not in LINKS:ok=False;break
    if b==u and a in ass and (ass[a],sl) not in LINKS:ok=False;break
   if ok:
    ass[u]=sl;used.add(sl)
    if rec(k+1):return True
    used.remove(sl);del ass[u]
  return False
 z=rec(0);embcache[sig]=z;return z
paths=sorted(glob.glob('embench-results/*_O*.trace.csv'));assert len(paths)==38
# key b,opt,ops,li,lo,mulcount,backbone_mappable
agg=collections.Counter();unknown=collections.Counter()
for pi,p in enumerate(paths,1):
 name=os.path.basename(p).replace('.trace.csv','');b,o=name.rsplit('_',1);rows=[]
 with open(p,newline='') as f:
  for r in csv.DictReader(f):
   op=r['op'].lower();a=[x.strip() for x in r['args'].split(',') if x.strip()];rows.append((op,a))
 live=set();deflive=[False]*len(rows)
 for i in range(len(rows)-1,-1,-1):
  op,a=rows[i];u,d=usedef(op,a);q=elig(op,a)
  if q and q[0]!='x0':deflive[i]=q[0] in live
  live.difference_update(d);live.update(u)
  known=(op in RR or op in RI or op in {'div','divu','rem','remu','lui','auipc','lb','lh','lw','lbu','lhu','sb','sh','sw','beq','bne','blt','bge','bltu','bgeu','jal','jalr','mv','not','neg','snez','seqz','bnez','beqz','bltz','bgez','blez','bgtz','bgt','ble','bgtu','bleu','j','ret','jr','csrrs','ecall','ebreak','fence','fence.i','nop'})
  if not known:unknown[(op,tuple(a))]+=1
 g=G();ng=0
 def flush():
  nonlocal_ng[0]+=1
  if not g.nodes:return
  last={}
  for reg,i in g.defs:last[reg]=i
  lo=sum(deflive[i] for i in last.values());mc=sum(op.startswith('mul') for op,_ in g.nodes);sig=backbone_signature(g.nodes)
  agg[(b,o,len(g.nodes),len(g.ext),lo,mc,emb(sig))]+=1;g.reset()
 nonlocal_ng=[0]
 for i,(op,a) in enumerate(rows):
  q=elig(op,a)
  if q is None:
   if g.nodes:flush()
   continue
  dst,src=q;ds,d=g.prospective(src)
  if g.nodes and (len(g.nodes)>=C or d>D):flush();ds,d=g.prospective(src)
  g.add(op,dst,src,ds,d,i)
 if g.nodes:flush()
 print('STEP4D3_TRACE',pi,'/',38,name,'groups',nonlocal_ng[0],flush=True)
with open('step4d3_joint_counts.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['benchmark','opt','ops','liveins','liveouts','mul_count','backbone_mappable','occurrences'])
 for k,v in sorted(agg.items()):w.writerow([*k,v])
print('STEP4D3_AUDIT traces',len(paths),'pairs',len(set((k[0],k[1]) for k in agg)),'unknown_occurrences',sum(unknown.values()),'unknown_forms',len(unknown),'backbone_signatures',len(embcache),flush=True)
def frac(rows,pred,opw=False):
 den=sum(v*(k[2] if opw else 1) for k,v in rows);num=sum(v*(k[2] if opw else 1) for k,v in rows if pred(k));return num/den if den else 0
for opt in ('O2','O3'):
 bs=sorted(set(k[0] for k in agg if k[1]==opt))
 for nin,nout in ((5,4),(6,4)):
  gm=[];om=[];exactgm=[];exactom=[];mulshare=[]
  for b in bs:
   rr=[(k,v) for k,v in agg.items() if k[0]==b and k[1]==opt]
   cond=lambda k:k[6] and k[3]<=nin and k[4]<=nout
   # all-G_t backbone+interface: MUL timing deliberately deferred
   gm.append(frac(rr,cond));om.append(frac(rr,cond,True))
   nom=[(k,v) for k,v in rr if k[5]==0]
   exactgm.append(frac(nom,cond));exactom.append(frac(nom,cond,True))
   mulshare.append(frac(rr,lambda k:k[5]>0))
  print('STEP4D3_RESULT',opt,'in',nin,'out',nout,
        'all_backbone_group_med',f'{statistics.median(gm):.9f}','all_backbone_group_q1',f'{statistics.quantiles(gm,n=4)[0]:.9f}',
        'all_backbone_op_med',f'{statistics.median(om):.9f}','all_backbone_op_q1',f'{statistics.quantiles(om,n=4)[0]:.9f}',
        'nomul_exact_group_med',f'{statistics.median(exactgm):.9f}','nomul_exact_group_q1',f'{statistics.quantiles(exactgm,n=4)[0]:.9f}',
        'nomul_exact_op_med',f'{statistics.median(exactom):.9f}','nomul_exact_op_q1',f'{statistics.quantiles(exactom,n=4)[0]:.9f}',
        'mul_group_med',f'{statistics.median(mulshare):.9f}',flush=True)
print('STEP4D3_NOTE nomul_exact is joint K5-topology + interface realizability for MUL-free G_t; all_backbone removes MUL nodes and therefore is an upper structural indicator pending temporal MUL scheduling, not full-array realizability and not speedup.',flush=True)
print('STEP4D3_LIMITATION K5 endpoint representative is one Pareto-equivalent logical labeling; no physical routing, clock, memory, configuration overhead, or cycle model is included.',flush=True)
