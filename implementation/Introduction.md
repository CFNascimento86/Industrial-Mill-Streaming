### 1. Contexto

As famílias IPEM, ARCH, ADR e DM estabeleceram o domínio industrial, a arquitetura, as principais decisões técnicas e o modelo de informação do IMS.

O Implementation Design inicia a transição entre essas definições de engenharia e sua materialização em componentes executáveis.

Seu objetivo é definir:

* componentes de software;
* responsabilidades;
* dependências;
* fluxo de informação;
* organização inicial do repositório;
* primeiro incremento executável.

O Implementation Design deverá orientar a implementação sem impedir sua evolução conforme restrições concretas forem identificadas.

---

### 2. Posicionamento da Implementação

O IMS será tratado como uma **implementação de referência executável de Engenharia de Dados Industrial**, projetada para integração com ambiente Siemens S7-1500.

Sua arquitetura industrial principal considera:

```text
Siemens S7-1500
      │
      ▼
Acquisition Service
      │
      ▼
Apache Kafka
      │
      ▼
Industrial Data Services
```

Ferramentas utilizadas para desenvolvimento, testes e reprodução do ambiente não fazem parte da arquitetura industrial conceitual do IMS.

Dessa forma, geração sintética de dados será tratada como **Engineering Tooling**, e não como fonte industrial oficial do sistema.

---

### 3. Component Map

A arquitetura executável inicial do IMS será composta por:

```text
                         SIEMENS S7-1500
                                │
                                ▼
                     Acquisition Service
                                │
                                ▼
                          Apache Kafka
                                │
                 ┌──────────────┼──────────────┐
                 │              │              │
                 ▼              ▼              ▼
           Processing     Persistence     Other Consumers
             Service        Service
                 │              │
                 ▼              ▼
          Derived Events    PostgreSQL


Contracts ───────────────► Apicurio Registry

Platform Metrics ────────► Prometheus
                                 │
                                 ▼
                              Grafana

Long-Term History ─────────────► ADLS
```

Cada componente deverá possuir responsabilidade claramente delimitada.

---

### 4. Industrial Source

A fonte industrial de referência do IMS será o: *Siemens S7-1500*

A fonte representa a infraestrutura OT responsável por disponibilizar observações originadas no processo industrial.

A arquitetura do IMS não deverá depender da forma específica como ambientes de desenvolvimento reproduzem essas observações.

```text
Industrial Source
       │
       ▼
Siemens S7-1500
       │
       ▼
Acquisition Service
```

---

### 5. Acquisition Service

Responsabilidade:

> **Adquirir informações da fonte industrial definida e convertê-las em eventos de Telemetry compatíveis com os contratos do IMS.**

Fluxo:

```text
Industrial Source
       │
       ▼
Acquisition Adapter
       │
       ▼
Normalization
       │
       ▼
Telemetry Event
       │
       ▼
     Kafka
```

A implementação de referência utilizará um adapter compatível com o Siemens S7-1500.

A responsabilidade de aquisição deverá permanecer isolada das demais camadas do IMS.

O Acquisition Service não deverá assumir responsabilidades de:

* analytics;
* persistência;
* contextualização avançada;
* geração de KPI;
* armazenamento histórico.

---

### 6. Event Backbone

Apache Kafka será o backbone de eventos do IMS.

Sua responsabilidade será transportar informações entre componentes independentes.

```text
Producer
   │
   ▼
Kafka Topic
   │
   ▼
Consumer Group
```

Kafka não representa:

* banco de dados industrial;
* Data Lake;
* historian de longo prazo;
* modelo semântico;
* camada analítica.

A topologia continuará orientada por responsabilidade informacional, conforme ADR-06.

---

### 7. Processing Service

Responsabilidade:

> **Consumir eventos industriais, aplicar transformações, contextualização e derivação de informação e produzir novos eventos quando necessário.**

Fluxo conceitual:

```text
Telemetry
    │
    ▼
Validation
    │
    ▼
Transformation
    │
    ▼
Contextualization
    │
    ▼
Derived Information
```

A implementação inicial será baseada em serviço Python consumer-producer.

Frameworks adicionais de stream processing somente deverão ser introduzidos quando requisitos concretos justificarem sua utilização.

---

### 8. Persistence Service

Responsabilidade:

> **Consumir informações persistíveis e materializá-las no PostgreSQL de maneira consistente e idempotente.**

