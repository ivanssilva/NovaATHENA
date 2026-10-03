import csv,statistics,collections
PIN='09c2ed8c3b7008c95d08b038de4a3f6dc103ed70'
assert open('EMBENCH_REVISION.txt').read().strip()==PIN
def fam(r):
 o,d,j,f,m=map(int,[r['ops'],r['depth'],r['joins'],r['forks'],r['mul_ops']])
 if o==1:return 'single_mul' if m else 'single_alu'
 if d==1:return 'parallel_with_mul' if m else 'parallel_independent'
 b='chain_join_fork' if j and f else 'convergence' if j else 'fork' if f else 'chain'
 return b+('_d3plus' if d>=3 else '_d2')+('_mul' if m else '')
rows=[r for r in csv.DictReader(open('gt_capacity_descriptor_counts.csv')) if r['D']=='3' and r['C']=='8']
mass=collections.Counter();tot=collections.Counter()
for r in rows:
 k=(r['benchmark'],r['opt']);w=int(r['occurrences'])*int(r['ops']);tot[k]+=w;mass[k+(fam(r),)]+=w
assert len(tot)==38
fs=sorted({k[2] for k in mass}); out=[]
for opt in ('O2','O3'):
 for F in fs:
  v=sorted(mass[(b,opt,F)]/tot[(b,opt)] for b,o in tot if o==opt); n=len(v)
  out.append([opt,F,statistics.median(v),statistics.median(v[:n//2]),statistics.median(v[(n+1)//2:]),sum(x>0 for x in v)])
with open('step3_pe_benchmark_summary.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['opt','family','median_share','q1','q3','benchmarks_nonzero']);w.writerows(out)
sets=[('PE-ALU',{'single_alu','parallel_independent'}),('+PE-C2',{'single_alu','parallel_independent','chain_d2'}),('+PE-J',{'single_alu','parallel_independent','chain_d2','convergence_d2'})]
mr=[]
for opt in ('O2','O3'):
 for label,S in sets:
  v=sorted(sum(mass[(b,opt,F)] for F in S)/tot[(b,opt)] for b,o in tot if o==opt)
  mr.append([opt,label,statistics.median(v),statistics.median(v[:9]),statistics.median(v[10:])])
with open('step3_pe_marginal_proxy.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['opt','candidate_set','median_structural_family_share','q1','q3']);w.writerows(mr)
with open('step3_pe_analysis.md','w') as f:
 f.write('# Step 3 benchmark-balanced PE evidence\n\nPinned Embench '+PIN+'; D=3,C=8; 19 paired benchmarks per optimization.\n')
 f.write('Shares are computed per benchmark before summary. Marginal values are structural family proxies, not exact mapping, cycles, IPC, ATHENA coverage, or speedup. D is RAW depth, not cycles.\n\n')
 for r in out:f.write('%s %s median=%.6f IQR=[%.6f,%.6f] nonzero=%d/19\n'%tuple(r))
 f.write('\n## Nested candidate-set proxy\n')
 for r in mr:f.write('%s %s median=%.6f IQR=[%.6f,%.6f]\n'%tuple(r))
print('STEP3_BENCHMARK_COMPLETE benchmarks',len(tot),'families',len(fs))
for r in mr:print('STEP3_PROXY',*r)
