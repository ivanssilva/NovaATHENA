#!/usr/bin/env python3
"""Derive timing-neutral candidate G_t descriptors from validated Embench traces.

This is the first G_t extraction stage. It does NOT assume that dependency depth equals
one hardware cycle. Instead it emits sensitivity families for maximum internal RAW depth
D={1,2,3}. Timing synthesis will later decide which D values/operation combinations can
actually fit the ATHENA target period.

A candidate starts at each strict ALU region boundary or immediately after the previous
candidate. Non-eligible instructions terminate a region. For each D, operations are added
in dynamic order while their internal ASAP dependency depth is <=D. External inputs and
live outputs are conservatively described from register reads/writes inside the candidate.
"""
import csv,glob,os,collections,json

RR={'add','sub','and','or','xor','sll','srl','sra','slt','sltu','mul','mulh','mulhu','mulhsu'}
RI={'addi','andi','ori','xori','slli','srli','srai','slti','sltiu'}
ELIGIBLE=RR|RI
DEPTHS=(1,2,3)

def operands(op,args):
    if len(args)<2: return None
    dst=args[0]
    src=args[1:3] if op in RR else args[1:2]
    return dst,src

def summarize(nodes):
    writers={}
    depth=[]
    ext=set()
    used_internal=set()
    succ=collections.Counter()
    for i,n in enumerate(nodes):
        deps=[]
        for s in n['src']:
            if s=='zero': continue
            if s in writers:
                p=writers[s]; deps.append(p); used_internal.add(p); succ[p]+=1
            else: ext.add(s)
        d=1+max((depth[p] for p in deps),default=0)
        depth.append(d)
        if n['dst']!='zero': writers[n['dst']]=i
        n['deps']=tuple(sorted(set(deps)))
    live=[i for i,n in enumerate(nodes) if n['dst']!='zero' and i not in used_internal]
    return {
      'ops':len(nodes),'depth':max(depth,default=0),
      'max_width':max(collections.Counter(depth).values(),default=0),
      'joins':sum(len(n['deps'])>=2 for n in nodes),
      'forks':sum(v>=2 for v in succ.values()),
      'external_inputs':len(ext),'live_outputs':len(live),
      'mul_ops':sum(n['op'].startswith('mul') for n in nodes),
      'signature':json.dumps([(n['op'],n['deps']) for n in nodes],separators=(',',':'))
    }

def partition(region,D):
    out=[]; cur=[]
    for raw in region:
        trial=[dict(x) for x in cur+[raw]]
        s=summarize(trial)
        if cur and s['depth']>D:
            fixed=[dict(x) for x in cur]; out.append(summarize(fixed))
            cur=[raw]
        else:
            cur.append(raw)
    if cur:
        fixed=[dict(x) for x in cur]; out.append(summarize(fixed))
    return out

os.makedirs('embench-results/gt',exist_ok=True)
aggregate=collections.Counter()
audit=[]
for path in sorted(glob.glob('embench-results/*_O*.trace.csv')):
    name=os.path.basename(path).replace('.trace.csv','')
    regions=[]; region=[]
    with open(path,newline='') as f:
        for r in csv.DictReader(f):
            op=r['op'].lower(); args=[x.strip() for x in r['args'].split(',') if x.strip()]
            o=operands(op,args) if op in ELIGIBLE else None
            if o is None:
                if region: regions.append(region); region=[]
                continue
            dst,src=o; region.append({'op':op,'dst':dst,'src':src})
    if region: regions.append(region)

    for D in DEPTHS:
        groups=[]
        for reg in regions: groups.extend(partition(reg,D))
        outpath=f'embench-results/gt/{name}_D{D}.gt.csv'
        fields=['ops','depth','max_width','joins','forks','external_inputs','live_outputs','mul_ops','signature']
        with open(outpath,'w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(groups)
        ops=sum(g['ops'] for g in groups)
        audit.append((name,D,len(regions),len(groups),ops,max((g['ops'] for g in groups),default=0)))
        for g in groups:
            aggregate[(name.rsplit('_',1)[1],D,g['signature'])]+=1

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
