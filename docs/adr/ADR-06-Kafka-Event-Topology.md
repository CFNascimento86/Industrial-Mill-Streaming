## ADR-06 — Kafka Event Topology and Delivery Semantics

| Campo             | Valor                                        |
| ----------------- | -------------------------------------------- |
| **Documento**     | ADR-06                                       |
| **Título**        | Kafka Event Topology and Delivery Semantics  |
| **Versão**        | 1.0                                          |
| **Status**        | Accepted                                     |
| **Projeto**       | Industrial Mill Streaming — IMS              |
| **Especificação** | Architecture Decision Records — ADR          |
| **Derivação**     | ARCH-03 / ARCH-05 / ADR-01 / ADR-04 / ADR-05 |

---

### 1. Context

O Industrial Mill Streaming (IMS) utiliza Apache Kafka como plataforma de event streaming responsável pela distribuição assíncrona das informações industriais entre capacidades desacopladas.

A adoção do Kafka, entretanto, não define automaticamente como tópicos, partições, consumidores, offsets e falhas de processamento devem ser organizados.

Uma topologia inadequada pode produzir:

* proliferação excessiva de tópicos;
* dependências entre produtores e consumidores;
* perda de significado informacional;
* dificuldade de governança;
* inconsistências de ordenação;
* complexidade operacional desnecessária.

O IMS necessita, portanto, de princípios explícitos para organizar sua topologia de eventos e estabelecer uma semântica de entrega coerente com os requisitos de confiabilidade e simplicidade do projeto.

---

### 2. Decision Drivers

A decisão considera os seguintes direcionadores:

* baixo acoplamento entre produtores e consumidores;
* governança dos eventos;
* preservação do significado industrial;
* ordenação quando necessária;
* suporte a múltiplos consumidores;
* replay;
* tolerância a falhas;
* idempotência.

---

### 3. Architectural Decision

*Domain-Oriented Event Topology*

> **A topologia Kafka do IMS será organizada pela responsabilidade e natureza informacional dos eventos, e não pela quantidade de tags, variáveis, equipamentos ou aplicações consumidoras.**

Os tópicos deverão representar conjuntos coerentes de acontecimentos industriais.

A arquitetura evitará modelos como:

```text
topic.pressure
topic.temperature
topic.motor_current
topic.bearing_temperature
topic.speed
topic.mill_01
topic.mill_02
```

quando essas divisões não representarem responsabilidades informacionais distintas.

Da mesma forma, o IMS não adotará um único tópico universal para todas as informações.

```text
industrial-data
```

A estratégia deverá buscar um nível de granularidade que preserve significado sem introduzir fragmentação excessiva.

---

### 4. Topic Design Principles

A definição dos tópicos deverá considerar:

* natureza do evento;
* ciclo de vida da informação;
* consumidores esperados;
* requisitos de ordenação;
* retenção;
* volume.

Uma organização conceitual inicial poderá distinguir, por exemplo:

```text
Apache Kafka
     │
     ├── Telemetry Events
     │
     ├── Contextualized Events
     │
     └── Derived / Process Events
```

Essa representação é conceitual.

O número definitivo de tópicos e suas nomenclaturas serão definidos durante a implementação conforme os contratos e workloads reais.

---

### 5. Topic Is Not a Data Layer

Os tópicos Kafka não representarão automaticamente camadas físicas de armazenamento.

O IMS evitará transportar para o event streaming nomenclaturas como:

```text
raw
bronze
curated
silver
gold
```

quando essas nomenclaturas representarem estágios de persistência.

Kafka possui responsabilidade distinta da arquitetura de armazenamento definida no ADR-03.

```text
Kafka
   │
   └── Streams of Events

PostgreSQL / ADLS
   │
   └── Persistence Responsibilities
```

Essa separação evita confundir evolução informacional com organização física de persistência.

---

### 6. Message Key and Ordering

