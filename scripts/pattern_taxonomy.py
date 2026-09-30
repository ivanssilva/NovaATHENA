#!/usr/bin/env python3
"""Dependency-motif taxonomy for ATHENA dynamic RV32 traces.
Descriptive graph analysis only: it does not estimate cycles or speedup.
Control-flow boundaries match dynamic_mapper.py. Eligible ALU set also matches it.
"""
import csv,glob,os,collections
os.makedirs("dynamic-results",exist_ok=True)
rr={'add','sub','and','or','xor','sll','srl','sra','slt','sltu'}
ri={'addi','andi','ori','xori','slli','srli','srai','slti','sltiu'}
branches={'beq','bne','blt','bge','bltu','bgeu','jal','jalr','ecall','ebreak'}

def parse(path):
    rows=list(csv.DictReader(open(path)))
    last={}; nodes=[]; groups=[]; current=[]
    for r in rows:
        op=r['op'].lower(); parts=[p.strip() for p in r['args'].split(',')]
        if op in branches:
            if current: groups.append(current); current=[]
            last={}; continue
        if op not in rr|ri or len(parts)<3: continue
        dest=parts[0]; sources=parts[1:3] if op in rr else parts[1:2]
        deps=set(last[s] for s in sources if s!='zero' and s in last)
        idx=len(nodes)
        depth=1+max((nodes[p]['depth'] for p in deps),default=0)
        node={'idx':idx,'deps':deps,'depth':depth,'op':op,'seq':int(r['seq']),'pc':r['pc']}
        nodes.append(node); current.append(node)
        if dest!='zero': last[dest]=idx
    if current: groups.append(current)
    return rows,nodes,groups

def analyze(nodes,groups,window=16):
    by={n['idx']:n for n in nodes}
    succ=collections.defaultdict(set)
    for n in nodes:
        for p in n['deps']: succ[p].add(n['idx'])
    conv2=[n for n in nodes if len(n['deps'])==2]
    conv3=[n for n in nodes if len(n['deps'])>=3]
    divergent=[n for n in nodes if len(succ[n['idx']])>=2]
    chain3=[n for n in nodes if n['depth']>=3]
    # diamond: p diverges to at least two direct children that reconverge at c.
    diamond=set()
    for c in conv2:
        ps=list(c['deps'])
        # Classic diamond detected one level earlier: common parent of the two producers.
        common=set(by[ps[0]]['deps']) & set(by[ps[1]]['deps'])
        if common: diamond.add(c['idx'])
    # Convergence whose two producers are themselves mutually independent.
    conv2_ready=0
    for c in conv2:
        p,q=list(c['deps'])
        if p not in by[q]['deps'] and q not in by[p]['deps']: conv2_ready+=1
    # Fixed 16-eligible-op windows, reset at control boundaries: >1 convergence
    # is a pressure indicator for the single-1F resource, not a packing proof.
    multi_windows=0; max_conv=0; windows=0
    for g in groups:
        for i in range(0,len(g),window):
            chunk=g[i:i+window]; ids={n['idx'] for n in chunk}
            k=sum(1 for n in chunk if len(n['deps'] & ids)==2)
            windows+=1; max_conv=max(max_conv,k)
            if k>=2: multi_windows+=1
    return dict(conv2=len(conv2),conv2_independent_producers=conv2_ready,
                conv3plus=len(conv3),divergent=len(divergent),depth_ge3=len(chain3),
                diamonds=len(diamond),windows16=windows,multi_conv_windows16=multi_windows,
                max_convergences_in_window16=max_conv)

out=[]
for path in sorted(glob.glob('dynamic-results/*.trace.csv')):
    rows,nodes,groups=parse(path); m=analyze(nodes,groups)
    out.append(dict(kernel=os.path.basename(path).replace('.trace.csv',''),
                    executed=len(rows),eligible=len(nodes),**m))
with open('dynamic-results/pattern_taxonomy.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print('PATTERN_TAXONOMY_START')
for opt in ('O0','O2','O3'):
    ss=[r for r in out if r['kernel'].endswith('_'+opt)]
    print('PATTERN_SUMMARY',opt,'n',len(ss),
          'eligible',sum(r['eligible'] for r in ss),
          'conv2',sum(r['conv2'] for r in ss),
          'conv2_indep',sum(r['conv2_independent_producers'] for r in ss),
          'conv3plus',sum(r['conv3plus'] for r in ss),
          'divergent',sum(r['divergent'] for r in ss),
          'depth3',sum(r['depth_ge3'] for r in ss),
          'diamonds',sum(r['diamonds'] for r in ss),
          'multi_conv_win16',sum(r['multi_conv_windows16'] for r in ss),
          'max_conv_win16',max(r['max_convergences_in_window16'] for r in ss))
print('PATTERN_FAMILY_O2_START')
for fam in sorted({r['kernel'].split('_v')[0] for r in out}):
    ss=[r for r in out if r['kernel'].startswith(fam+'_') and r['kernel'].endswith('_O2')]
    print('PATTERN_FAMILY',fam,
          'eligible',sum(r['eligible'] for r in ss),
          'conv2',sum(r['conv2'] for r in ss),
          'conv2_indep',sum(r['conv2_independent_producers'] for r in ss),
          'depth3',sum(r['depth_ge3'] for r in ss),
          'diamonds',sum(r['diamonds'] for r in ss),
          'multi_conv_win16',sum(r['multi_conv_windows16'] for r in ss),
          'max_conv_win16',max(r['max_convergences_in_window16'] for r in ss))
print('PATTERN_TAXONOMY_END')
