# ATHENA-T/ROB — Nota técnica incremental III
## Síntese RTL, implementação física e caracterização dinâmica controlada
**Data:** 30 de setembro de 2026 · **Estado:** relatório experimental incremental, com ressalvas de validação

### 1. Relação com os documentos anteriores
Esta nota é complemento, e **não substituição**, de (D1) *ATHENA-T/ROB: geração oportunista de configurações, exploração de topologias do array e viabilidade físico-elétrica*, versão de 29/09/2026, e (D2) *ATHENA — nota de quantificação preliminar*. A leitura recomendada é D1 → D2 → esta nota. D1 define o hospedeiro RISC-V quatro vias, observação do despacho Tomasulo, LearnQ, ControlQ, eventos ROB, gerador, cache de configurações e array. D1 contém simulação dirigida de 24 instruções, três cenários de filas e exercício de 13 operações do kernel real MiBench/basicmath/usqrt. D2 introduz as estimativas estruturais das quatro topologias. **Esta nota acrescenta implementações RTL exploratórias, síntese e caracterização dinâmica controlada; não valida ainda a ATHENA integrada.**

A evolução experimental é: grafo ilustrativo e usqrt → quatro topologias e estimativas GE → síntese lógica e fluxo físico → 10 famílias de algoritmos C × 3 variantes × 3 otimizações, com rastros QEMU e mapeamento heurístico. O estudo usqrt de D1 não deve ser confundido com os dez templates sintéticos deste documento.

### 2. Topologias e fronteiras da implementação
| Topologia | ULAs físicas | Operações independentes, limite conceitual | Conexões |
|---|---:|---:|---|
| 4+4 | 8 | 8 | C1 com quatro ULAs; cada C2 recebe no máximo um resultado de C1 e um operando externo, ou executa independentemente |
| 4+4-1F | 8 | 8 | 4+4 com uma C2 dotada de dois seletores para dois resultados novos distintos de C1 |
| PE6 | 12 | 6 | Seis pares locais A→B; B só executa dependente de sua A |
| PE6-1F | 12 | 6 | PE6 com um B especial que aceita o resultado de sua A e um segundo resultado de outra A |

A ULA RTL comum implementa aritmética inteira e operações lógicas/deslocamentos/comparações. Multiplicação e memória não integram o datapath sintetizado nesta etapa. As versões RTL são blocos exploratórios, **não** incluem processador hospedeiro, ROB, LearnQ, ControlQ, gerador, cache de configurações, arbitragem de operandos ou implementação da integração arquitetural de D1. Consequentemente, não se pode inferir a área total da ATHENA.

### 3. Resultados de hardware e definição metrológica
**Distinguir obrigatoriamente:**
- **GE estimados em D2:** aproximação estrutural pré-síntese, dependente da definição de porta equivalente e do modelo de ULA/MUX; não converter diretamente para µm² sem calibração.
- **Área lógica Yosys/Nangate45:** soma das áreas das células mapeadas da implementação **combinacional** das quatro topologias, excluindo registradores dos wrappers físicos.
- **Área pós-fluxo físico OpenROAD:** métrica potencialmente distinta porque usa **wrappers com registradores de entrada/saída** e células após implementação física; não é a área do mesmo netlist combinacional. Não atribuir toda a diferença ao roteamento. Não somar área de floorplan/core com área de células.

**Resultados de síntese lógica verificados**, execução GitHub Actions 36709111463, artefato `athena-nangate45-synthesis`:
| Topologia | Células mapeadas | Área de células (µm²) | Variação relativa ao modelo básico da mesma família |
|---|---:|---:|---:|
| 4+4 | 9.400 | 10.429,062 | referência |
| 4+4-1F | 9.517 | 10.620,050 | +1,831% |
| PE6 | 13.238 | 14.598,612 | referência |
| PE6-1F | 13.275 | 14.694,372 | +0,656% |

