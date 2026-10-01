#!/usr/bin/env python3
"""Scalable mining of recurrent topology-agnostic RAW templates from Embench RV32 traces.

Structural discovery only: this script does not estimate ATHENA mapping, cycles, or speedup.
Only strictly contiguous eligible ALU sequences are considered. Any non-eligible instruction
(including memory and control operations) closes the current structural region, preventing
windows from spanning intervening operations.

The implementation is streaming: it keeps only the last 12 eligible operations and aggregate
statistics per canonical template, rather than materializing every occurrence.
"""
import csv, glob, os, collections, json

RR={'add','sub','and','or','xor','sll','srl','sra','slt','sltu','mul','mulh','mulhu','mulhsu'}
RI={'addi','andi','ori','xori','slli','srli','srai','slti','sltiu'}
ELIGIBLE=RR|RI
MIN_N,MAX_N=4,12

def key_for(win):
    pos={n['idx']:i for i,n in enumerate(win)}
    return tuple((n['op'],tuple(sorted(pos[p] for p in n['deps'] if p in pos))) for n in win)

def metrics(key):
    depths=[]; succ=collections.Counter()
    for _,deps in key:
        depths.append(1+max((depths[p] for p in deps),default=0))
        for p in deps: succ[p]+=1
    width=max(collections.Counter(depths).values())
    joins=sum(len(d)>=2 for _,d in key)
    forks=sum(v>=2 for v in succ.values())
    return max(depths),width,joins,forks

# (opt,key) -> aggregate counters. last_end is kept separately per benchmark.
agg={}
last_end={}
trace_audit=[]

for path in sorted(glob.glob('embench-results/*_O*.trace.csv')):
    base=os.path.basename(path).replace('.trace.csv','')
    bench,opt=base.rsplit('_',1)
    window=collections.deque(maxlen=MAX_N)
    last_writer={}
    eligible_idx=0
    rows=0
    eligible_rows=0
    regions=0
    in_region=False

    with open(path,newline='') as f:
        for r in csv.DictReader(f):
            rows+=1
            op=r['op'].lower()
            args=[x.strip() for x in r['args'].split(',') if x.strip()]
            if op not in ELIGIBLE or len(args)<2:
                window.clear(); last_writer.clear(); in_region=False
                continue

            if not in_region:
                regions+=1; in_region=True
            d=args[0]
            src=args[1:3] if op in RR else args[1:2]
            deps=tuple(sorted({last_writer[s] for s in src if s!='zero' and s in last_writer}))
            node={'idx':eligible_idx,'op':op,'deps':deps}
            eligible_idx+=1; eligible_rows+=1
            window.append(node)
            if d!='zero': last_writer[d]=node['idx']

            wlist=list(window)
            upto=min(MAX_N,len(wlist))
            for n in range(MIN_N,upto+1):
                win=wlist[-n:]
                k=key_for(win)
                ak=(opt,k)
                rec=agg.get(ak)
                if rec is None:
                    rec=agg[ak]={'raw':0,'nonover':0,'benches':set()}
                rec['raw']+=1
                rec['benches'].add(bench)
                start,end=win[0]['idx'],win[-1]['idx']+1
                lk=(opt,k,bench)
                if start>=last_end.get(lk,-1):
                    rec['nonover']+=1
                    last_end[lk]=end

    trace_audit.append((base,rows,eligible_rows,regions))
    print('TRACE',base,'rows',rows,'eligible',eligible_rows,'regions',regions,flush=True)

records=[]
for (opt,k),rec in agg.items():
    n=len(k); depth,width,joins,forks=metrics(k)
    records.append({
        'opt':opt,'N':n,'raw_occurrences':rec['raw'],
        'nonoverlap_occurrences':rec['nonover'],
        'benchmark_prevalence':len(rec['benches']),
        'prevalence_fraction':len(rec['benches'])/19.0,
        'depth':depth,'max_width':width,'joins':joins,'forks':forks,
        'template':json.dumps(k,separators=(',',':'))
    })

records.sort(key=lambda r:(r['opt'],-r['benchmark_prevalence'],-r['nonoverlap_occurrences'],-r['N']))
os.makedirs('embench-results',exist_ok=True)
fields=list(records[0]) if records else ['opt','N','raw_occurrences','nonoverlap_occurrences',
    'benchmark_prevalence','prevalence_fraction','depth','max_width','joins','forks','template']
with open('embench-results/recurrent_templates.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(records)
with open('embench-results/trace_audit.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['trace','rows','eligible_alu_rows','strict_alu_regions']); w.writerows(trace_audit)

print('TEMPLATE_MINING_START')
for opt in ('O2','O3'):
    rr=[r for r in records if r['opt']==opt and r['nonoverlap_occurrences']>=2]
    print('OPT',opt,'templates',sum(r['opt']==opt for r in records),'recurrent_templates',len(rr))
    for r in rr[:25]:
        print('TEMPLATE',opt,'N',r['N'],'R_nonoverlap',r['nonoverlap_occurrences'],
              'R_raw',r['raw_occurrences'],'P',r['benchmark_prevalence'],'/19',
              'depth',r['depth'],'width',r['max_width'],'joins',r['joins'],'forks',r['forks'],
              r['template'])
print('TEMPLATE_MINING_END')
