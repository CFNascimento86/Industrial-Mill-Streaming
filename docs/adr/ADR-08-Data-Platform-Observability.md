## ADR-08 — Data Platform Observability

| Campo             | Valor                                                          |
| ----------------- | -------------------------------------------------------------- |
| **Documento**     | ADR-08                                                         |
| **Título**        | Data Platform Observability                                    |
| **Versão**        | 1.0                                                            |
| **Status**        | Accepted                                                       |
| **Projeto**       | Industrial Mill Streaming — IMS                                |
| **Especificação** | Architecture Decision Records — ADR                            |
| **Derivação**     | ARCH-04 / ARCH-05 / ADR-01 / ADR-03 / ADR-05 / ADR-06 / ADR-07 |

---

### 1. Context

O Industrial Mill Streaming (IMS) é composto por diferentes serviços responsáveis por aquisição, integração, processamento, persistência e disponibilização de informações industriais.

À medida que essas capacidades passam a operar de forma distribuída, falhas podem ocorrer em diferentes pontos.

Exemplos incluem:

* indisponibilidade do Acquisition Service;
* perda de conectividade;
* falha de processamento;
* aumento da latência;
* indisponibilidade do PostgreSQL;
* indisponibilidade do Schema Registry.

Sem mecanismos de observabilidade, a identificação dessas condições dependeria principalmente de inspeção manual de logs ou percepção tardia dos efeitos produzidos downstream.

O IMS necessita, portanto, de uma capacidade arquitetural que permita verificar continuamente o estado operacional da própria plataforma.

---

### 2. Decision Drivers

A decisão considera os seguintes direcionadores:

* visibilidade operacional da plataforma;
* diagnóstico de falhas;
* monitoramento de Kafka;
* medição de Near Real Time;
* rastreabilidade de eventos;
* identificação de gargalos.

---

### 3. Scope Boundary

*Data Platform Observability ≠ Industrial Process Monitoring*

O ADR-08 estabelece observabilidade exclusivamente sobre a arquitetura de dados do IMS.

Seu escopo inclui questões como:

```text
Acquisition Service está disponível?

Kafka está recebendo eventos?

Processing Service está acompanhando o fluxo?

Eventos estão falhando?

PostgreSQL está disponível?

Qual é a latência end-to-end?

```

Não pertence ao escopo deste ADR interpretar condições como:

```text
Pressão hidráulica alta

Temperatura crítica

Vibração excessiva

Falha operacional da Moenda

Desvio de processo
```

Essas condições pertencem ao conhecimento do processo, às disciplinas responsáveis pela planta e ao Event Model estabelecido no IPEM.

```text
Industrial Process
        │
        │  Process Monitoring
        │  Engineering Rules
        │  Alarm Management
        ▼
──────────────────────────────────
        │
        │  Data Platform Boundary
        ▼
       IMS
        │
        ├── Service Health
        ├── Metrics
        ├── Logs
        ├── Kafka Lag
        ├── Processing Latency
        └── Platform Failures
```

> **O IMS observa sua capacidade de processar informação; não redefine como o processo industrial deve ser monitorado.**

---

### 4. Architectural Decision

*Observable Data Platform*

> **Todo componente executável do IMS deverá expor informações suficientes para que seu estado, desempenho e falhas possam ser identificados e correlacionados ao longo do fluxo de dados.**

A observabilidade deverá atravessar as principais capacidades da arquitetura.

```text
Acquisition
     │
     ▼
   Kafka
     │
     ▼
Processing
     │
     ▼
Persistence
     │
     ▼
PostgreSQL
```

Sobre esse fluxo deverão existir sinais operacionais relacionados a:

```text
Health

Metrics

Logs

Event Correlation
```

Esses sinais permitirão avaliar o comportamento da plataforma sem depender de inspeção manual.

---

### 5. Health

Health representa a capacidade de determinar se um componente está funcional e pronto para executar sua responsabilidade.

A arquitetura deverá distinguir:

```text
Process Running
```

de:

```text
Service Ready
```

Conceitualmente:

```text
Service
   │
   ▼
Process Started
   │
   ▼
Dependencies Available?
   │
   ├── No ───► Not Ready
   │
   ▼
  Yes
   │
   ▼
Healthy / Ready
```

Health checks deverão ser utilizados sempre que aplicável para componentes como:

* Acquisition Service;
* Processing Service;
* Persistence Consumer;
* Kafka;
* PostgreSQL;
* Schema Registry.

Essa decisão complementa a estratégia de runtime definida no ADR-07.

---

### 6. Metrics

Os componentes do IMS deverão produzir métricas capazes de representar volume, desempenho, disponibilidade e falhas da plataforma.

Exemplos conceituais incluem:

```text
events_received_total

events_processed_total

events_failed_total

events_published_total
```

As métricas definitivas serão estabelecidas conforme a implementação.

O objetivo não será medir tudo que tecnicamente possa ser medido.

---

### 7. Structured Logging

Logs de aplicação deverão possuir estrutura suficiente para permitir investigação e correlação.

Sempre que possível, o log deverá preservar elementos de contexto.

Conceitualmente:

```json
{
  "service": "ims-processing",
  "event_id": "...",
  "event_type": "...",
  "timestamp": "...",
  "level": "ERROR",
  "error": "..."
}
```

Os campos definitivos serão estabelecidos durante a implementação.

A decisão arquitetural é:

> **Logs devem transportar contexto operacional da plataforma suficiente para investigação técnica.**

Eles não deverão replicar integralmente o payload industrial quando isso não for necessário.

---

### 8. Event Correlation

O mesmo evento poderá atravessar diferentes componentes da arquitetura.

```text
Acquisition
     │
     ▼
   Kafka
     │
     ▼
Processing
     │
     ▼
   Kafka
     │
     ▼
Persistence
```

A plataforma deverá preservar identificadores suficientes para permitir correlação entre esses estágios.

Conceitualmente:

```text
event_id = abc123
       │
       ├── Acquisition
       │
       ├── Processing
       │
       └── Persistence
```

Essa correlação permitirá investigar:

* onde uma falha ocorreu;
* onde uma informação sofreu atraso;
* se um evento foi reprocessado;
* qual serviço produziu determinada informação derivada;
* qual evento originou um registro persistido.

Essa decisão utiliza a identidade estabelecida no ADR-04.

---

### 9. End-to-End Latency

Near Real Time será tratado como característica mensurável da plataforma.

O IMS deverá permitir medir conceitualmente:

```text
t0
Industrial Occurrence
      │
      ▼
Acquisition
      │
      ▼
    Kafka
      │
      ▼
  Processing
      │
      ▼
Persistence / Serving
      │
      ▼
     tN
```

Onde:

```text
End-to-End Latency = tN - t0
```

Essa métrica permitirá avaliar objetivamente se o fluxo informacional atende ao requisito operacional esperado.

O limite quantitativo aceitável será definido posteriormente conforme os casos de uso.

---

### 10. Kafka Consumer Lag

Consumer lag será tratado como um dos principais indicadores operacionais da arquitetura Kafka.

Conceitualmente:

```text
Kafka Partition

e1 ─ e2 ─ e3 ─ e4 ─ e5 ─ e6 ─ e7
                    ▲              ▲
                    │              │
             Consumer Offset    Latest Offset

                 <---- lag ---->
```

Crescimento contínuo do lag poderá indicar:

* processamento abaixo da taxa de ingestão;
* indisponibilidade de consumer;
* limitação computacional;
* gargalo no PostgreSQL;
* falha downstream;
* configuração inadequada de paralelismo.

O acompanhamento de lag deverá ser realizado por Consumer Group.

---

### 11. Throughput

O IMS deverá ser capaz de observar a taxa de eventos processados ao longo do fluxo.

Exemplos conceituais:

```text
Events / second acquired

Events / second published

Events / second processed

Events / second persisted
```

A comparação entre esses valores poderá auxiliar na identificação de gargalos.

```text
Acquisition   500 events/s
      │
      ▼
    Kafka     500 events/s
      │
      ▼
Processing    480 events/s
      │
      ▼
Persistence   470 events/s
```

Essas métricas deverão ser interpretadas juntamente com consumer lag e latência.

---

### 12. Error Rate

Falhas deverão ser observáveis como comportamento mensurável da plataforma.

Exemplos:

```text
processing_errors_total

publication_errors_total

persistence_errors_total

contract_validation_errors_total

opcua_connection_errors_total
```

A observabilidade deverá permitir identificar tanto eventos isolados quanto tendências de degradação.

