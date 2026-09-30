#!/usr/bin/env python3
"""Generate 30 self-contained, integer C kernels, deliberately varied in dependence patterns."""
from pathlib import Path
out=Path("benchmarks/generated");out.mkdir(parents=True,exist_ok=True)
headers="#include <stdint.h>\n#define N 64\nstatic volatile uint32_t sink;\n"
templates={
"fir":"for(int i=8;i<N;i++){uint32_t s=0;for(int j=0;j<8;j++)s+=a[i-j]*b[j];a[i]=s;}",
"iir":"for(int i=2;i<N;i++)a[i]=a[i-1]*3+a[i-2]*5+b[i];",
"dot":"uint32_t s=0;for(int i=0;i<N;i++)s+=a[i]*b[i];sink=s;",
"axpy":"for(int i=0;i<N;i++)a[i]=a[i]*3+b[i];",
"prefix":"for(int i=1;i<N;i++)a[i]+=a[i-1];",
"xor_mix":"for(int i=0;i<N;i++){uint32_t x=a[i],y=b[i];a[i]=((x<<7)^(y>>3))+(x&y);}",
"crc":"uint32_t c=0xffffffff;for(int i=0;i<N;i++){c^=a[i];for(int j=0;j<8;j++)c=(c>>1)^((0u-(c&1u))&0xedb88320u);}sink=c;",
"branch":"for(int i=0;i<N;i++){uint32_t x=a[i],y=b[i];a[i]=x>y?(x-y):(x+y);}",
"minmax":"for(int i=0;i<N;i++){uint32_t x=a[i],y=b[i];a[i]=x<y?x:y;b[i]=x>y?x:y;}",
"butterfly":"for(int i=0;i<N;i+=2){uint32_t x=a[i],y=a[i+1];a[i]=x+y;a[i+1]=x-y;}",
}
for name,body in templates.items():
 for variant in range(3):
  # Three variants use distinct, explicit data initialization and loop repetition, not three independent algorithms.
  init=f"for(int i=0;i<N;i++){{a[i]=(uint32_t)(i*{variant+3}+1);b[i]=(uint32_t)(i*{variant+5}+7);}}"
  code=headers+f"int main(void){{uint32_t a[N],b[N];{init}for(int rep=0;rep<{variant+1};rep++){{{body}}}for(int i=0;i<N;i++)sink^=a[i];return (int)(sink&255u);}}\n"
  (out/f"{name}_v{variant}.c").write_text(code)
print("Generated",len(list(out.glob("*.c"))),"kernels")
