## ADR-05 — Continuous Event Processing and Information Enrichment

| Campo | Valor |
|---|---|
| **Documento** | ADR-05 |
| **Título** | Continuous Event Processing and Information Enrichment |
| **Versão** | 1.0 |
| **Status** | Accepted |
| **Projeto** | Industrial Mill Streaming — IMS |
| **Especificação** | Architecture Decision Records — ADR |
| **Derivação** | ARCH-02 / ARCH-03 / ARCH-04 / ARCH-06 / ADR-01 / ADR-04 |

---

### 1. Context

O Industrial Mill Streaming (IMS) utiliza uma arquitetura orientada a eventos para adquirir, distribuir e persistir informações provenientes do processo industrial.

Após a aquisição, os eventos de telemetria possuem identidade, temporalidade, qualidade, origem e contrato estrutural definidos.

Entretanto, uma observação industrial isolada ainda possui capacidade limitada de representar o contexto operacional no qual determinado comportamento ocorreu.

Uma informação como:

```text
hydraulic_pressure = 185.4 bar
```

representa uma observação válida, porém não necessariamente informa:

- em qual condição operacional a Moenda se encontrava;
- se o valor representa comportamento esperado;
- se existe relação com outras variáveis do processo;
- se uma condição relevante foi identificada;
- se uma informação derivada pode ser produzida;
- qual significado aquela observação assume dentro de determinado contexto.

O IMS necessita, portanto, de uma capacidade de processamento contínuo capaz de transformar eventos de telemetria em informações progressivamente enriquecidas, preservando baixa latência e desacoplamento entre as capacidades da arquitetura.

> **Transportar eventos disponibiliza dados. Processá-los com contexto produz informação.**

---

### 2. Decision Drivers

A decisão considera os seguintes direcionadores:

- processamento contínuo de eventos;
- baixa latência end-to-end;
- simplicidade de implementação;
- preservação do desacoplamento;
- enriquecimento progressivo da informação;
- contextualização industrial;
- possibilidade de geração de informações derivadas;
- reutilização dos resultados por múltiplos consumidores.

---

### 3. Architectural Decision

*Continuous Event Processing*

> **O IMS adotará processamento contínuo de eventos para validar, transformar, contextualizar e derivar informações industriais em Near Real Time.**

O processamento será executado por uma capacidade independente da aquisição, persistência e analytics.

```text
Telemetry Event
      │
      ▼
Apache Kafka
      │
      ▼
Continuous Processing
      │
      ├── Validation
      ├── Transformation
      ├── Contextualization
      └── Derivation
      │
      ▼
Enriched / Derived Information
```

O processamento contínuo será utilizado quando a informação puder gerar valor operacional a partir de sua transformação próxima ao momento em que o evento ocorre.

Processamentos históricos, análises extensivas ou workloads que não dependam de baixa latência poderão utilizar outros modelos quando necessário.

---

### 4. Processing as Information Transformation

O processamento deverá consumir eventos de telemetria e produzir novos eventos somente quando existir uma transformação informacional relevante.

```text
Telemetry Event
      │
      ▼
Processing Service
      │
      ├── No Relevant Transformation
      │          │
      │          └── No Derived Event
      │
      └── Relevant Information Produced
                 │
                 ▼
          Enriched / Derived Event
```

O objetivo não é republicar cada evento apenas para criar uma nova etapa na arquitetura.

Um novo evento deverá representar uma nova informação, contexto ou condição relevante.

Essa abordagem reduz proliferação desnecessária de eventos e mantém o fluxo arquitetural objetivo.

---

### 5. Progressive Information Enrichment

Processamento contínuo materializa o princípio **Progressive Information Enrichment**, estabelecido no ARCH-02.

A informação poderá adquirir progressivamente maior significado conforme percorre diferentes capacidades.

```text
Industrial Signal
       │
       ▼
  Observation
       │
       ▼
Telemetry Event
       │
       ▼
Contextualized Information
       │
       ▼
Derived Information
       │
       ▼
Analytical Knowledge
```

Esses níveis representam **estados de maturidade informacional**, não necessariamente tabelas, bancos, tópicos ou camadas físicas independentes.

Por exemplo:

