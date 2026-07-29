### 1. Introdução

O KPI Model estabelece como as informações produzidas ao longo da arquitetura IMS são consolidadas em indicadores capazes de apoiar decisões operacionais, táticas e estratégicas.

No contexto do Industrial Mill Streaming (IMS), um KPI não representa apenas um número utilizado para acompanhar desempenho.

Ele representa a síntese contextualizada do comportamento do processo industrial, construída a partir da integração entre telemetrias, eventos e conhecimento operacional.

Dessa forma, o KPI deixa de ser um objetivo da arquitetura e passa a ser um mecanismo de investigação que direciona a compreensão das condições que influenciaram determinado resultado.

---

### 2. Engineering Question

Como transformar informações operacionais em indicadores capazes de apoiar decisões fundamentadas no contexto do processo industrial?

Essa pergunta estabelece claramente o propósito do KPI Model.

---

### 3. Princípio de Modelagem
*Context Before KPI*

O IMS adota o princípio Context Before KPI, segundo o qual nenhum indicador deve ser interpretado isoladamente.

Todo KPI deve preservar sua relação com:

- o processo que representa;
- os ativos envolvidos;
- as telemetrias observadas;
- os eventos ocorridos;
- o contexto operacional da planta.

Consequentemente, um indicador deixa de representar apenas um resultado numérico e passa a representar conhecimento contextualizado para tomada de decisão.

---

### 4. Conceito de KPI

No IMS, um KPI representa um indicador derivado da interpretação conjunta de telemetrias, eventos e contexto operacional.

Seu objetivo não é apenas medir desempenho, mas direcionar a investigação das condições que levaram determinado processo a apresentar um resultado específico.

Portanto, um KPI constitui uma entidade de apoio à decisão e não apenas um mecanismo de monitoramento.
````
    Processo
        │
        ▼
      Ativos
        │
        ▼
   Instrumentação
        │
        ▼
    Telemetria
        │
        ▼
     Eventos
        │
        ▼
       KPI
````
Essa sequência estabelece a rastreabilidade completa do indicador até sua origem física no processo industrial.

---

### 6. Estrutura Conceitual do KPI

Todo KPI deve preservar sua rastreabilidade e seu significado operacional.

| Elemento              | Descrição                               |
| --------------------- | --------------------------------------- |
| Nome                  | Identificação do indicador              |
| Objetivo              | Decisão que o indicador pretende apoiar |
| Processo              | Processo industrial associado           |
| Ativos Relacionados   | Equipamentos envolvidos                 |
| Telemetrias de Origem | Variáveis utilizadas                    |
| Eventos Relacionados  | Eventos considerados no cálculo         |
| Unidade               | %, t/h, h, °C, kWh/t etc.               |
| Frequência            | Atualização do indicador                |
| Contexto Operacional  | Condições em que o indicador foi obtido |

Essa estrutura garante que o indicador preserve sua interpretação ao longo de toda a arquitetura.

---

### 7. Classificação dos KPIs

Os indicadores podem ser classificados conforme sua finalidade.

*7.1 - KPIs de Processo*

Avaliam o desempenho do processo produtivo.

Exemplos:

- Produção Horária
- Eficiência de Extração
- Consumo Específico
- Tempo Médio de Ciclo

  
*7.2 - KPIs de Ativos*

Avaliam o desempenho dos equipamentos.

Exemplos:

- Disponibilidade
- MTBF
- MTTR
- Índice de Utilização

  
*7.3 - KPIs Operacionais*

Relacionados à execução da operação.

Exemplos:

- Tempo de Parada
- Tempo de Partida
- Tempo em Operação
- Cumprimento de Produção

  
*7.4 - KPIs de Qualidade*

Relacionados à qualidade do processo.

Exemplos:

- Brix Médio
- Pureza
- Pol
- Umidade

  
*7.5 - KPIs da Plataforma de Dados*

Relacionados ao desempenho da arquitetura IMS.

Exemplos:

- Latência de Ingestão
- Disponibilidade dos Pipelines
- Integridade dos Dados
- Qualidade das Telemetrias
- Percentual de Dados Perdidos

---

### 8. Relação entre Eventos e KPIs

Os eventos representam acontecimentos relevantes.

Os KPIs sintetizam o impacto desses acontecimentos sobre o desempenho do processo.

Exemplo:

| Evento               | KPI Impactado               |
| -------------------- | --------------------------- |
| Alta Temperatura     | Eficiência                  |
| Parada da Moenda     | Disponibilidade             |
| Vibração Excessiva   | MTBF                        |
| Falha de Pipeline    | Disponibilidade dos Dados   |
| Perda de Comunicação | Integridade das Informações |

Essa relação preserva a rastreabilidade entre causa operacional e desempenho observado.

---

### 9. Papel do KPI Model na Arquitetura IMS

O KPI Model representa a etapa responsável por transformar acontecimentos operacionais em indicadores capazes de orientar decisões.
````
Processo Industrial
        │
        ▼
      Ativos
        │
        ▼
   Instrumentação
        │
        ▼
    Telemetria
        │
        ▼
     Eventos
        │
        ▼
      KPIs
        │
        ▼
   Investigação
        │
        ▼
     Decisão
        │
        ▼
      Ação
````
Essa sequência demonstra que o KPI não encerra o fluxo informacional.

Ele inicia o processo de investigação que culmina na tomada de decisão.

---

### 10. Governança dos Indicadores

Todo KPI representado pelo IMS deve preservar:

- sua definição operacional;
- sua rastreabilidade;
- sua origem nas telemetrias e eventos;
- seu contexto operacional;
- sua consistência ao longo do tempo.

O IMS não estabelece metas corporativas nem critérios gerenciais de desempenho.

Seu papel consiste em representar indicadores de forma consistente, rastreável e contextualizada, preservando o significado técnico das informações utilizadas.

---

### 11. Limites Arquiteturais

O KPI Model é responsável por:

- representar indicadores industriais;
- consolidar telemetrias e eventos;
- preservar rastreabilidade;
- fornecer suporte à decisão.

Não é responsabilidade deste documento:

- definir dashboards;
- construir relatórios;
- especificar ferramentas analíticas;
- implementar visualizações;
- definir metas de produção;

Esses elementos pertencem às camadas de Analytics, Business Intelligence e Gestão.

---

### 12. Considerações Finais

O KPI Model conclui a cadeia de representação estabelecida pelo Industrial Process & Event Model (IPEM).

Ao consolidar telemetrias, eventos e contexto operacional em indicadores de desempenho, o IMS transforma observações do processo industrial em conhecimento estruturado para apoio à decisão.

Entretanto, no IMS, o indicador não representa a finalidade da arquitetura.

Sua verdadeira função consiste em direcionar a investigação das condições operacionais que explicam determinado comportamento do processo.

Assim, a plataforma deixa de responder apenas "qual foi o resultado?" e passa a responder "quais condições operacionais produziram esse resultado?".

Essa abordagem permite que processo, operação, manutenção e Engenharia de Dados compartilhem uma visão comum sobre o comportamento da planta industrial, transformando indicadores em instrumentos efetivos para melhoria contínua.

---

### 13. Relação com a Arquitetura IMS

Com o encerramento do IPEM-09, conclui-se a camada de Modelagem de Engenharia.

A sequência completa torna-se:
````
     Domínio
        │
        ▼
     Processo
        │
        ▼
      Ativos
        │
        ▼
   Instrumentação
        │
        ▼
    Telemetria
        │
        ▼
     Eventos
        │
        ▼
      KPIs
        │
        ▼
   Investigação
        │
        ▼
     Decisão
        │
        ▼
      Ação
````
Essa cadeia estabelece a base conceitual sobre a qual serão construídas as próximas camadas do IMS:
Arquitetura (ARCH), Registros de Decisão Arquitetural (ADR), Modelo de Dados (DM) e Implementação.
