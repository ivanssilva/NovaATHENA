#!/usr/bin/env python3
import csv,collections
c=collections.Counter(); forms=collections.Counter()
with open('step4d1_unknown_semantics.csv',newline='') as f:
 for r in csv.DictReader(f):
  n=int(r['occurrences']);c[r['op']]+=n;forms[r['op']]+=1
t=sum(c.values())
print('STEP4D1A_AUDIT total',t,'opcodes',len(c),'forms',sum(forms.values()))
cum=0
for i,(op,n) in enumerate(c.most_common(),1):
 cum+=n
 print('STEP4D1A_OPCODE',i,op,'occurrences',n,'share',f'{n/t:.9f}','cumulative',f'{cum/t:.9f}','forms',forms[op])