```text
185.4
  │
  ▼
hydraulic_pressure = 185.4 bar
  │
  ▼
mill_01.hydraulic_pressure = 185.4 bar
  │
  ▼
Operating Condition = HIGH_LOAD
  │
  ▼
Pressure Deviation = +8.2%
```

Cada transformação acrescenta significado sem destruir a identidade e a rastreabilidade da informação original.

---

### 6. Processing Responsibilities

O Processing Service poderá assumir responsabilidades como:

*Validation*

Verificação de consistência adicional necessária ao processamento.

.

*Transformation*

Conversão ou reorganização da informação para uma nova finalidade.

.

*Contextualization*

Associação da observação a informações necessárias para interpretação operacional.

.

*Correlation*

Relacionamento entre eventos ou variáveis quando necessário para produzir uma nova informação.

.

*Derivation*

Produção de novas informações calculadas a partir dos eventos recebidos.

```text
Telemetry
    │
    ▼
Processing
    │
    ├── Validate
    ├── Transform
    ├── Contextualize
    ├── Correlate
    └── Derive
            │
            ▼
      New Information
```

Essas responsabilidades deverão permanecer limitadas ao processamento informacional.

O Processing Service não deverá assumir responsabilidades pertencentes à aquisição, persistência ou analytics.

---

### 7. Near Real-Time Processing

O IMS considera Near Real Time uma propriedade end-to-end do fluxo informacional.

A latência deverá ser observada desde a ocorrência do fenômeno industrial até a disponibilização da informação.

```text
t0
Industrial Event
      │
      ▼
t1
OPC UA Acquisition
      │
      ▼
t2
Kafka Publication
      │
      ▼
t3
Event Consumption
      │
      ▼
t4
  Processing
      │
      ▼
t5
Processed Information Available
```

Conceitualmente:

```text
End-to-End Latency = t5 - t0
```

O número de componentes da arquitetura não define isoladamente se um fluxo é ou não Near Real Time.

O requisito relevante é se a latência total atende à finalidade operacional da informação.

Os limites quantitativos de latência serão definidos posteriormente conforme os casos de uso e medições da implementação.

---

### 8. Minimal Processing Path

Para preservar baixa latência e simplicidade, o IMS evitará cadeias desnecessárias de processamento intermediário.

Não será adotado inicialmente um modelo como:

```text
Kafka
  │
  ▼
Processor A
  │
  ▼
Kafka
  │
  ▼
Processor B
  │
  ▼
Kafka
  │
  ▼
Processor C
```

quando a mesma responsabilidade puder ser atendida por uma capacidade de processamento coesa.

A implementação inicial privilegiará:

```text
Kafka
  │
  ▼
IMS Processing Service
  │
  ▼
Kafka
```

A separação futura de processadores somente deverá ocorrer quando existir justificativa relacionada a:

- responsabilidade de domínio;
- escalabilidade independente;
- isolamento de falhas;
- requisitos distintos de processamento;
- ciclo de vida independente.

> **Cada etapa de processamento deve justificar sua existência.**

---

### 9. Technology Decision

*Python Kafka Processing Service*

> **O processamento contínuo inicial do IMS será implementado como um serviço Python capaz de consumir eventos do Apache Kafka, processá-los e publicar novas informações quando necessário.**

O serviço seguirá conceitualmente o fluxo:

```text
Consume
   │
   ▼
Process
   │
   ▼
Publish
```

Arquiteturalmente:

```text
Telemetry Event
       │
       ▼
Apache Kafka
       │
       ▼
Python Processing Service
       │
       ├── Validation
       ├── Transformation
       ├── Contextualization
       ├── Correlation
       └── Derivation
       │
       ▼
Enriched / Derived Event
       │
       ▼
Apache Kafka
```

A escolha preserva o ecossistema de desenvolvimento do IMS e permite que os fundamentos do Kafka permaneçam explícitos durante a implementação.

O Processing Service deverá atuar simultaneamente como:

- **Kafka Consumer**, para receber os eventos;
- **Processing Component**, para executar a lógica informacional;
- **Kafka Producer**, quando uma nova informação precisar ser publicada.

---

### 10. Kafka Fundamentals Preservation

A implementação deliberadamente evitará inicialmente abstrações avançadas de stream processing.

Essa decisão permitirá que conceitos fundamentais do Apache Kafka permaneçam explícitos no IMS, incluindo:

- producers;
- consumers;
- topics;
- partitions;
- consumer groups;
- offsets;
- replay.

```text
Kafka Topic
telemetry
    │
    ▼
Consumer Group
ims-processing
    │
    ▼
Python Processing Service
    │
    ▼
Kafka Producer
    │
    ▼
Kafka Topic
enriched-events
```

Essa abordagem mantém a implementação simples sem remover os princípios de Event-Driven Architecture definidos no ADR-01.

---

### 11. Process → Publish

O Processing Service não deverá persistir diretamente as informações processadas como parte de sua responsabilidade principal.

Quando uma nova informação relevante for produzida, ela deverá ser publicada novamente no event stream.

```text
Kafka
  │
  ▼
Processing Service
  │
  ▼
Enriched Event
  │
  ▼
Kafka
  │
  ├──► Persistence Consumer
  ├──► Analytics Consumer
  └──► Future Consumers
```

Essa decisão preserva o desacoplamento entre processamento e utilização da informação.

O Processing Service não precisa conhecer os consumidores downstream.

> **Process → Publish. Consumers decide how to use.**

A persistência continuará sendo responsabilidade das capacidades definidas no ADR-03.

---

### 12. Event Contracts

Eventos produzidos pelo Processing Service deverão respeitar as decisões estabelecidas no ADR-04.

Isso inclui:

- contrato explícito;
- identificação do evento;
- versionamento;
- temporalidade;
- proveniência;
- contexto mínimo;
- validação estrutural.

```text
Telemetry Contract
       │
       ▼
   Processing
       │
       ▼
Derived Information
       │
       ▼
Derived Event Contract
       │
       ▼
     Kafka
```

Um evento derivado representa uma nova informação e poderá possuir contrato próprio quando sua semântica justificar essa distinção.

A transformação não deverá romper a rastreabilidade em relação às informações que deram origem ao resultado.

---

### 13. Temporal Processing

O IMS deverá preservar a distinção entre:

- **Event Time** — momento em que o acontecimento ocorreu no processo;
- **Processing Time** — momento em que o IMS processou o evento.

```text
Industrial Process
       │
       │ Event Time
       ▼
Observation
       │
       ▼
     Kafka
       │
       │ Processing Time
       ▼
Processing Service
```

Quando uma transformação depender da sequência temporal real dos acontecimentos industriais, o Event Time deverá ser utilizado como referência conceitual.

A implementação inicial não introduzirá mecanismos avançados de event-time processing, watermarks ou gerenciamento distribuído de janelas sem que exista requisito correspondente.

Essa capacidade permanece como possibilidade de evolução.

---

### 14. Processing State

Determinadas transformações poderão necessitar de pequeno estado temporário.

Por exemplo:

```text
t1 → pressure = 180
t2 → pressure = 183
t3 → pressure = 187
t4 → pressure = 192
```

Uma sequência pode permitir derivações que uma observação isolada não permite.

```text
Events
  │
  ▼
Processing Service
  │
  ├── Recent Values
  ├── Simple Window
  └── Temporary Context
          │
          ▼
    Derived Information
```

O IMS permitirá estado local limitado quando necessário ao requisito atual.

Entretanto, essa decisão não equivale à adoção de uma arquitetura distribuída de stateful stream processing.

Caso o projeto passe a exigir:

- grandes volumes de estado;
- janelas temporais complexas;
- joins entre múltiplos streams;
- event-time avançado;
- recuperação distribuída de estado;
- processamento paralelo stateful;

uma nova decisão arquitetural deverá avaliar a introdução de uma engine especializada.

---

### 15. Relationship with Analytics

O Processing Service não assumirá as responsabilidades da camada de Analytics definida no ARCH-06.

A fronteira conceitual será:

```text
Telemetry
    │
    ▼
Processing
    │
    ▼
Contextualized /
Derived Information
    │
    ▼
Analytics
    │
    ▼
Knowledge /
Decision Support
```

O processamento produz e contextualiza informação.

Analytics utiliza informações contextualizadas para responder perguntas analíticas e apoiar decisões.

Essa separação evita que regras analíticas, dashboards ou decisões gerenciais sejam incorporadas indevidamente ao pipeline de processamento.

---