```text
Kafka
  │
  ▼
Persistence Service
  │
  ├── Validation
  ├── Idempotency
  └── Persistence
          │
          ▼
      PostgreSQL
```

A separação entre Processing e Persistence deverá impedir que regras de transformação fiquem acopladas à tecnologia de armazenamento.

O PostgreSQL permanecerá responsável pelos dados operacionais e analíticos consultáveis.

---

### 9. Information Contracts

Os contratos de informação serão independentes dos serviços produtores e consumidores.

Estrutura conceitual:

```text
contracts/
└── avro/
    ├── telemetry/
    ├── event/
    └── context/
```

Apicurio Registry será responsável pela gestão dos contratos e de sua compatibilidade.

```text
Producer
   │
   ▼
Avro Contract
   │
   ▼
Apicurio Registry
   │
   ▼
Consumer
```

> **The contract belongs to the information, not to the producer.**

---

### 10. Service Decoupling

Serviços não deverão depender diretamente da disponibilidade runtime uns dos outros.

Evitar:

```text
Acquisition ─────► Processing
Processing  ─────► Persistence
```

Adotar:

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

Essa separação preserva desacoplamento, escalabilidade independente e capacidade de replay.

---

### 11. Delivery Semantics

Os consumers do IMS deverão respeitar as decisões estabelecidas no ADR-06:

```text
At-Least-Once
      │
      ├── Idempotent Processing
      ├── Bounded Retry
      ├── Controlled Offset Commit
      └── Dead Letter Topic
```

Fluxo de erro:

```text
Event
 │
 ▼
Consumer
 │
 ├── Success
 │      │
 │      ▼
 │   Commit Offset
 │
 └── Failure
        │
        ▼
      Retry
        │
        ├── Success ───► Commit Offset
        │
        └── Exhausted
                │
                ▼
               DLQ
```

Offsets deverão representar processamento concluído, e não apenas mensagem recebida.

---

### 12. Idempotency

Idempotência será particularmente importante nos componentes que produzem efeitos persistentes.

```text
Event
  │
  ▼
Persistence Service
  │
  ├── Already persisted?
  │        │
  │        └── Yes → Ignore safely
  │
  └── No
       │
       ▼
    Persist
```

O mesmo evento processado novamente não deverá gerar efeitos persistentes duplicados.

---

### 13. Platform Observability

Desde as primeiras implementações, cada serviço deverá fornecer pelo menos:

```text
Health
Metrics
Structured Logs
```

Prometheus será responsável pela coleta de métricas.

Grafana será utilizado para visualização da saúde operacional da plataforma.

Sinais prioritários incluem:

* service availability;
* Kafka consumer lag;
* throughput;
* processing latency;
* error rate;
* retry count;
* DLQ count.

Structured Logs deverão permitir correlação entre processamento e eventos.

Exemplos de campos:

```text
service_name
telemetry_id
event_id
correlation_id
event_type
processing_result
processing_duration
```

OpenTelemetry e distributed tracing permanecem como evolução futura.

---

### 14. Engineering Tooling

Ferramentas de desenvolvimento serão mantidas separadas da arquitetura industrial principal.

Entre elas estará um:

*Industrial Data Generator*

Sua responsabilidade será reproduzir de forma controlada comportamentos compatíveis com o domínio da Moenda para:

* desenvolvimento;
* testes;
* validação;
* demonstração;
* reprodutibilidade do projeto.

Estrutura sugerida:

```text
tools/
└── industrial-data-generator/
    ├── src/
    ├── scenarios/
    └── tests/
```

O gerador não deverá ser apresentado como componente da arquitetura industrial.

```text
ENGINEERING TOOLING

Industrial Data Generator
          │
          └── Development / Testing / Reproducibility
```

> **The IMS does not depend conceptually on simulated industrial infrastructure.**

---

### 15. Repository Structure

A organização inicial do repositório será:

```text
ims/
│
├── services/
│   ├── acquisition/
│   │   ├── src/
│   │   ├── tests/
│   │   └── Dockerfile
│   │
│   ├── processing/
│   │   ├── src/
│   │   ├── tests/
│   │   └── Dockerfile
│   │
│   └── persistence/
│       ├── src/
│       ├── tests/
│       └── Dockerfile
│
├── contracts/
│   └── avro/
│       ├── telemetry/
│       ├── event/
│       └── context/
│
├── database/
│   ├── migrations/
│   └── seeds/
│
├── infrastructure/
│   ├── kafka/
│   ├── apicurio/
│   ├── postgres/
│   ├── prometheus/
│   └── grafana/
│
├── tools/
│   └── industrial-data-generator/
│       ├── src/
│       ├── scenarios/
│       └── tests/
│
├── docs/
│   ├── ipem/
│   ├── architecture/
│   ├── adr/
│   └── data-model/
│
├── tests/
│   └── integration/
│
├── docker-compose.yml
├── .env.example
├── Makefile
└── README.md
```