A PE6 básica apresenta aproximadamente 40% mais área lógica que 4+4, **com 12 versus 8 ULAs**. O acréscimo de área da conexão 1F é pequeno nos dois pares; isso não prova ganho de desempenho.

**Implementação física:** o workflow OpenROAD/Nangate45 da execução 36709476622 foi concluído e publicou o artefato `athena-nangate45-physical`. Em resposta anterior foram divulgados, respectivamente para 4+4, 4+4-1F, PE6 e PE6-1F, os números de área 24.111, 24.746, 33.553 e 30.037 µm²; leakage 0,603, 0,625, 0,852 e 0,744 mW; período 2,32, 2,31, 2,36 e 2,37 ns. **Esses valores históricos NÃO foram novamente extraídos e conferidos dos relatórios brutos nesta elaboração; registrar como alegações pendentes de auditoria, não como resultados verificados.** A queda aparentemente anômala de área de PE6-1F frente à PE6 exige verificação de wrappers, registradores, otimização, célula reportada e logs. Só após essa auditoria apresentar tabela física como medição confirmada.

**Rastreabilidade física:** fluxo em `scripts/generate_physical.py`, `.github/workflows/physical.yml`, run 36709476622. Para publicação, anexar nome exato de cada relatório, etapa (synth/place/CTS/route), biblioteca/canto, restrições de clock, área de células, área do core, contagem de FFs, buffers, leakage e caminho crítico; verificar se as interfaces registradas são comparáveis.

### 4. Benchmark controlado: dez famílias, três variantes
O código gerador `scripts/generate_kernels.py` cria **30 fontes C**, não 90 fontes distintas. Para cada fonte, a compilação em **-O0, -O2 e -O3** produz **90 executáveis RV32IM**. Cada executável é mapeado nas quatro topologias, produzindo **360 linhas** de comparação. Todas as fontes usam arrays `uint32_t a[64], b[64]`, inicialização parametrizada e um acumulador volátil `sink` para preservar efeitos observáveis. A compilação é freestanding e os programas são executados em QEMU RV32. São **templates sintéticos controlados**, não dez aplicações completas independentes nem amostra representativa de MiBench.

**Variantes exatas** (iguais para as dez famílias):
| Variante | Inicialização de a[i] | Inicialização de b[i] | Repetições do corpo da família |
|---|---|---|---:|
| v0 | i×3+1 | i×5+7 | 1 |
| v1 | i×4+1 | i×6+7 | 2 |
| v2 | i×5+1 | i×7+7 | 3 |

As expressões são convertidas para `uint32_t`. Os laços de inicialização percorrem `i=0..63`. Ao final, `sink ^= a[i]` para cada posição e `main` retorna `sink & 255`. A combinação de inicialização e repetição significa que **v0/v1/v2 variam duas dimensões simultaneamente**; não é um experimento fatorial capaz de separar causalmente os dois efeitos.

**Tabela integral das dez famílias (definição do benchmark):**
| Família | Corpo do kernel (resumo fiel) | Estrutura que se pretende investigar |
|---|---|---|
| FIR | Para i=8..63, acumular oito produtos `a[i-j]*b[j]` e escrever `a[i]` | Acumulação, multiplicação, dependências interiterações |
| IIR | Para i=2..63, `a[i]=3*a[i-1]+5*a[i-2]+b[i]` | Recorrências de dois atrasos |
| DOT | Acumular `a[i]*b[i]` em escalar `s` e atribuir `sink=s` | Produto escalar e redução |
| AXPY | `a[i]=3*a[i]+b[i]` | Operações independentes por elemento e fusões |
| PREFIX | Para i=1..63, `a[i]+=a[i-1]` | Dependência sequencial entre iterações |
| XOR MIX | `a[i]=((a[i]<<7)^(b[i]>>3))+(a[i]&b[i])` | Convergência de caminhos lógicos |
| CRC | Inicializar `c=0xffffffff`; para cada `a[i]`, aplicar XOR e oito passos de atualização condicional com polinômio `0xedb88320`; atribuir `sink=c` | Cadeia longa e lógica condicional |
| BRANCH | `a[i]=a[i]>b[i] ? a[i]-b[i] : a[i]+b[i]` | Desvio/seleção dependente de dados |
| MINMAX | Calcular mínimo e máximo de `a[i]`, `b[i]`, atualizando ambos | Comparação e múltiplas saídas |
| BUTTERFLY | Para pares adjacentes `x=a[i],y=a[i+1]`, produzir `x+y` e `x-y` | Compartilhamento de operandos e paralelismo |