Apache Kafka preserva ordenação dentro de uma partição.

Portanto, quando a ordem relativa dos eventos possuir significado para o processo, a escolha da chave deverá garantir afinidade adequada de particionamento.

```text
Related Events
      │
      ▼
Stable Message Key
      │
      ▼
Kafka Partition
      │
      ├── Event t1
      ├── Event t2
      └── Event t3
```

A arquitetura estabelece:

> **Eventos cuja ordem relativa possua significado deverão utilizar uma chave estável capaz de preservar afinidade de particionamento.**

Possíveis estratégias poderão considerar:

```text
asset_id

variable_id

asset_id + variable_id
```

A composição definitiva da chave será definida conforme o tipo de evento, requisitos de ordenação e comportamento de carga.

O IMS não exigirá ordenação global quando o domínio não a exigir.

---

### 7. Consumer Groups

Consumer Groups representarão responsabilidades independentes de consumo.

Conceitualmente:

```text
                    Apache Kafka
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
     Processing      Persistence     Analytics
   Consumer Group  Consumer Group  Consumer Group
```

Cada grupo deverá processar os eventos segundo sua própria responsabilidade.

Múltiplas instâncias dentro do mesmo grupo representarão paralelismo de uma única capacidade.

```text
Consumer Group
ims-processing
      │
  ┌───┼───┐
  ▼   ▼   ▼
 C1  C2  C3
```

A arquitetura estabelece:

> **Consumer Groups representam responsabilidades independentes; consumers dentro do mesmo grupo representam paralelismo da mesma responsabilidade.**

Essa distinção deverá ser preservada durante a implementação.

---

### 8. Delivery Semantics

*At-Least-Once Delivery*

> **O IMS adotará At-Least-Once como semântica predominante de processamento de eventos.**

Essa abordagem prioriza a redução do risco de perda silenciosa de informação, aceitando que determinados cenários possam resultar em reprocessamento.

Conceitualmente:

```text
Kafka Event
     │
     ▼
  Consumer
     │
     ▼
  Process
     │
     ├── Failure
     │      │
     │      └── Retry / Reprocessing
     │
     ▼
  Success
     │
     ▼
Offset Commit
```

A possibilidade de processamento duplicado deverá ser tratada por mecanismos de idempotência nas capacidades que produzam efeitos persistentes.

> **At-Least-Once + Idempotent Processing**

será o padrão predominante do IMS.

---

### 9. Offset Management

O offset representa o progresso lógico de processamento de um consumer.

```text
Partition

0 ─ 1 ─ 2 ─ 3 ─ 4 ─ 5
            ▲
            │
          Offset
```

O IMS estabelece:

> **O avanço do offset deverá representar processamento concluído, não apenas mensagem recebida.**

Conceitualmente:

```text
Consume
   │
   ▼
Process
   │
   ├── Failure
   │      │
   │      └── Processing not completed
   │
   ▼
Success
   │
   ▼
Commit
```

A política física de commit será definida posteriormente conforme a implementação dos consumers.

---

### 10. Idempotent Processing

A adoção de At-Least-Once implica possibilidade de reprocessamento.

Consumidores que produzam efeitos persistentes deverão ser projetados para lidar com eventos repetidos sem provocar inconsistências indevidas.

```text
Event
  │
  ▼
Consumer
  │
  ├── First Processing
  │
  └── Replay / Duplicate
           │
           ▼
     Idempotent Handling
```

A idempotência poderá utilizar, conforme o caso:

* identidade única do evento;
* controle de processamento;
* constraints de persistência;
* deduplicação;
* operações determinísticas.

A estratégia específica será definida durante o Data Model e a implementação.

---

### 11. Retry Strategy

Falhas temporárias não deverão resultar imediatamente no descarte ou isolamento definitivo do evento.

O IMS adotará uma estratégia conceitual de **bounded retry**.

