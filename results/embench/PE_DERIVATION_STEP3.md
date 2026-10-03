# ATHENA — Passo 3: evidência estrutural para PEs candidatos

## Proveniência
- Embench fixado: `09c2ed8c3b7008c95d08b038de4a3f6dc103ed70`; RV32IM/ILP32; 19 benchmarks, O2/O3, 38 traces.
- Corpus validado: run `36900929836`, 121418557 linhas, 65876529 operações ALU elegíveis.
- Extração e famílias: run `37145305760`, commit `e789df0982839f4d000280b28cca33d7a8039606`, artefato `11282509918`, SHA-256 `47d51909ffc17246af9edd2de7bdbf5ab24bc6f2d2536d809cc22f75c2d4af6a`.
- Fonte numérica: log STEP3_FAMROW e CSVs `gt_pe_family_summary.csv`, `gt_pe_evidence.csv`, `gt_capacity_descriptor_counts.csv`.
- Parâmetros: profundidade RAW D=1,2,3; limite de operações C=4,6,8,12. Referência descritiva D=3,C=8.
- Método: contagem de grupos por família, soma de operações ponderada por ocorrência, número de benchmarks por família, comparação separada O2/O3 e sensibilidade a C.

## Evidência D=3,C=8
| Família | O2 % das operações elegíveis | O3 % | Benchmarks O2/O3 |
|---|---:|---:|---:|
| parallel_independent | 30.779052 | 30.611676 | 19/19 |
| chain_d2 | 14.623944 | 15.994583 | 17/17 |
| single_alu | 11.079268 | 10.855275 | 19/19 |
| chain_d3plus | 9.863059 | 10.248364 | 16/16 |
| chain_d2_mul | 9.565690 | 5.622305 | 8/9 |
| convergence_d2 | 7.146953 | 7.959871 | 10/10 |
| convergence_d3plus | 4.184648 | 4.409345 | 11/9 |

## Sensibilidade D=3 (O2/O3 %, C=4 → C=8 → C=12)
- parallel_independent: 39.792977/41.328012 → 30.779052/30.611676 → 26.555594/25.756111.
- chain_d2: 18.394008/16.581350 → 14.623944/15.994583 → 13.593514/14.313270.
- chain_d3plus: 7.284892/7.396483 → 9.863059/10.248364 → 10.001438/10.384404.
- convergence_d3plus: 1.054816/1.123284 → 4.184648/4.409345 → 11.585003/12.294294.

## Inferências arquiteturais provisórias (não são resultados medidos)
1. PE-ALU simples: bloco elementar configurável para ALU isolada, também serve para paralelismo independente quando replicado.
2. PE-C2: candidato com duas ALUs conectáveis A→B, com bypass para executar operação simples. A cadeia curta tem presença em 17/19 benchmarks nas duas otimizações. Não assumir execução combinacional no mesmo ciclo antes de síntese de timing.
3. PE-J: candidato seletivo para convergência de dois resultados internos em uma operação consumidora, sujeito à extração de assinaturas exatas, demanda de entradas/saídas e custo de mux/interconexão. Convergência de G_t pode exceder um único PE.
4. MUL: tratar como recurso seletivo/compartilhado ou variante candidata após análise balanceada por benchmark e latência; não presumir multiplicador em cada PE.
5. Cadeias de profundidade 3, forks e join+fork: inicialmente mapear em múltiplos PEs ou estágios; especialização adicional requer ganho marginal comprovado.

## Limitações e decisões pendentes
- Percentuais são participação estrutural das operações elegíveis na classificação de grupos; NÃO são cobertura de ATHENA, IPC, ciclos ou speedup.
- Famílias descritivas não determinam forma exata do subgrafo, quantidade de entradas nem interconexão.
- Contagem de benchmarks não substitui estatísticas balanceadas (mediana, IQR) por benchmark; extraí-las de `gt_capacity_descriptor_counts.csv` antes de selecionar configuração final.
- `unconsumed_defs` é local ao grupo e NÃO mede live-out verdadeiro para operações futuras.
- D é profundidade RAW, não número de ciclos. Síntese de timing no mesmo alvo tecnológico deve validar cadeias no período de clock.
- Comparar cobertura marginal conjunta de tipos de PE, não somar percentuais de famílias como se fossem ganho de desempenho.
- Topologia, simulação temporal, área total e potência estática permanecem passos posteriores.

## Próximo subpasso
Analisar descritores por benchmark e assinaturas de entradas/saídas, selecionar e avaliar cobertura marginal do menor conjunto de PEs; em seguida validar a viabilidade temporal por síntese. Não fixar PE-J nem PE-C2 como hardware definitivo antes dessas verificações.