**Reprodução:** as fontes geradas são produtos do script, não estão necessariamente versionadas uma a uma. Arquivar hash do script, versão do compilador, comandos completos, código de inicialização `benchmarks/start.S`, versões do QEMU, logs e arquivos CSV. Para um artigo, manter esta tabela no texto e 30 fontes, 90 rastros e CSVs no repositório/artefato versionado; não imprimir 90 programas.

### 5. Coleta e análise dinâmica
Workflow `.github/workflows/dynamic.yml`: gerar C; compilar RV32IM em três otimizações; executar via QEMU com `-d in_asm,exec,nochain`; reconstruir sequência de instruções por TB usando `scripts/dynamic_trace.py`; analisar com `scripts/dynamic_mapper.py`. A execução inicial 36723533191 concluiu com sucesso e publicou `athena-rv32-dynamic`. Uma execução posterior 36724587672 publicou logs de agregação auditáveis.

O mapeador identifica produtores por **última escrita no nome de registrador**, e reinicializa relações nos desvios reconhecidos. Só considera `add/sub/and/or/xor/sll/srl/sra/slt/sltu` e equivalentes imediatos. Não incorpora `mul`, cargas, stores, dependências de memória, aliases ou semântica completa de renomeação; não atravessa fronteiras de desvio. Trabalha com janelas heurísticas de 16 operações e não simula ciclos de Tomasulo, ROB, cache de configurações, latências de unidades ou custo de transferência. `configurations` é **quantidade de agrupamentos heurísticos**, não número de configurações únicas armazenadas, nem ciclos ou speedup. `fused_2producer` conta agrupamentos 2→1 aceitos pelo modelo, não fusões eletricamente verificadas.

### 6. Resultados dinâmicos agregados
**Contagens somadas sobre as 30 fontes para cada otimização:**
| Métrica | -O0 | -O2 | -O3 |
|---|---:|---:|---:|
| Instruções dinâmicas | 294.206 | 94.722 | 72.843 |
| Operações elegíveis pelo mapeador | 137.308 | 48.150 | 37.723 |
| Nós convergentes identificados | 34.490 | 4.243 | 4.626 |

**Agrupamentos estimados pelo mapeador:**
| Topologia | -O0 | -O2 | -O3 |
|---|---:|---:|---:|
| 4+4 | 22.161 | 15.932 | 14.061 |
| 4+4-1F | 22.272 | 15.929 | 13.935 |
| PE6 | 21.923 | 17.438 | 15.516 |
| PE6-1F | 21.923 | 15.902 | 13.915 |

**Fusões 2→1 aceitas pela heurística:**
| Topologia | -O0 | -O2 | -O3 |
|---|---:|---:|---:|
| 4+4-1F | 1.058 | 383 | 319 |
| PE6-1F | 9 | 1.920 | 1.920 |

Em -O2, as 1.920 fusões de PE6-1F concentram-se em CRC (1.536) e XOR MIX (384); as 383 de 4+4-1F concentram-se em XOR MIX. **Esses dados indicam sensibilidade a famílias e otimizações, não benefício generalizável.** A PE6-1F reduziu os agrupamentos de PE6 em ~8,81% em -O2, mas a comparação com 4+4 básica resulta em apenas ~0,19% menos agrupamentos. A 4+4-1F produz **mais** agrupamentos que a 4+4 em -O0: evidência de que a heurística não é monotônica com o acréscimo de recursos. **Não converter diferenças em speedup ou ganho energético.** Os totais acima são extraídos dos logs agregados da execução 36724587672; verificar novamente contra CSV antes de publicação final.

