# Atribuição de consumo elétrico em hosts Proxmox

Use este procedimento quando existir um medidor físico de potência no Home Assistant e o usuário quiser descobrir quais VMs, containers ou componentes provocam picos no host.

## Princípio central

O medidor do Home Assistant mede o conjunto; o Proxmox mede atividade, não watts por guest. Portanto, trate a atribuição como **correlação temporal com grau de confiança**, nunca como medição elétrica individual.

Separe sempre:

1. **Consumo de base** — hardware permanentemente energizado: HDDs ativos, GPUs, RAM, controladoras, NICs, ventoinhas e perdas da fonte.
2. **Consumo incremental** — CPU, disco, rede, aceleradores e workloads que coincidem com um pico.

## Coleta mínima

1. Confirme entidade, unidade, `device_class` e `state_class` no Home Assistant.
2. Consulte `/api/history/period/<start>` com:
   - `filter_entity_id=<sensor>`;
   - `end_time=<end>`;
   - `significant_changes_only=0`.
3. Preserve timestamps com timezone explícito. Para este ambiente, normalize para `America/Sao_Paulo`.
4. Busque RRD do Proxmox em resolução de um minuto:
   - host: `/nodes/<node>/rrddata?timeframe=day&cf=AVERAGE`;
   - QEMU: `/nodes/<node>/qemu/<vmid>/rrddata`;
   - LXC: `/nodes/<node>/lxc/<vmid>/rrddata`.
5. Consulte também `/nodes/<node>/tasks`, journal do período, estado dos discos e inventário/passthrough.
6. Faça uma fotografia ao vivo com potência física, estado do host e, se disponível, RAPL em `/sys/class/powercap/intel-rapl:*`.

## Correlação

Para cada leitura de potência relevante:

- alinhe-a ao minuto RRD mais próximo e rejeite correspondências inesperadamente distantes, em vez de preencher lacunas silenciosamente;
- compare contra a mediana do dia, não apenas contra outra leitura arbitrária;
- examine host CPU, load, iowait, PSI de I/O, memória, swap e rede;
- calcule CPU efetiva do guest como `cpu * maxcpu`;
- trate `diskread`, `diskwrite`, `netin` e `netout` como taxas e mantenha as direções separadas;
- examine uma janela de pelo menos ±10 minutos, pois o workload pode começar antes ou persistir depois da leitura elétrica.

A direção da rede pode revelar pipelines. Exemplo genérico: guest A envia ~20 MB/s, guest B recebe e retransmite ~20 MB/s, guest C recebe ~20 MB/s e grava valor semelhante no disco. Isso sustenta uma hipótese A → B → C com confiança alta, embora não prove aplicação ou arquivo.

## Testes de causalidade úteis

- Compare pontos com CPU maior e potência menor. Isso pode refutar “CPU é a causa única”.
- Verifique tarefas e logs para excluir backup, start/stop, migração ou restore.
- Use RAPL ao vivo para separar pacote da CPU do restante da máquina; deixe explícito que RAPL não mede o servidor completo e que uma amostra atual não representa retrospectivamente o minuto histórico do pico.
- Confira HDDs com `hdparm -C` ou equivalente sem acordá-los desnecessariamente.
- Para atribuir watts de verdade, proponha ensaios A/B controlados, uma mudança por vez, usando medianas de 10–15 minutos.

## Limitações obrigatórias no relatório

- Histórico REST do Home Assistant contém mudanças de estado e pode ser esparso; média aritmética das amostras não é média diária ponderada nem kWh.
- “Máximo” significa máximo registrado, não garantia de capturar impulsos entre atualizações.
- Proxmox não mede watts por VM/LXC.
- Não invente potência nominal de HDD, GPU ou guest sem medição ou fonte verificável.
- Diferencie evidência observada, inferência forte e hipótese.

## Estrutura recomendada do relatório

1. Conclusão executiva com pico, delta absoluto e percentual sobre a mediana.
2. Estatísticas e maiores leituras do medidor.
3. Estado do host no minuto do pico versus mediana diária.
4. Linha do tempo da janela.
5. Ranking de contribuidores com grau de confiança e evidência.
6. Consumo de base versus consumo incremental.
7. Hipóteses descartadas.
8. Fotografia atual.
9. Recomendações A/B e melhorias de telemetria.
10. Limitações e parecer final.

Antes de entregar, confirme que o arquivo foi realmente criado no destino solicitado, releia início e conclusão, valide tamanho/linhas, faça uma varredura conservadora por credenciais e preserve os dados-fonte sem alteração.

Nunca inclua tokens do Home Assistant, credenciais SSH ou segredos do Proxmox no relatório ou nos artefatos persistentes.
