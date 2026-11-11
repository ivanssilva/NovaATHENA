# E7.3 / E7.3b — consolidação e limites de inferência

## Evidência de execução
- E7.3: [GitHub Actions 43068953101](https://github.com/ivanssilva/NovaATHENA/actions/runs/43068953101), **success**, 144 cenários, artefato `novaathena-e7-3-synthetic`.
- E7.3b: [GitHub Actions 43069895714](https://github.com/ivanssilva/NovaATHENA/actions/runs/43069895714), **success**, 144 cenários, artefato `novaathena-e7-3b-controlq`.
- Scripts de reprodução: `scripts/e7_3_queue_pressure.py` e `scripts/e7_3b_controlq_saturation.py`.

## O que os experimentos efetivamente demonstram
1. **Conservação de eventos:** nos dois modelos, os testes verificam `completed + dropped == offered` e `accepted == completed` ao término da simulação. Na política de backpressure não há descarte; na política drop eventos podem ser eliminados por falta de capacidade.
2. **E7.3:** dois perfis de chegada sintéticos (rajada de quatro eventos por ciclo durante 12 ciclos; esparso, um evento a cada quatro ciclos), políticas drop/backpressure, capacidades e taxas de serviço variáveis. O modelo consome a ControlQ no mesmo ciclo da transferência da LearnQ; por isso a pressão persistente na ControlQ é insuficientemente explorada.
3. **E7.3b:** introduz consumo de **um** evento da ControlQ a cada 1, 2 ou 4 ciclos, medindo ocupação, ciclos de fila cheia, bloqueio de entrada e latência de conclusão. Assim, torna possível observar a saturação dessa fila em cenários dirigidos.
4. **Trade-off estrutural:** descarte pode reduzir o tempo até o esvaziamento do sistema por **não processar todos os eventos**; backpressure conserva os eventos à custa de maior atraso e retenção. Não interpretar a menor duração de drop como ganho de desempenho de aplicação.

## Limitações científicas — essenciais para o artigo
- Os **288 cenários são sintéticos** e não derivados de tempos/eventos de renomeação, commit, squash ou resolução de desvio observados em uma execução OoO real.
- As métricas não são IPC, speedup, utilização de PEs ou aceleração de t-CGRA. São exclusivamente métricas do subsistema abstrato de filas.
- O período de serviço de E7.3b é uma hipótese de projeto, não latência de hardware medida.
- O backpressure está modelado como retenção dos eventos oferecidos no buffer `pending` de capacidade **não limitada**. Portanto, o experimento **não** modela retropropagação completa ao front-end, ROB, fetch ou impacto em throughput da CPU.
- `blocked_cycles` conta ciclos com tentativa de entrada frustrada; não corresponde necessariamente a ciclos de stall de CPU.
- A ocupação é amostrada ao fim de cada ciclo. E7.3 e E7.3b possuem ordem de atualização diferente; **não comparar diretamente suas métricas de ocupação ou latência** sem harmonizar a semântica temporal.
- Na política drop, a média de latência se refere **somente aos eventos concluídos**; há viés de seleção em relação aos eventos oferecidos.
- A validação do GitHub Actions confirma execução, invariantes e geração de CSV, **não** valida a representatividade do modelo frente a um OoO real.
- Não foi feita nesta consolidação uma auditoria linha a linha dos CSVs publicados; não atribuir valores agregados específicos a esses artefatos sem lê-los.

## Conclusão arquitetural sustentada
Capacidades finitas, taxa de transferência e latência de serviço impõem limites de admissão e escoamento de eventos. O dimensionamento de LearnQ e ControlQ deve considerar tráfego em rajadas e a política de perda/bloqueio. Sob taxas de serviço inferiores à demanda, apenas aumentar capacidade absorve transientes: não elimina sobrecarga sustentada. Estes são **limites do modelo de filas**, não limites quantitativos demonstrados de utilização da t-CGRA.

## Decisão de campanha
Encerrar **E7.3 e E7.3b como estudos paramétricos sintéticos executados com sucesso**, preservando suas limitações. Para sustentar alegações de impacto no desempenho e utilização da t-CGRA, será necessária uma etapa posterior de acoplamento a eventos temporais observáveis do OoO e métricas de utilização. Antes da E7.4, revisar os critérios da [issue #21](https://github.com/ivanssilva/NovaATHENA/issues/21) e garantir que seu escopo não dependa de evidência ausente.