### 7. Interpretação conjunta: custo versus oportunidade
O acréscimo lógico de 1F é +1,831% para 4+4 e +0,656% para PE6. O número de fusões e a redução heurística de agrupamentos são maiores em PE6-1F para os kernels CRC e XOR MIX otimizados. A comparação entre famílias permanece confundida por **12 versus 8 ULAs**, diferenças de independência, política de agrupamento e interfaces de operandos. Os resultados não demonstram que uma topologia tenha melhor desempenho ou eficiência total. Também não justificam usar área lógica de blocos combinacionais como área de ATHENA completa.

### 8. Auditoria, verificações obrigatórias e experimentos seguintes
1. **Auditar os relatórios físicos originais:** confirmar áreas/leakage/atraso de cada topologia, mesma etapa e mesmo tipo de wrapper; investigar a área menor anteriormente atribuída a PE6-1F.
2. **Verificar monotonicidade do mapeador:** para cada grafo, um modelo com 1F deve poder reproduzir a configuração da versão sem 1F; incorporar teste dirigido para 4+4-1F em -O0.
3. **Verificar fidelidade da topologia:** PE6-1F tem somente um B especial; testar a posição/localidade do A pareado, seleção de outro A, fan-out e número de entradas externas. Para 4+4, testar operações C2 independentes e dependentes e seus seletores.
4. **Validar semântica dos rastros:** checar instruções QEMU executadas versus contagem independente, saltos, blocos e pseudoinstruções; documentar versão das ferramentas.
5. **Separar parâmetros de variantes:** quando desejar causalidade, executar desenho fatorial com inicialização e repetição variando independentemente.
6. **Adicionar benchmarks independentes:** incorporar Embench, MiBench e/ou PolyBench com commits fixos e licenças verificadas, distinguindo-os deste conjunto sintético.
7. **Integrar modelo temporal:** janelas efetivas de despacho, ROB, RS, latências, cache, configuração, disponibilidade de operandos e reutilização; só então estimar ciclos, speedup e energia.

### 9. Manifesto mínimo de rastreabilidade
| Evidência | Local |
|---|---|
| RTL e síntese | `rtl/athena_*.v`, `scripts/run.sh`, `.github/workflows/nangate45.yml`; run [36709111463](https://github.com/ivanssilva/NovaATHENA/actions/runs/36709111463) |
| Fluxo físico | `scripts/generate_physical.py`, `.github/workflows/physical.yml`; run [36709476622](https://github.com/ivanssilva/NovaATHENA/actions/runs/36709476622) |
| Gerador do benchmark | `scripts/generate_kernels.py` |
| Rastreamento QEMU | `scripts/dynamic_trace.py`, `benchmarks/start.S`, `.github/workflows/dynamic.yml` |
| Mapeador heurístico | `scripts/dynamic_mapper.py` |
| Primeira execução dinâmica concluída | run [36723533191](https://github.com/ivanssilva/NovaATHENA/actions/runs/36723533191) |
| Execução com agregados nos logs | run [36724587672](https://github.com/ivanssilva/NovaATHENA/actions/runs/36724587672) |
| Resultado por combinação | Artefato `athena-rv32-dynamic`, arquivo `dynamic_summary.csv` |
| Fonte histórica da arquitetura | D1, relatório ATHENA-T/ROB de 29/09/2026, especialmente §§2, 4–5 e Anexos A–G |
| Fonte histórica das estimativas | D2, nota de quantificação preliminar |

**Regra editorial:** todo número publicado deve identificar grandeza, unidade, estágio do fluxo, bloco incluído/excluído, revisão do código, execução e arquivo bruto. Dados ainda não auditados permanecem marcados como pendentes, nunca misturados a medições confirmadas.
