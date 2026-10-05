#!/usr/bin/env python3
"""Step 4D.1: reconstruct true register live-ins/live-outs for selected G_t(D=3,C=8).
A live-in is a source whose reaching definition is outside the candidate.
A true live-out is a candidate definition whose value is consumed later before
being overwritten. x0/zero is excluded. Structural analysis; no cycle claim.
"""
import csv,glob,os,re,collections,statistics
RR={'add','sub','and','or','xor','sll','srl','sra','slt','sltu','mul','mulh','mulhu','mulhsu'}
RI={'addi','andi','ori','xori','slli','srli','srai','slti','sltiu'}
EL=RR|RI; D=3; C=8
def oa(op,args):
 if len(args)<2:return None
 return args[0],(args[1:3] if op in RR else args[1:2])
def norm(r): return 'zero' if r in ('x0','zero') else r
class G:
 def __init__(self):self.reset()
 def reset(self):self.nodes=[];self.w={};self.dep=[];self.ext=set();self.defseq=[]
 def prospective(self,src):
  ds=tuple(sorted(set(self.w[s] for s in src if s!='zero' and s in self.w)))
  return ds,1+max((self.dep[i] for i in ds),default=0)
 def add(self,op,dst,src,ds,d,seq):
  for x in src:
   if x!='zero' and x not in self.w:self.ext.add(x)
  i=len(self.nodes);self.nodes.append((op,ds));self.dep.append(d);self.defseq.append((norm(dst),seq))
  if dst!='zero':self.w[dst]=i
def later_use_map(rows):
 # next event for each register scanning backwards: True means next relevant event is read, False overwrite
 live=[False]*len(rows); state={}
 for idx in range(len(rows)-1,-1,-1):
  op,args,seq=rows[idx];o=oa(op,args) if op in EL else None
  # include reads/writes from broad RISC-V syntax conservatively: for eligible defs exact;
  # for all instructions, sources are all register tokens except first token when likely destination.
  regs=[norm(x) for x in re.findall(r'\b(?:x(?:[12]?\d|3[01])|zero|ra|sp|gp|tp|t[0-6]|s(?:[0-9]|1[01])|a[0-7])\b',','.join(args))]
  if o:
   dst=norm(o[0]); src=[norm(x) for x in o[1]]
   live[idx]=dst!='zero' and state.get(dst,False)
   if dst!='zero':state[dst]=False
   for x in src:
    if x!='zero':state[x]=True
  else:
   # conservative noneligible treatment: mark referenced registers as future reads;
   # this cannot identify a destination generically, so barriers end G_t and any mention after it preserves liveness.
   for x in regs:
    if x!='zero':state[x]=True
 return live
paths=sorted(glob.glob('embench-results/*_O*.trace.csv'));assert len(paths)==38
out=[];dist=collections.Counter()
for pi,p in enumerate(paths,1):
 name=os.path.basename(p).replace('.trace.csv','');bench,opt=name.rsplit('_',1)
 rows=[]
 with open(p,newline='') as f:
  for r in csv.DictReader(f):
   op=r['op'].lower();args=[norm(x.strip()) for x in r['args'].split(',') if x.strip()]
   rows.append((op,args,int(r['seq'])))
 lv=later_use_map(rows);g=G();groups=[]
 def flush():
  if not g.nodes:return
  lo=sum(1 for reg,seq in g.defseq if reg!='zero' and lv[seq])
  # multiple defs of same architectural reg inside group: only last reaching def can be live-out
  last={}
  for reg,seq in g.defseq:
   if reg!='zero':last[reg]=seq
  lo=sum(1 for reg,seq in last.items() if lv[seq])
  groups.append((len(g.nodes),len(g.ext),lo));g.reset()
 for idx,(op,args,seq) in enumerate(rows):
  o=oa(op,args) if op in EL else None
  if o is None:flush();continue
  dst,src=o;ds,d=g.prospective(src)
  if g.nodes and (len(g.nodes)>=C or d>D):flush();ds,d=g.prospective(src)
  g.add(op,dst,src,ds,d,seq)
 flush()
 for ops,li,lo in groups:dist[(bench,opt,ops,li,lo)]+=1
 print('STEP4D1_TRACE',pi,'/',len(paths),name,'groups',len(groups),flush=True)
with open('step4d1_liveio_counts.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['benchmark','opt','ops','true_liveins','true_liveouts','occurrences'])
 for k,n in sorted(dist.items()):w.writerow([*k,n])
print('STEP4D1_AUDIT traces',len(paths),'pairs',len(set((b,o) for b,o,*_ in dist)),flush=True)
for opt in ('O2','O3'):
 vals_in=[];vals_out=[];allg=0
 for b in sorted(set(k[0] for k in dist if k[1]==opt)):
  rows=[(k,n) for k,n in dist.items() if k[0]==b and k[1]==opt];tot=sum(n for k,n in rows)
  vals_in.append(sum(k[3]*n for k,n in rows)/tot);vals_out.append(sum(k[4]*n for k,n in rows)/tot);allg+=tot
 def q(v,p):return statistics.quantiles(v,n=4,method='inclusive')[p-1]
 print('STEP4D1_SUMMARY',opt,'groups',allg,'mean_liveins_per_group_median',statistics.median(vals_in),'Q1',q(vals_in,1),'Q3',q(vals_in,3),'mean_liveouts_per_group_median',statistics.median(vals_out),'Q1',q(vals_out,1),'Q3',q(vals_out,3),flush=True)
print('STEP4D1_LIMITATION true live-out tracking is register-level dynamic future-use analysis; noneligible instructions are conservative read barriers because generic destination semantics are not decoded; memory/control semantics require later temporal modeling.',flush=True)
