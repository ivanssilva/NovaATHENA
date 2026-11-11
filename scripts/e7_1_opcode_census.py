#!/usr/bin/env python3
"""E7.1 preflight: exhaustive opcode and operand-shape census, no semantic assumptions."""
import csv,glob,collections,json,hashlib,re
from pathlib import Path
paths=sorted(set(glob.glob('structural/*_O*.trace.csv')+glob.glob('structural/**/*.trace.csv',recursive=True)))
assert len(paths)==38,('expected 38 traces',len(paths))
out=Path('e7-1-census');out.mkdir(exist_ok=True)
op=collections.Counter();examples={};shapes=collections.Counter();traces=[];total=0
for p in paths:
 c=collections.Counter();n=0
 with open(p,newline='') as f:
  rd=csv.DictReader(f);assert {'pc','op','args'}.issubset(rd.fieldnames)
  for r in rd:
   mnemonic=r['op'].strip().lower();args=r['args'].strip()
   op[mnemonic]+=1;c[mnemonic]+=1;n+=1
   examples.setdefault(mnemonic,{'trace':Path(p).name,'pc':r['pc'],'args':args})
   shape=(mnemonic,len(args.split(',')) if args else 0)
   shapes[shape]+=1
 traces.append({'name':Path(p).name,'instructions':n,'distinct_opcodes':len(c),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()})
 total+=n
with open(out/'opcodes.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['opcode','count','example_trace','example_pc','example_args'])
 for name,count in sorted(op.items()):w.writerow([name,count,examples[name]['trace'],examples[name]['pc'],examples[name]['args']])
with open(out/'operand_shapes.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['opcode','comma_fields','count'])
 for (name,arity),count in sorted(shapes.items()):w.writerow([name,arity,count])
(out/'manifest.json').write_text(json.dumps({'experiment':'E7.1 opcode preflight','source_run':36850448602,'source_artifact':'athena-embench-structural','traces':traces,'instructions':total,'distinct_opcodes':len(op),'note':'Opcode census only; semantic decoding and OoO rename not validated'},indent=2)+'\n')
print('E7_1_CENSUS_PASS traces',len(paths),'instructions',total,'opcodes',len(op),flush=True)
for name,count in sorted(op.items()):print('OPCODE',name,count,examples[name]['args'],flush=True)