```text
Processing Failure
       │
       ▼
Transient Failure?
     /      \
   YES      NO
    │        │
    ▼        ▼
 Retry    Controlled Failure
```

Retries deverão:

* possuir quantidade limitada;
* ser aplicados apenas quando houver possibilidade razoável de recuperação;
* evitar loops infinitos;
* preservar observabilidade sobre as falhas.

---

### 12. Dead Letter Topics

Eventos que não possam ser processados após a política controlada de tentativas deverão ser isolados para investigação.

```text
Kafka Event
    │
    ▼
Consumer
    │
    X
Processing Failure
    │
    ▼
Bounded Retry
    │
    X
Retries Exhausted
    │
    ▼
Dead Letter Topic
    │
    ▼
Investigation / Recovery
```

Uma Dead Letter Topic deverá preservar, quando possível:

* evento original;
* identidade;
* contrato;
* timestamp;
* origem;
* contexto mínimo de processamento.

Eventos enviados para DLQ permanecem sob responsabilidade operacional da plataforma.

---

### 13. Replay

Replay é uma capacidade arquitetural prevista do IMS.

Kafka permite reposicionar o progresso de consumo e reprocessar eventos ainda disponíveis conforme sua política de retenção.

```text
Kafka Partition

e1 ─ e2 ─ e3 ─ e4 ─ e5
              ▲
              │
       Current Position

Replay

e1 ─ e2 ─ e3 ─ e4 ─ e5
     ▲
     │
New Position
```

Replay poderá ser utilizado para:

* recuperação;
* correção de processamento;
* reconstrução de projeções;
* reprocessamento;
* testes controlados;
* evolução de lógica.

Consumidores que produzam efeitos persistentes deverão considerar replay em seu design.

---

### 14. Retention Principles

A retenção Kafka deverá suportar as necessidades de operação e replay.

Entretanto:

> **Kafka retention is not historical persistence.**

A responsabilidade pelo histórico de longo prazo permanece definida no ADR-03.

Os períodos definitivos de retenção deverão considerar:

* janela necessária de replay;
* volume de eventos;
* capacidade de armazenamento;
* recuperação operacional;
* custo;
* comportamento real da plataforma.

Não serão estabelecidos períodos arbitrários neste ADR.

---

### 15. Topic Naming Principles

Os nomes dos tópicos deverão representar responsabilidade e significado informacional.

O IMS evitará nomes acoplados a:

* bibliotecas;
* linguagem;
* consumer específico;
* banco de destino;
* container;
* implementação transitória.

Exemplos a evitar:

```text
python-processor-output
postgres-input
consumer-01-data
```

Uma nomenclatura informacionalmente orientada poderá assumir conceitualmente formas como:

```text
ims.<domain>.<event-category>
```

ou:

```text
ims.<context>.<event-type>
```

A convenção definitiva será estabelecida durante a implementação.

---

### 16. Initial Topology

A topologia inicial deverá permanecer proporcional ao escopo atual do IMS.

Conceitualmente:

```text
                   Apache Kafka
                        │
             ┌──────────┴──────────┐
             │                     │
             ▼                     ▼
      Telemetry Events       Derived Events
             │                     │
      ┌──────┼──────┐        ┌─────┼─────┐
      ▼      ▼      ▼        ▼     ▼     ▼
Processing Persist Other   Persist Analytics Other
```

Esse modelo não determina o número definitivo de tópicos.

Ele estabelece apenas que tópicos deverão representar responsabilidades informacionais suficientemente distintas para justificar sua existência.

---

### 17. Rationale

A decisão procura equilibrar:

```text
Information Governance
         │
         │
Reliability ─────── Simplicity
         │
         ▼
Domain-Oriented Kafka Topology
         +
At-Least-Once Delivery
         +
Idempotent Processing
```

A topologia orientada à responsabilidade informacional reduz fragmentação e preserva significado.

At-Least-Once reduz o risco de perda silenciosa.

