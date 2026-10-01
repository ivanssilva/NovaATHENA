#!/usr/bin/env python3
"""Streaming extraction of timing-neutral candidate G_t descriptors.

The extractor emits sensitivity families D={1,2,3}, where D is maximum internal
RAW dependency depth. D is NOT asserted to fit one hardware cycle; later synthesis
must establish timing feasibility.

Non-eligible instructions terminate strict ALU regions. Each family greedily
partitions each region in dynamic order. State is updated incrementally, avoiding
quadratic re-summarization and avoiding materializing complete traces/regions.
"""
import csv,glob,os,collections,json

RR={'add','sub','and','or','xor','sll','srl','sra','slt','sltu','mul','mulh','mulhu','mulhsu'}
RI={'addi','andi','ori','xori','slli','srli','srai','slti','sltiu'}
ELIGIBLE=RR|RI
DEPTHS=(1,2,3)
FIELDS=['ops','depth','max_width','joins','forks','external_inputs','live_outputs','mul_ops','signature']

def operands(op,args):
    if len(args)<2: return None
    return args[0], (args[1:3] if op in RR else args[1:2])

class Group:
    def __init__(self,D):
        self.D=D; self.reset()
    def reset(self):
        self.nodes=[]; self.writers={}; self.depths=[]; self.width=collections.Counter()
        self.ext=set(); self.used=set(); self.succ=collections.Counter(); self.mul=0
    def empty(self): return not self.nodes
    def prospective(self,dst,src):
        deps=[]
        for s in src:
            if s!='zero' and s in self.writers: deps.append(self.writers[s])
        deps=tuple(sorted(set(deps)))
        dep=1+max((self.depths[p] for p in deps),default=0)
        return deps,dep
    def add(self,op,dst,src,deps,dep):
        i=len(self.nodes)
        for s in src:
            if s=='zero': continue
            if s not in self.writers: self.ext.add(s)
        for p in deps: self.used.add(p); self.succ[p]+=1
        self.nodes.append((op,deps)); self.depths.append(dep); self.width[dep]+=1
        if dst!='zero': self.writers[dst]=i
        if op.startswith('mul'): self.mul+=1
    def row(self):
        live=sum(1 for i,(op,deps) in enumerate(self.nodes) if i not in self.used)
        return {'ops':len(self.nodes),'depth':max(self.depths,default=0),
          'max_width':max(self.width.values(),default=0),
          'joins':sum(len(deps)>=2 for op,deps in self.nodes),
          'forks':sum(v>=2 for v in self.succ.values()),
          'external_inputs':len(self.ext),'live_outputs':live,'mul_ops':self.mul,
          'signature':json.dumps(self.nodes,separators=(',',':'))}

os.makedirs('embench-results/gt',exist_ok=True)
aggregate=collections.Counter(); audit=[]
paths=sorted(glob.glob('embench-results/*_O*.trace.csv'))
for ti,path in enumerate(paths,1):
    name=os.path.basename(path).replace('.trace.csv',''); opt=name.rsplit('_',1)[1]
    outs={}; writers={}; groups={D:Group(D) for D in DEPTHS}
    stats={D:{'regions':0,'groups':0,'ops':0,'max':0,'in_region':False} for D in DEPTHS}
    try:
        for D in DEPTHS:
            fp=open(f'embench-results/gt/{name}_D{D}.gt.csv','w',newline='')
            w=csv.DictWriter(fp,fieldnames=FIELDS); w.writeheader(); outs[D]=(fp,w)
        def flush(D):
            g=groups[D]
            if g.empty(): return
            row=g.row(); outs[D][1].writerow(row)
            st=stats[D]; st['groups']+=1; st['ops']+=row['ops']; st['max']=max(st['max'],row['ops'])
            aggregate[(opt,D,row['signature'])]+=1; g.reset()
        with open(path,newline='') as f:
            for r in csv.DictReader(f):
                op=r['op'].lower(); args=[x.strip() for x in r['args'].split(',') if x.strip()]
                o=operands(op,args) if op in ELIGIBLE else None
                if o is None:
                    for D in DEPTHS:
                        flush(D); stats[D]['in_region']=False
                    continue
                dst,src=o
                for D in DEPTHS:
                    st=stats[D]
                    if not st['in_region']: st['regions']+=1; st['in_region']=True
                    g=groups[D]; deps,dep=g.prospective(dst,src)
                    if not g.empty() and dep>D:
                        flush(D); g=groups[D]; deps,dep=g.prospective(dst,src)
                    g.add(op,dst,src,deps,dep)
        for D in DEPTHS: flush(D)
    finally:
        for fp,w in outs.values(): fp.close()
    for D in DEPTHS:
        st=stats[D]; audit.append((name,D,st['regions'],st['groups'],st['ops'],st['max']))
    print('GT_TRACE',ti,'/',len(paths),name,
          ' '.join(f"D{D}:g={stats[D]['groups']},ops={stats[D]['ops']},max={stats[D]['max']}" for D in DEPTHS),flush=True)

with open('embench-results/gt_audit.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['trace','D','strict_regions','candidate_Gt','covered_alu_ops','max_group_ops']); w.writerows(audit)
with open('embench-results/gt_signature_counts.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['opt','D','signature','occurrences'])
    for (opt,D,sig),n in sorted(aggregate.items(),key=lambda x:(x[0][0],x[0][1],-x[1])):
        w.writerow([opt,D,sig,n])
print('GT_EXTRACTION_START')
for D in DEPTHS:
    rows=[r for r in audit if r[1]==D]
    print('GT_AUDIT D',D,'traces',len(rows),'groups',sum(r[3] for r in rows),
          'covered_alu_ops',sum(r[4] for r in rows),'max_group_ops',max(r[5] for r in rows))
print('GT_EXTRACTION_END')
