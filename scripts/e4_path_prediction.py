#!/usr/bin/env python3
"""E4 closed: causal last-observed path prediction, NOT configuration preparation.
Fixed 38 Embench dynamic RV32IM traces; BB windows k=2,4,8.
At the FIRST BB of each nonoverlapping window, predict full sequence of BB entry PCs
using only a previously completed window with the same entry PC.
A full-path hit requires all future BB entry PCs to match.
No oracle, no timing, no CFG, no K5 mapping or speedup.
"""
import csv,glob,hashlib,json,collections
from pathlib import Path
BR={'beq','bne','blt','bge','bltu','bgeu','jal','jalr','j','jr','ret','call','tail','c.j','c.jal','c.jr','c.jalr','c.beqz','c.bnez','ecall','ebreak','mret','sret'}
KS=(2,4,8)
paths=sorted(set(glob.glob('structural/*_O*.trace.csv')+glob.glob('structural/**/*.trace.csv',recursive=True)))
assert len(paths)==38,len(paths)
Path('e4-results').mkdir(exist_ok=True)
out=[];audits=[]
for path in paths:
 name=Path(path).name.removesuffix('.trace.csv');b,opt=name.rsplit('_',1)
 stats={k:collections.Counter() for k in KS};prior={k:{} for k in KS};pending={k:[] for k in KS}
 prev=None;bbstart=None;rows=0;blocks=0
 def finish():
  global blocks
  if bbstart is None:return
  blocks+=1
  for k in KS:
   q=pending[k];q.append(bbstart)
   if len(q)==k:
    s=stats[k];s['windows']+=1;entry=q[0];actual=tuple(q[1:])
    old=prior[k].get(entry)
    if old is None:s['cold']+=1
    else:
     s['predicted']+=1
     if old==actual:s['hits']+=1
     else:s['misses']+=1
     for i,(x,y) in enumerate(zip(old,actual)):
      if x==y:s['matching_positions']+=1
      else:break
    prior[k][entry]=actual
    q.clear()
 with open(path,newline='') as f:
  reader=csv.DictReader(f);assert {'pc','op','args'}.issubset(reader.fieldnames)
  for r in reader:
   rows+=1;pc=int(r['pc'],0)
   if prev is not None and (prev['op'].lower().strip() in BR or pc!=int(prev['pc'],0)+4):
    finish();bbstart=None
   if bbstart is None:bbstart=pc
   prev=r
 finish()
 for k in KS:
  q=pending[k]
  if q:stats[k]['incomplete_tail_BBs']=len(q)
  s=stats[k]
  assert s['windows']*k+s['incomplete_tail_BBs']==blocks
  assert s['predicted']+s['cold']==s['windows']
  assert s['hits']+s['misses']==s['predicted']
  out.append(dict(benchmark=b,opt=opt,group_BBs=k,dynamic_BBs=blocks,windows=s['windows'],cold=s['cold'],predicted=s['predicted'],hits=s['hits'],misses=s['misses'],matching_positions=s['matching_positions'],incomplete_tail_BBs=s['incomplete_tail_BBs'],full_path_hit_rate=round(s['hits']/s['predicted'],9) if s['predicted'] else 0,coverage=round(s['predicted']/s['windows'],9) if s['windows'] else 0))
 audits.append(dict(trace=name,sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),instructions=rows,blocks=blocks))
 print('E4_TRACE',name,'BBs',blocks,'k8',stats[8]['hits'],'/',stats[8]['predicted'],flush=True)
with open('e4-results/e4_per_trace.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
with open('e4-results/e4_aggregate.csv','w',newline='') as f:
 fields=['opt','group_BBs','windows','cold','predicted','hits','misses','coverage','full_path_hit_rate']
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for opt in ('O2','O3'):
  for k in KS:
   rr=[r for r in out if r['opt']==opt and r['group_BBs']==k]
   s={key:sum(r[key] for r in rr) for key in ('windows','cold','predicted','hits','misses')}
   w.writerow(dict(opt=opt,group_BBs=k,**s,coverage=round(s['predicted']/s['windows'],9) if s['windows'] else 0,full_path_hit_rate=round(s['hits']/s['predicted'],9) if s['predicted'] else 0))
assert len(out)==114 and len(audits)==38
manifest=dict(experiment='E4-closed-causal-path-prediction',source_run=36850448602,source_artifact='athena-embench-structural',group_sizes=list(KS),traces=audits,predictor='last completed nonoverlapping BB-window suffix per first-BB PC, initially empty; causal update only after complete window',limitations=['Retrospective BB windows, not validated single-entry superblocks','No BTB/aliasing/capacity, no prediction lead-time or configuration-generation costs','Prediction of full future BB-entry sequence, not instruction correctness','No K5 mapping, speedup, branch penalties, synthesis','k=1 omitted as trivial empty future path','No generalization beyond these dynamic traces'])
Path('e4-results/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
Path('e4-results/README.md').write_text('# E4 closed causal path-prediction feasibility\n\nAt the first BB of each disjoint 2/4/8 BB window, a predictor keyed by the entry PC emits the suffix of the last **completed** window with that entry PC, or abstains (cold). Exact-match success requires the entire suffix to match. This is a causal prediction baseline, not a branch predictor integrated into the OoO machine or a prepared CGRA configuration. No K5 feasibility or performance claims.\n')
print('E4_AUDIT_PASS traces 38 rows 114',flush=True)
