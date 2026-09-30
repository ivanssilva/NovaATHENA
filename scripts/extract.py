import re,csv,pathlib,sys
lib=pathlib.Path(sys.argv[1]).read_text()
# Liberty area extraction; leakage is not estimated unless mapping and units can be validated.
cell_area={}
for m in re.finditer(r'\bcell\s*\(\s*([A-Za-z0-9_]+)\s*\)\s*\{',lib):
  start=m.end();depth=1;i=start
  while depth and i<len(lib):
    if lib[i]=='{':depth+=1
    elif lib[i]=='}':depth-=1
    i+=1
  c=lib[start:i];a=re.search(r'\barea\s*:\s*([\d.]+)',c)
  if a:cell_area[m.group(1)]=float(a.group(1))
rows=[]
for top in ['athena_4x4','athena_pe6','athena_4x4_1f','athena_pe6_1f']:
  v=pathlib.Path(f'reports/{top}.mapped.v').read_text()
  # Yosys ABC mapped netlist uses library cell names as instantiation types.
  counts={c:len(re.findall(r'(?m)^\s*'+re.escape(c)+r'\s+\\?\w+\s*\(',v)) for c in cell_area}
  area=sum(cell_area[c]*n for c,n in counts.items())
  unknown=[x for x in re.findall(r'(?m)^\s*([A-Za-z_][A-Za-z0-9_]*)\s+\\?\w+\s*\(',v) if x not in cell_area and not x.startswith('module')]
  rows.append({'top':top,'mapped_cell_area_um2':round(area,4),'mapped_cells':sum(counts.values()),'unmatched_instantiations':len(unknown)})
with open('reports/summary.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(rows)
