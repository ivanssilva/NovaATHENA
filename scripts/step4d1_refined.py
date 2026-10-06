#!/usr/bin/env python3
"""Step 4D.1 refined: exact dynamic register use/def semantics and live-I/O CDFs
for the selected G_t(D=3,C=8) population. Structural evidence only.
"""
import csv,glob,os,re,collections,statistics
RR={'add','sub','and','or','xor','sll','srl','sra','slt','sltu','mul','mulh','mulhu','mulhsu','div','divu','rem','remu'}
RI={'addi','andi','ori','xori','slli','srli','srai','slti','sltiu'}
EL=RR|RI;D=3;C=8
ALIASES={'zero':'x0','ra':'x1','sp':'x2','gp':'x3','tp':'x4',
't0':'x5','t1':'x6','t2':'x7','s0':'x8','fp':'x8','s1':'x9',
'a0':'x10','a1':'x11','a2':'x12','a3':'x13','a4':'x14','a5':'x15','a6':'x16','a7':'x17',
's2':'x18','s3':'x19','s4':'x20','s5':'x21','s6':'x22','s7':'x23','s8':'x24','s9':'x25','s10':'x26','s11':'x27',
't3':'x28','t4':'x29','t5':'x30','t6':'x31'}
REG=re.compile(r'^(?:x(?:[12]?\d|3[01])|zero|ra|sp|gp|tp|t[0-6]|s(?:[0-9]|1[01])|fp|a[0-7])$')
def n(x):x=x.strip();return ALIASES.get(x,x)
def regs(x): return [n(z) for z in re.findall(r'\b(?:x(?:[12]?\d|3[01])|zero|ra|sp|gp|tp|t[0-6]|s(?:[0-9]|1[01])|fp|a[0-7])\b',x)]
def elig(op,a):
 if op not in EL or len(a)<2:return None
 return n(a[0]),[n(x) for x in (a[1:3] if op in RR else a[1:2])]
def usedef(op,a):
 """RV32I/M GNU/QEMU syntax register uses/defs relevant to future liveness."""
 A=[n(x) for x in a]
 if op in RR or op in RI:
  q=elig(op,A);return set(q[1]),({q[0]} if q[0]!='x0' else set())
 if op in {'lui','auipc'} and A:return set(),({A[0]} if A[0]!='x0' else set())
 if op in {'lb','lh','lw','lbu','lhu'} and A:
  u=set(regs(','.join(A[1:])));return u,({A[0]} if A[0]!='x0' else set())
 if op in {'sb','sh','sw'} and A:return set(regs(','.join(A))),set()
 if op in {'beq','bne','blt','bge','bltu','bgeu'}:return set(x for x in A[:2] if REG.match(x) and x!='x0'),set()
 if op=='jal' and A:
  # disassembly may omit rd; one-operand jal is pseudo jal ra,target
  if len(A)>=2 and REG.match(A[0]):return set(),({A[0]} if A[0]!='x0' else set())
  return set(),{'x1'}
 if op=='jalr' and A:
  d=A[0] if REG.match(A[0]) else 'x1';u=set(regs(','.join(A[1:] if REG.match(A[0]) else A)))
  return u,({d} if d!='x0' else set())
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
  d={A[0]} if REG.match(A[0]) and A[0]!='x0' else set()
  return u,d
 if op in {'ecall','ebreak','fence','fence.i','nop'}:return set(),set()
 # conservative fallback is explicit and audited
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
paths=sorted(glob.glob('embench-results/*_O*.trace.csv'));assert len(paths)==38
agg=collections.Counter();unknown=collections.Counter()
for pi,p in enumerate(paths,1):
 name=os.path.basename(p).replace('.trace.csv','');b,o=name.rsplit('_',1);rows=[]
 with open(p,newline='') as f:
  for r in csv.DictReader(f):
   op=r['op'].lower();a=[x.strip() for x in r['args'].split(',') if x.strip()];rows.append((op,a))
 # backward exact use-before-next-def liveness
 live=set();deflive=[False]*len(rows)
 for i in range(len(rows)-1,-1,-1):
  op,a=rows[i];u,d=usedef(op,a)
  q=elig(op,a)
  if q and q[0]!='x0':deflive[i]=q[0] in live
  live.difference_update(d);live.update(u)
  known=(op in RR or op in RI or op in {'lui','auipc','lb','lh','lw','lbu','lhu','sb','sh','sw','beq','bne','blt','bge','bltu','bgeu','jal','jalr','mv','not','neg','snez','seqz','bnez','beqz','bltz','bgez','blez','bgtz','bgt','ble','bgtu','bleu','j','ret','jr','csrrs','ecall','ebreak','fence','fence.i','nop'})
  if not known:unknown[(op,tuple(a))]+=1
 g=G();ng=[0]
 def flush():
  if not g.nodes:return
  last={}
  for reg,i in g.defs:last[reg]=i
  lo=sum(deflive[i] for i in last.values());agg[(b,o,len(g.nodes),len(g.ext),lo)]+=1;ng[0]+=1;g.reset()
 for i,(op,a) in enumerate(rows):
  q=elig(op,a)
  if q is None:flush();continue
  dst,src=q;ds,d=g.prospective(src)
  if g.nodes and (len(g.nodes)>=C or d>D):flush();ds,d=g.prospective(src)
  g.add(op,dst,src,ds,d,i)
 flush();print('STEP4D1R_TRACE',pi,'/',38,name,'groups',ng[0],flush=True)
with open('step4d1_refined_counts.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['benchmark','opt','ops','true_liveins','true_liveouts','occurrences'])
 for k,v in sorted(agg.items()):w.writerow([*k,v])
with open('step4d1_unknown_semantics.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['op','args','occurrences'])
 for (op,a),v in sorted(unknown.items(),key=lambda x:-x[1]):w.writerow([op,','.join(a),v])
print('STEP4D1R_AUDIT traces',len(paths),'pairs',len(set((b,o) for b,o,*_ in agg)),'unknown_occurrences',sum(unknown.values()),'unknown_forms',len(unknown),flush=True)
for opt in ('O2','O3'):
 bs=sorted(set(k[0] for k in agg if k[1]==opt))
 for metric,pos in [('liveins',3),('liveouts',4)]:
  print('STEP4D1R_CDF',opt,metric,end='')
  for cap in range(0,9):
   vals=[]
   for b in bs:
    rr=[(k,v) for k,v in agg.items() if k[0]==b and k[1]==opt];tot=sum(v for k,v in rr)
    vals.append(sum(v for k,v in rr if k[pos]<=cap)/tot)
   print(' cap'+str(cap)+'_median '+format(statistics.median(vals),'.9f'),end='')
  print(flush=True)
print('STEP4D1R_NOTE CDF values are benchmark-balanced medians of per-benchmark fractions, not pooled dynamic fractions.',flush=True)
