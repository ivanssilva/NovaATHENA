#!/usr/bin/env python3
"""E5 closed: causal reuse of exact BB-entry path configurations, no speedup.
Causal last-path predictor plus independently trained completed-path dictionary.
At entry of a nonoverlapping k-BB window, prediction may hit only an already
completed and stored path. A correct prediction can be useful only when its
configuration has already been observed; no oracle or future data.
This is a path-key reuse upper proxy, NOT K5 configuration generation.
"""
import csv,glob,collections,json,hashlib
from pathlib import Path
BR={'beq','bne','blt','bge','bltu','bgeu','jal','jalr','j','jr','ret','call','tail','c.j','c.jal','c.jr','c.jalr','c.beqz','c.bnez','ecall','ebreak','mret','sret'}
KS=(2,4,8)
paths=sorted(set(glob.glob('structural/*_O*.trace.csv')+glob.glob('structural/**/*.trace.csv',recursive=True)))
assert len(paths)==38
Path('e5-results').mkdir(exist_ok=True)
out=[];audits=[]
for path in paths:
 name=Path(path).name.removesuffix('.trace.csv');bench,opt=name.rsplit('_',1)
 pending={k:[] for k in KS};state={k:{} for k in KS};seen={k:set() for k in KS};stats={k:collections.Counter() for k in KS}
 prev=None;start=None;rows=blocks=0
 def finish():
  global blocks
  if start is None:return
  blocks+=1
  for k in KS:
   q=pending[k];q.append(start)
   if len(q)!=k:continue
   s=stats[k];s['windows']+=1
   pathkey=tuple(q);entry=pathkey[0];actual=pathkey[1:]
   pred=state[k].get(entry)
   if pred is None:s['cold_predictor']+=1
   else:
    s['predictions']+=1
    predicted_key=(entry,)+pred
    if pred==actual:
     s['correct']+=1
     if predicted_key in seen[k]:s['causal_reuse_hits']+=1
     else:s['correct_without_stored_key']+=1
    else:s['wrong']+=1
   if pathkey in seen[k]:s['actual_path_previously_seen']+=1
   else:s['new_path_keys']+=1
   # Critical causal order: query predictor/cache BEFORE inserting observed path.
   seen[k].add(pathkey);state[k][entry]=actual
   q.clear()
 with open(path,newline='') as f:
  rd=csv.DictReader(f);assert {'pc','op','args'}.issubset(rd.fieldnames)
  for r in rd:
   rows+=1;pc=int(r['pc'],0)
   if prev is not None and (prev['op'].lower().strip() in BR or pc!=int(prev['pc'],0)+4):
    finish();start=None
   if start is None:start=pc
   prev=r
 finish()
 for k in KS:
  s=stats[k];s['tail_BBs']=len(pending[k])
  assert s['windows']*k+s['tail_BBs']==blocks
  assert s['windows']==s['cold_predictor']+s['predictions']
  assert s['predictions']==s['correct']+s['wrong']
  assert s['correct']==s['causal_reuse_hits']+s['correct_without_stored_key']
  assert s['actual_path_previously_seen']+s['new_path_keys']==s['windows']
  assert s['correct_without_stored_key']==0
  out.append(dict(benchmark=bench,opt=opt,group_BBs=k,dynamic_BBs=blocks,**{a:s[a] for a in ('windows','cold_predictor','predictions','correct','wrong','causal_reuse_hits','correct_without_stored_key','actual_path_previously_seen','new_path_keys','tail_BBs')}))
 audits.append(dict(trace=name,sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),instructions=rows,blocks=blocks))
 print('E5_TRACE',name,'k8',stats[8]['causal_reuse_hits'],'/',stats[8]['windows'],flush=True)
with open('e5-results/e5_per_trace.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
with open('e5-results/e5_aggregate.csv','w',newline='') as f:
 cols=list(out[0]);w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
 for opt in ('O2','O3'):
  for k in KS:
   rr=[r for r in out if r['opt']==opt and r['group_BBs']==k]
   w.writerow(dict(benchmark='ALL',opt=opt,group_BBs=k,**{key:sum(r[key] for r in rr) for key in cols[3:]}))
assert len(out)==114 and len(audits)==38
manifest=dict(experiment='E5-closed-causal-path-key-reuse',source_run=36850448602,source_artifact='athena-embench-structural',group_sizes=list(KS),trace_audit=audits,semantics='At entry, predict path suffix from last completed same-entry window; look up predicted full-path key in unbounded previously completed path set; update only after completion',limits=['No actual CGRA configuration generated; path key is a reuse proxy','Unbounded dictionary, no eviction, no cache access latency or preparation cost','No branch predictor integrated in pipeline; no speedup','No cross-branch K5 mapping; no correctness of speculative execution established','No online binary translation latency','Disjoint trace-anchored windows, not static single-entry superblocks','This is a logical upper bound on reusable exact path-key occurrences, not an estimate of configuration-cache hit rate'])
Path('e5-results/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
Path('e5-results/README.md').write_text('# E5 closed causal path-key reuse proxy\n\nFrozen 38 Embench traces, nonoverlapping k=2,4,8 BB windows. At the entry PC, predict last completed suffix for this PC, then query an unbounded dictionary of previously completed full path keys. Count causal exact predicted reuse only if prediction is correct and key already stored. No actual configuration generation, mapping, cache capacity, latency or speedup.\n')
print('E5_AUDIT_PASS traces 38 rows 114',flush=True)