```text
Normal Operation
      │
      ▼
Low Error Rate
      │
      ▼
Sudden Increase
      │
      ▼
Investigation
```

O objetivo é detectar degradação antes que ela se transforme em indisponibilidade prolongada.

---

### 13. Dead Letter Topic Observability

O envio de eventos para Dead Letter Topic, definido no ADR-06, deverá produzir sinais observáveis.

```text
Processing Failure
       │
       ▼
Bounded Retry
       │
       X
       ▼
      DLQ
       │
       ▼
Metric + Log
```

Devem ser observáveis, quando aplicável:

* quantidade de eventos enviados;
* taxa de crescimento;
* origem;
* tipo de evento;
* serviço responsável;
* natureza da falha.

Eventos em DLQ deverão permanecer sujeitos a investigação e recuperação.

---

### 14. Technology Decision - A

*Prometheus — Platform Metrics*

> **Prometheus será adotado como mecanismo inicial de coleta e armazenamento de métricas operacionais da plataforma IMS.**

A escolha considera:

* modelo orientado a métricas;
* integração com serviços containerizados;
* ecossistema aberto;
* facilidade de instrumentação;
* ampla utilização em ambientes distribuídos;
* integração com Grafana.

Conceitualmente:

```text
IMS Services
      │
      │ Metrics
      ▼
Prometheus
```

Os componentes deverão expor métricas relevantes para suas responsabilidades.

---

### 15. Technology Decision - B

*Grafana — Platform Visualization*

> **Grafana será adotado como ferramenta inicial de visualização das métricas operacionais do IMS.**

Conceitualmente:

```text
IMS Services
      │
      ▼
Prometheus
      │
      ▼
   Grafana
      │
      ▼
Platform Observability
```

O Grafana será utilizado para observar a **plataforma de dados**, e não como camada principal de Analytics.

Exemplos de visualizações adequadas:

```text
Kafka Consumer Lag

Events / Second

Processing Latency

Persistence Latency

Error Rate

DLQ Count

Service Availability
```

---

### 16. Grafana Boundary

O Grafana utilizado neste ADR não substitui a arquitetura analítica definida no ARCH-06.

A separação será:

```text
   Grafana
      │
      ▼
IMS Platform Health
```

enquanto:

```text
Industrial Analytics
      │
      ▼
Process / Operational Knowledge
```

Exemplos que não pertencem ao escopo principal do Grafana de plataforma:

```text
OEE da Moenda

Eficiência de Extração

Indicadores de Produção

Análise de Disponibilidade

Condições Operacionais
```

---

### 17. Structured Logging Strategy

A implementação inicial utilizará logs estruturados produzidos diretamente pelos serviços.

Conceitualmente:

```text
IMS Service
     │
     ▼
Structured Log
     │
     ▼
Container Runtime / Log Access
```

A arquitetura não adotará inicialmente uma plataforma completa de centralização de logs apenas para atender ao escopo atual.

Caso volume, quantidade de serviços ou necessidade de correlação justifiquem, uma solução centralizada poderá ser introduzida futuramente.

---

### 18. Initial Observability Stack

A implementação inicial deverá permanecer enxuta.

```text
IMS Services
   │
   ├── Health Checks
   │
   ├── Structured Logs
   │
   └── Metrics
           │
           ▼
       Prometheus
           │
           ▼
        Grafana
```

Essa composição é considerada suficiente para:

* avaliar disponibilidade;
* medir throughput;
* acompanhar consumer lag;
* medir latência;
* identificar falhas;
* monitorar DLQ;
* investigar serviços.

A arquitetura deverá evoluir somente quando novos requisitos justificarem capacidades adicionais.

---

### 19. Observability by Responsibility

Cada serviço deverá expor sinais relacionados à sua responsabilidade arquitetural.

*Acquisition Service*

Pode fornecer informações relacionadas a:

* estado da conexão OPC UA;
* eventos adquiridos;
* falhas de aquisição;
* latência de aquisição.

.

*Kafka*

Pode fornecer:

* throughput;
* consumer lag;
* disponibilidade;
* comportamento das partitions.

.

*Processing Service*

Pode fornecer:

* eventos consumidos;
* eventos processados;
* eventos derivados;
* falhas;
* latência de processamento.

.

*Persistence Consumer*

Pode fornecer:

* eventos persistidos;
* erros;
* tempo de persistência;
* backlog.

.

*PostgreSQL*

