#!/usr/bin/env python3
"""Mine recurrent topology-agnostic RAW templates from Embench RV32 traces.
This is structural discovery, not ATHENA mapping, cycle count, or speedup.
Templates are contiguous eligible-ALU windows inside control-flow regions.
Canonical key preserves opcode sequence and internal RAW predecessor positions.
Reports raw occurrences, greedy non-overlapping occurrences, benchmark prevalence,
depth, width, joins/forks, and hypothetical occupancy for 8/10/12 ALUs.
"""
import csv,glob,os,collections,json
RR={'add','sub','and','or','xor','sll','srl','sra','slt','sltu','mul','mulh','mulhu','mulhsu'}
RI={'addi','andi','ori','xori','slli','srli','srai','slti','sltiu'}
BOUND={'beq','bne','blt','bge','bltu','bgeu','jal','jalr','ecall','ebreak'}
SIZES=range(4,13)

def parse(path):
    groups=[]; cur=[]; last={}
    for r in csv.DictReader(open(path)):
        op=r['op'].lower(); a=[x.strip() for x in r['args'].split(',')]
        if op in BOUND:
            if cur: groups.append(cur)
            cur=[]; last={}; continue
        if op not in RR|RI or len(a)<2: continue
        d=a[0]; src=a[1:3] if op in RR else a[1:2]
        deps=tuple(sorted({last[s] for s in src if s!='zero' and s in last}))
        idx=sum(map(len,groups))+len(cur)
        cur.append({'gidx':idx,'op':op,'deps':deps,'seq':int(r['seq']),'pc':r['pc']})
        if d!='zero': last[d]=idx
    if cur: groups.append(cur)
    return groups

def key_for(win):
    pos={n['gidx']:i for i,n in enumerate(win)}
    return tuple((n['op'],tuple(sorted(pos[p] for p in n['deps'] if p in pos))) for n in win)

def metrics(key):
    depths=[]; succ=collections.Counter()
    for i,(_,deps) in enumerate(key):
        depths.append(1+max((depths[p] for p in deps),default=0))
        for p in deps: succ[p]+=1
    width=max(collections.Counter(depths).values())
    joins=sum(len(d)>=2 for _,d in key)
    forks=sum(v>=2 for v in succ.values())
    return max(depths),width,joins,forks

records=[]
perbench=collections.defaultdict(lambda:collections.defaultdict(list))
for path in sorted(glob.glob('embench-results/*_O*.trace.csv')):
    base=os.path.basename(path).replace('.trace.csv','')
    bench,opt=base.rsplit('_',1)
    groups=parse(path)
    for gi,g in enumerate(groups):
        for n in SIZES:
            for s in range(0,len(g)-n+1):
                win=g[s:s+n]; k=key_for(win)
                perbench[(opt,k)][bench].append((gi,s,s+n,win[0]['seq'],win[-1]['seq']))

for (opt,k),bm in perbench.items():
    raw=sum(len(v) for v in bm.values())
    nonover=0
    for bench,occ in bm.items():
        bygroup=collections.defaultdict(list)
        for x in occ: bygroup[x[0]].append(x)
        for xs in bygroup.values():
            end=-1
            for x in sorted(xs,key=lambda z:(z[1],z[2])):
                if x[1]>=end: nonover+=1; end=x[2]
    n=len(k); depth,width,joins,forks=metrics(k)
    records.append({'opt':opt,'N':n,'raw_occurrences':raw,'nonoverlap_occurrences':nonover,
      'benchmark_prevalence':len(bm),'prevalence_fraction':len(bm)/19.0,
      'depth':depth,'max_width':width,'joins':joins,'forks':forks,
      'occ8':min(1,n/8),'idle8':max(0,1-n/8),
      'occ10':min(1,n/10),'idle10':max(0,1-n/10),
      'occ12':n/12,'idle12':1-n/12,
      'template':json.dumps(k,separators=(',',':'))})

records.sort(key=lambda r:(r['opt'],-r['benchmark_prevalence'],-r['nonoverlap_occurrences'],-r['N']))
os.makedirs('embench-results',exist_ok=True)
fields=list(records[0]) if records else []
with open('embench-results/recurrent_templates.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(records)
print('TEMPLATE_MINING_START')
for opt in ('O2','O3'):
    rr=[r for r in records if r['opt']==opt and r['nonoverlap_occurrences']>=2]
    print('OPT',opt,'recurrent_templates',len(rr))
    for r in rr[:25]:
        print('TEMPLATE',opt,'N',r['N'],'R_nonoverlap',r['nonoverlap_occurrences'],
          'R_raw',r['raw_occurrences'],'P',r['benchmark_prevalence'],'/19',
          'depth',r['depth'],'width',r['max_width'],'joins',r['joins'],'forks',r['forks'],
          'idle12',round(100*r['idle12'],1),'%',r['template'])
print('TEMPLATE_MINING_END')