Idempotência controla os efeitos do reprocessamento.

Bounded Retry permite recuperação de falhas transitórias.

DLQ isola eventos que exigem investigação.

Essas decisões proporcionam confiabilidade suficiente para o escopo atual sem introduzir semânticas transacionais ou topologias complexas prematuramente.

---

### 18. Consequences

*18.1 - Positive*

A decisão proporciona:

* menor proliferação de tópicos;
* melhor governança;
* consumer groups semanticamente coerentes;
* preservação de ordenação quando necessária;
* replay;
* tratamento explícito de falhas;
* reutilização dos eventos;
* escalabilidade.


*18.2 - Negative*

A decisão implica:

* necessidade de definir corretamente as message keys;
* possibilidade de eventos duplicados;
* necessidade de idempotência;
* necessidade de monitoramento de consumer lag;
* necessidade de tratamento de DLQ;
* disciplina sobre commits de offsets;
* responsabilidade adicional de governança da topologia.

*18.3 - Risks / Trade-offs*

At-Least-Once reduz o risco de perda, mas admite reprocessamento.

Uma topologia muito agregada pode misturar responsabilidades.

Uma topologia excessivamente fragmentada pode aumentar complexidade operacional.

Esse equilíbrio deverá ser continuamente avaliado conforme o volume e os casos de uso evoluírem.

> **O IMS aceita a possibilidade controlada de reprocessamento para reduzir o risco de perda silenciosa e preservar uma arquitetura Kafka simples e confiável.**

---

 ### 19. Boundaries

Este ADR não define:

* número e nomes definitivo de tópicos;
* quantidade de partitions;
* quantidade de brokers;
* períodos definitivos de retention;
* quantidade definitiva de retries;
* retry backoff;
* número de consumers;
* consumer concurrency.

Esses elementos serão definidos durante a implementação, dimensionamento ou por novos ADRs quando possuírem impacto arquitetural próprio.

---

### 20. Related Architecture

| Documento   | Relação                                                         |
| ----------- | --------------------------------------------------------------- |
| **IPEM-08** | Define Event Model e significado operacional dos eventos        |
| **ARCH-00** | Estabelece tecnologia como consequência da arquitetura          |
| **ARCH-03** | Define Communication Through Events                             |
| **ARCH-05** | Define confiança, rastreabilidade e governança                  |
| **ADR-01**  | Define Event-Driven Integration e Apache Kafka                  |
| **ADR-03**  | Distingue event retention de historical persistence             |
| **ADR-04**  | Define contratos e governança estrutural dos eventos            |
| **ADR-05**  | Define processamento contínuo e publicação de eventos derivados |

---

### 21. Considerações Finais

O ADR-06 estabelece como o Apache Kafka deverá ser utilizado como backbone de eventos do IMS sem transformar a plataforma em uma topologia excessivamente complexa.

Os tópicos serão organizados pela responsabilidade informacional.

Consumer Groups representarão capacidades independentes.

Message keys preservarão ordenação quando necessária.

At-Least-Once será adotado como semântica predominante, complementado por processamento idempotente.

Falhas transitórias serão tratadas por bounded retry, enquanto eventos persistentemente problemáticos serão isolados por Dead Letter Topics.

```text
Industrial Event
       │
       ▼
Information Contract
       │
       ▼
Apache Kafka
       │
       ├── Domain-Oriented Topic
       │
       ▼
Consumer Group
       │
       ▼
Process
       │
       ├── Success ─────► Commit
       │
       └── Failure
              │
              ▼
         Bounded Retry
              │
              └──► DLQ when required
```

A arquitetura preserva recursos avançados como exactly-once e Retry Topics para cenários futuros nos quais sua complexidade seja justificada por requisitos concretos.

> **Confiabilidade não significa eliminar todo reprocessamento; significa saber como detectá-lo, controlá-lo e recuperar-se dele.**