A estrutura poderá evoluir conforme responsabilidades reais emergirem durante a implementação.

---

### 16. Shared Code

O IMS não deverá criar inicialmente uma biblioteca genérica `shared`, `common` ou `utils`.

Responsabilidades compartilhadas somente deverão ser extraídas quando demonstrarem estabilidade e reutilização real.

Possíveis candidatos futuros:

```text
libs/
└── ims_common/
```

para responsabilidades como:

* contract serialization;
* configuration;
* logging conventions.

> **Share stable abstractions, not convenient code.**

---

### 17. Configuration

Configurações deverão permanecer externas ao código.

Exemplos:

```text
KAFKA_BOOTSTRAP_SERVERS
SCHEMA_REGISTRY_URL

POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
```

O repositório poderá conter:

```text
.env.example
```

Credenciais reais e informações sensíveis não deverão ser versionadas.

---

### 18. Runtime

Docker será utilizado para empacotamento dos componentes.

Docker Compose será utilizado como runtime inicial de desenvolvimento e implantação de referência.

```text
Docker Compose
│
├── Kafka
├── Apicurio Registry
├── PostgreSQL
├── Acquisition Service
├── Processing Service
├── Persistence Service
├── Prometheus
└── Grafana
```

A infraestrutura deverá materializar as fronteiras definidas pela arquitetura, sem introduzir orquestração desnecessária.

---

### 19. First Vertical Slice

O primeiro incremento executável será:

*M1 — First Industrial Event Flow*

Arquitetura validada:

```text
Industrial Source
      │
      ▼
Acquisition Service
      │
      ▼
Telemetry Contract
      │
      ▼
Apache Kafka
      │
      ▼
Persistence Service
      │
      ▼
  PostgreSQL
```

Durante desenvolvimento e testes, o Industrial Data Generator poderá fornecer observações equivalentes às esperadas da fonte industrial.

Essa substituição é exclusivamente operacional e não altera o modelo arquitetural.

---

### 20. M1 Success Criteria

O milestone estará concluído quando uma observação industrial puder atravessar:

```text
Process
  │
  ▼
Asset
  │
  ▼
Variable
  │
  ▼
Source
  │
  ▼
Telemetry Event
  │
  ▼
Kafka
  │
  ▼
Persistence
  │
  ▼
PostgreSQL
```

preservando pelo menos:

* industrial identity;
* source traceability;
* telemetry identity;
* occurrence time;
* ingestion time;
* value;
* quality.

O objetivo do M1 não será apenas demonstrar conectividade entre tecnologias.

Seu objetivo será demonstrar que o modelo industrial estabelecido pelo IMS permanece íntegro através de todo o fluxo executável.

---

### 21. Evolution

O Implementation Design não deverá ser tratado como especificação imutável.

Durante a implementação, novas restrições poderão justificar:

* refinamento das fronteiras dos serviços;
* alteração da organização do repositório;
* evolução dos contratos;
* novos ADRs;
* ajustes no Physical Data Model;
* novos mecanismos de observabilidade;
* novos consumidores;
* novas estratégias de processamento.

Alterações deverão ser incorporadas conscientemente, preservando rastreabilidade entre necessidade, decisão e implementação.

```text
Engineering Decision
        │
        ├──► Implementation
        │
        └──► Documentation Update
```

---

### 22. Considerações Finais

O Implementation Design estabelece a primeira decomposição executável do IMS.

A arquitetura industrial permanece centrada em:

```text
Industrial Source
       │
       ▼
Acquisition
       │
       ▼
Event Backbone
       │
       ▼
Processing / Persistence
       │
       ▼
Contextualized Industrial Information
```

Ferramentas de desenvolvimento permanecem explicitamente fora dessa identidade arquitetural.

Essa separação permite que o IMS seja simultaneamente:

* executável;
* reproduzível;
* testável;
* tecnologicamente verificável;
* independente de acesso permanente à infraestrutura OT.

O projeto deixa, portanto, de existir apenas como definição arquitetural e passa a possuir uma trajetória explícita de materialização.