## 16. Rationale

A decisão procura equilibrar três necessidades:

```text
        Architectural Quality
                 │
                 │
Simplicity ──────┼────── Near Real Time
                 │
                 ▼
      Python Processing Service
```

O IMS necessita de processamento contínuo para materializar Progressive Information Enrichment.

Entretanto, o domínio atual não exige uma engine distribuída especializada.

A utilização de um serviço Python como Consumer e Producer Kafka permite:

- manter processamento Near Real Time;
- preservar desacoplamento;
- aprofundar os fundamentos do Kafka;
- reduzir complexidade operacional;
- manter coerência tecnológica;
- permitir evolução futura.

A arquitetura é preparada para evoluir sem implementar capacidades que o domínio ainda não exige.

---

### 17. Consequences

*17.1 - Positive*

A decisão proporciona:

- processamento contínuo;
- baixa complexidade inicial;
- aderência ao ecossistema Python;
- desacoplamento entre processamento e persistência;
- materialização do Progressive Information Enrichment;
- geração controlada de eventos derivados.

*17.2 - Negative*

A decisão implica:

- ausência inicial de state stores distribuídos;
- ausência de windowing avançado;
- ausência de joins complexos entre streams;
- necessidade de implementar explicitamente parte do comportamento do consumer e producer;
- estado local com capacidade limitada;
- necessidade futura de evolução caso o workload se torne significativamente mais complexo.

*17.3 - Risks / Trade-offs*

A implementação simplificada possui menos capacidades nativas do que uma engine especializada de stream processing. Esse trade-off é conscientemente aceito.

> **O IMS aceita capacidades iniciais mais simples de stream processing para preservar clareza arquitetural, reduzir complexidade e permitir evolução orientada por requisitos reais.**

---

### 18. Boundaries

Este ADR não define:

- lógica definitiva de processamento;
- regras completas de contextualização;
- nomes definitivos dos tópicos Kafka;
- quantidade de partitions;
- configuração dos consumer groups;
- política definitiva de commits de offsets;
- estratégia completa de retry;
- SLAs quantitativos de latência;


Esses elementos serão definidos pelo Event Model, Data Model, implementação ou ADRs posteriores quando possuírem relevância arquitetural própria.

---

### 19. Related Architecture

| Documento | Relação |
|---|---|
| **IPEM-07** | Estabelece o Telemetry Model |
| **IPEM-08** | Define Event Model e preservação do conhecimento de engenharia |
| **IPEM-09** | Estabelece contexto operacional como base para interpretação |
| **ARCH-00** | Estabelece tecnologia como consequência da arquitetura |
| **ARCH-02** | Define Progressive Information Enrichment |
| **ARCH-03** | Define comunicação através de eventos |
| **ARCH-04** | Distribui capacidades conforme responsabilidade |
| **ARCH-06** | Define Analytics e disponibilização de conhecimento |
| **ADR-01** | Define Event-Driven Integration e Apache Kafka |
| **ADR-02** | Define Industrial Data Acquisition |
| **ADR-03** | Define Industrial Data Persistence |
| **ADR-04** | Define Industrial Information Contracts |

---

### 20. Considerações Finais

O ADR-05 estabelece que o IMS transformará eventos industriais através de processamento contínuo, preservando baixa latência, desacoplamento e simplicidade de implementação.

A arquitetura não introduzirá camadas intermediárias sem responsabilidade explícita e não adotará inicialmente uma engine especializada de stream processing.

```text
Siemens S7-1500
        │
      OPC UA
        │
        ▼
Acquisition Service
        │
        ▼
  Telemetry Event
        │
        ▼
  Apache Kafka
        │
        ▼
Python Processing Service
        │
        ├── Validate
        ├── Transform
        ├── Contextualize
        ├── Correlate
        └── Derive
        │
        ▼
Enriched / Derived Event
        │
        ▼
  Apache Kafka
        │
        ├──► Persistence
        ├──► Analytics
        └──► Other Consumers
```

O processamento deixa de ser apenas uma transformação técnica e passa a representar uma etapa de evolução da informação industrial.

Ao mesmo tempo, sua implementação permanece proporcional ao problema atual.

> **O IMS começa simples, preserva seus princípios e evolui quando a Engenharia justificar a evolução.**
