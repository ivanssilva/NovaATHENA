# E7.4 — decisão de prontidão e bloqueio metodológico

Data: 2026-11-11. Referência normativa: [issue #21](https://github.com/ivanssilva/NovaATHENA/issues/21).

## Pergunta experimental
Determinar bloqueios de prontidão por **live-ins**, recursos, configuração e sincronização, **somente quando** existirem eventos de `operand-ready` confiáveis. Não confundir essas medidas com desempenho medido.

## Auditoria da evidência disponível
- [E7.2 audit](E7_2_validation_and_ooo_event_audit.md): `scripts/step5d_ooo4.py` e `scripts/ooo4_c2_experiment.py` modelam épocas de computação e filas/ROB, mas não fornecem fluxo completo observável de eventos de renomeação, operand-ready, resolução de desvio e squash em execução especulativa OoO.
- E7.1: análise reconstruída de dependências arquiteturais a partir de traces; não observa wakeup de operandos no escalonador OoO.
- E7.2: microcasos sintéticos de formação/publicação segura; não mede o instante em que operandos reais ficam prontos.
- [E7.3 / E7.3b](E7_3_E7_3b_consolidation.md): experimentos sintéticos de filas; `blocked_cycles` não equivale a stalls reais de CPU nem indica operand-ready.

## Decisão
**E7.4 quantitativa: NÃO EXECUTÁVEL com a instrumentação atualmente demonstrada.** Não é uma falha de execução: é uma barreira de validade científica. Não atribuir números de stalls por live-ins, recursos, configuração ou sincronização a traces arquiteturais de instruções confirmadas. Não produzir gráfico de prontidão artificial como resultado de benchmark.

## Condições de desbloqueio
1. Fonte de eventos OoO com ID dinâmico único, geração/epoch de especulação, PC, estágio de despacho/renomeação, mapa de produtores físicos e `operand-ready` com ciclo/timestamp.
2. Eventos de resolução de branch, squash/flush, commit e reutilização de ROB identificáveis; vínculo explícito entre produtor, consumidor e instruções descartadas.
3. Estado e eventos da configuração: tradução, fila, disponibilidade, invalidação e consumo pela t-CGRA; recursos de execução ocupados/liberados.
4. Microcasos dirigidos com oráculo independente: live-in pronto/atrasado, competição por recurso, configuração pendente, sincronização e squash; depois aplicar a corpus O2/O3.
5. Métricas com denominadores e unidades explícitos: oportunidades de região, ciclos de espera por causa, sobreposição entre causas, proporção de regiões utilizáveis; não chamar de speedup sem modelo temporal completo.
6. Manifestos com commit, run ID, configuração, input hashes, CSV e logs; separar resultados observados de hipóteses.

## Encaminhamento para V4
A issue #21 autoriza redação V4 após E7.1–E7.3, análise de limitações e **decisão** sobre E7.4. Esta decisão está registrada: relatar E7.4 como questão em aberto por ausência de observabilidade; não como experimento com resultados negativos. Para afirmações quantitativas, utilizar somente E1–E6 já validados e E7.1–E7.3 dentro do respectivo escopo. E7.1 não possui validação independente contra eventos de renomeação reais; E7.2 e E7.3 são sintéticos.