Pode fornecer:

* disponibilidade;
* conexões;
* comportamento de consultas relevantes;
* capacidade operacional.

A arquitetura não exige que todos os componentes publiquem as mesmas métricas.

---

### 20. Rationale

A decisão procura equilibrar:

```text
Visibility
    │
    │
Diagnosis ─────── Simplicity
    │
    ▼
Health Checks
     +
Structured Logs
     +
Prometheus
     +
Grafana
```

O IMS necessita tornar seu comportamento verificável sem criar uma plataforma de observabilidade mais complexa que o próprio sistema observado.

Prometheus e Grafana oferecem capacidade suficiente para medir os principais indicadores técnicos.

Logs estruturados fornecem contexto para investigação.

Health checks suportam operação dos serviços.

Distributed tracing permanece disponível como possibilidade evolutiva.

---

### 21. Consequences

*21.1 - Positive*

A decisão proporciona:

* visibilidade operacional;
* diagnóstico mais rápido;
* medição objetiva de Near Real Time;
* acompanhamento de Kafka;
* identificação de consumer lag;
* medição de throughput.

.
  
*21.2 - Negative*

A decisão introduz:

* novos componentes;
* armazenamento de métricas;
* necessidade de instrumentação;
* necessidade de definir métricas relevantes;
* disciplina de logs;
* manutenção de dashboards técnicos.

.

*21.3 - Risks / Trade-offs*

Observabilidade excessiva pode gerar:

* métricas sem finalidade;
* excesso de logs;
* dashboards sem uso;
* maior custo computacional;
* complexidade operacional desnecessária.

Esse trade-off será controlado pelo princípio:

> **Measure what supports an operational decision.**

O IMS aceita o custo de instrumentação necessário para tornar o comportamento da plataforma verificável, mas não buscará medir tudo que tecnicamente possa ser medido.

---

### 22. Boundaries

Este ADR não define:

* SLAs;
* políticas de retenção de métricas;
* infraestrutura centralizada de logs;
* monitoramento de processo;
* regras de alarmes industriais;
* OT Cybersecurity monitoring;
* KPIs de produção;
* indicadores gerenciais.

Esses elementos pertencem à implementação, Analytics, disciplinas industriais específicas ou ADRs posteriores quando houver necessidade arquitetural.

---

### 23. Related Architecture

| Documento   | Relação                                                     |
| ----------- | ----------------------------------------------------------- |
| **IPEM-08** | Delimita eventos industriais e conhecimento operacional     |
| **ARCH-04** | Define responsabilidades dos ambientes de execução          |
| **ARCH-05** | Estabelece confiança e rastreabilidade na plataforma        |
| **ARCH-06** | Separa Analytics industrial do estado técnico da plataforma |
| **ADR-01**  | Define Apache Kafka como backbone de eventos                |
| **ADR-03**  | Define persistência e recuperação                           |
| **ADR-04**  | Estabelece identidade e contratos dos eventos               |
| **ADR-05**  | Define Near Real-Time Continuous Processing                 |
| **ADR-06**  | Define consumer lag, DLQ, delivery e replay                 |
| **ADR-07**  | Define containers, health e runtime                         |

---

### 24. Considerações Finais

O ADR-08 estabelece que o IMS deverá ser capaz de tornar seu próprio comportamento operacional verificável.

A plataforma será observada por meio de health checks, métricas, logs estruturados e correlação de eventos.

Prometheus será utilizado para coleta de métricas.

Grafana fornecerá visualização operacional.

```text
                    IMS Platform

Acquisition ───────► Kafka ───────► Processing
    │                  │                 │
    │                  │                 │
    └────── Metrics / Health / Logs ─────┘
                       │
                       ▼
                  Prometheus
                       │
                       ▼
                    Grafana
                       │
                       ▼
              Platform Visibility
```

A observabilidade permitirá medir se a arquitetura realmente atende aos comportamentos esperados, incluindo throughput, consumer lag, falhas e latência end-to-end.

Ao mesmo tempo, o IMS preserva explicitamente a fronteira entre observabilidade técnica da plataforma e monitoramento do processo industrial.

> **A plataforma precisa compreender seu próprio estado antes que possamos confiar plenamente no estado das informações que ela entrega.**

> **Near Real Time deixa de ser uma promessa arquitetural e passa a ser uma característica mensurável.**
