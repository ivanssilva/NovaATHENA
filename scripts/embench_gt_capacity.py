#!/usr/bin/env python3
"""Capacity-sensitivity extraction for ATHENA candidate G_t families.

This substage constrains the already timing-neutral families by two orthogonal
structural limits: maximum internal RAW depth D and maximum operations per
candidate C. C is a sensitivity parameter, not a proposed PE size.

The output is intended to support later heterogeneous-PE selection and topology
inference. No row is a cycle count or speedup claim.
"""
import csv,glob,os,collections,json,re

RR={'add','sub','and','or','xor','sll','srl','sra','slt','sltu','mul','mulh','mulhu','mulhsu'}
RI={'addi','andi','ori','xori','slli','srli','srai','slti','sltiu'}
ELIGIBLE=RR|RI
DEPTHS=(1,2,3)
CAPS=(4,6,8,12)
FIELDS=['ops','depth','max_width','joins','forks','external_inputs','unconsumed_defs','mul_ops','signature']

def operands(op,args):
    if len(args)<2:return None
    return args[0],(args[1:3] if op in RR else args[1:2])

class Group:
    def __init__(self,D,C): self.D=D;self.C=C;self.reset()
    def reset(self):
        self.nodes=[];self.writers={};self.depths=[];self.width=collections.Counter()
        self.ext=set();self.used=set();self.succ=collections.Counter();self.mul=0;self.defines=[]
    def empty(self):return not self.nodes
    def prospective(self,src):
        deps=tuple(sorted(set(self.writers[s] for s in src if s!='zero' and s in self.writers)))
        dep=1+max((self.depths[p] for p in deps),default=0)
        return deps,dep
    def can_add(self,dep):return len(self.nodes)<self.C and dep<=self.D
    def add(self,op,dst,src,deps,dep):
        i=len(self.nodes)
        for s in src:
            if s!='zero' and s not in self.writers:self.ext.add(s)
        for p in deps:self.used.add(p);self.succ[p]+=1
        self.nodes.append((op,deps));self.depths.append(dep);self.width[dep]+=1
        self.defines.append(dst!='zero')
        if dst!='zero':self.writers[dst]=i
        if op.startswith('mul'):self.mul+=1
    def row(self):
        return {'ops':len(self.nodes),'depth':max(self.depths,default=0),
          'max_width':max(self.width.values(),default=0),
          'joins':sum(len(d)>=2 for _,d in self.nodes),
          'forks':sum(v>=2 for v in self.succ.values()),
          'external_inputs':len(self.ext),
          'unconsumed_defs':sum(1 for i,_ in enumerate(self.nodes) if self.defines[i] and i not in self.used),
          'mul_ops':self.mul,
          'signature':json.dumps(self.nodes,separators=(',',':'))}

paths=sorted(glob.glob('embench-results/*_O*.trace.csv'))
assert len(paths)==38,len(paths)
pairs=collections.defaultdict(set)
for p in paths:
    m=re.match(r'(.+)_O([23])\.trace\.csv$',os.path.basename(p));assert m,p
    pairs[m.group(1)].add(m.group(2))
assert len(pairs)==19 and all(v=={'2','3'} for v in pairs.values()),pairs

os.makedirs('embench-results/gt_capacity',exist_ok=True)
audit=[];aggregate=collections.Counter();bench_aggregate=collections.Counter();descriptor_aggregate=collections.Counter();opfreq=collections.Counter()
for ti,path in enumerate(paths,1):
    name=os.path.basename(path).replace('.trace.csv','');benchmark,opt=name.rsplit('_',1)
    keys=[(D,C) for D in DEPTHS for C in CAPS]
    groups={k:Group(*k) for k in keys};outs={};stats={k:[0,0,0,0] for k in keys} # regions,groups,ops,max
    try:
        for k in keys:
            D,C=k;fp=open(f'embench-results/gt_capacity/{name}_D{D}_C{C}.csv','w',newline='')
            w=csv.DictWriter(fp,fieldnames=FIELDS);w.writeheader();outs[k]=(fp,w)
        def flush(k):
            g=groups[k]
            if g.empty():return
            row=g.row();outs[k][1].writerow(row);st=stats[k]
            st[1]+=1;st[2]+=row['ops'];st[3]=max(st[3],row['ops'])
            aggregate[(opt,k[0],k[1],row['signature'])]+=1
            bench_aggregate[(benchmark,opt,k[0],k[1],row['signature'])]+=1
            descriptor_aggregate[(benchmark,opt,k[0],k[1],row['ops'],row['depth'],row['max_width'],row['joins'],row['forks'],row['external_inputs'],row['unconsumed_defs'],row['mul_ops'])]+=1
            g.reset()
        in_region=False
        with open(path,newline='') as f:
            for r in csv.DictReader(f):
                op=r['op'].lower();args=[x.strip() for x in r['args'].split(',') if x.strip()]
                opfreq[(name,op,1 if op in ELIGIBLE else 0)]+=1
                o=operands(op,args) if op in ELIGIBLE else None
                if o is None:
                    for k in keys:flush(k)
                    in_region=False;continue
                if not in_region:
                    for k in keys:stats[k][0]+=1
                    in_region=True
                dst,src=o
                for k in keys:
                    g=groups[k];deps,dep=g.prospective(src)
                    if not g.empty() and not g.can_add(dep):
                        flush(k);g=groups[k];deps,dep=g.prospective(src)
                    g.add(op,dst,src,deps,dep)
        for k in keys:flush(k)
    finally:
        for fp,w in outs.values():fp.close()
    for D,C in keys:
        st=stats[(D,C)];audit.append((name,D,C,*st))
    print('GTC_TRACE',ti,'/',len(paths),name,flush=True)

with open('embench-results/gt_capacity_audit.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow(['trace','D','C','strict_regions','candidate_Gt','covered_alu_ops','max_group_ops']);w.writerows(audit)
with open('embench-results/gt_capacity_signature_counts.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow(['opt','D','C','signature','occurrences'])
    for (opt,D,C,sig),n in sorted(aggregate.items(),key=lambda x:(x[0][0],x[0][1],x[0][2],-x[1])):
        w.writerow([opt,D,C,sig,n])
with open('embench-results/gt_capacity_benchmark_signature_counts.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow(['benchmark','opt','D','C','signature','occurrences'])
    for k,n in sorted(bench_aggregate.items(),key=lambda x:(x[0][0],x[0][1],x[0][2],x[0][3],-x[1])):w.writerow([*k,n])
with open('embench-results/gt_capacity_descriptor_counts.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow(['benchmark','opt','D','C','ops','depth','max_width','joins','forks','external_inputs','unconsumed_defs','mul_ops','occurrences'])
    for k,n in sorted(descriptor_aggregate.items()):w.writerow([*k,n])
with open('embench-results/gt_operation_coverage.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow(['trace','op','eligible_alu','occurrences'])
    for k,n in sorted(opfreq.items()):w.writerow([*k,n])

print('GTC_AUDIT_START')
for D in DEPTHS:
  for C in CAPS:
    r=[x for x in audit if x[1]==D and x[2]==C]
    print('GTC_AUDIT D',D,'C',C,'traces',len(r),'groups',sum(x[4] for x in r),
          'covered',sum(x[5] for x in r),'max',max(x[6] for x in r))
print('GTC_AUDIT_END')
