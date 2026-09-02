### 1. Contexto

O DM-06 estabelece a estrutura lógica das informações do IMS por meio de entidades, identidades, relacionamentos e responsabilidades.

O DM-07 materializa essa estrutura em um **modelo físico de persistência**, definindo como as entidades serão organizadas e representadas no PostgreSQL sem alterar o significado estabelecido pelos modelos anteriores.

> **Physical structure must preserve logical meaning.**

O modelo físico representa a implementação da estrutura lógica, e não uma redefinição do domínio industrial.

---

### 2. Princípio de Modelagem

O modelo físico segue a progressão:

```text
Conceptual Meaning
       │
       ▼
Logical Structure
       │
       ▼
Physical Structure
       │
       ▼
  Implementation
````
Decisões físicas poderão otimizar armazenamento, integridade e acesso, desde que preservem as responsabilidades semânticas estabelecidas pelo modelo lógico.

---

### 3. Organização Física

PostgreSQL será utilizado como principal persistência estruturada para informações operacionais e analíticas consultáveis do IMS.

A organização física será orientada por responsabilidade informacional:
````
PostgreSQL
│
├── industrial
├── telemetry
├── context
└── analytics
````
Estrutura inicial:
````
industrial.process
industrial.asset
industrial.variable
industrial.source
industrial.variable_source

telemetry.telemetry
telemetry.event
telemetry.event_evidence

context.context_definition
context.context_instance

analytics.kpi_definition
analytics.kpi_result
````
Os schemas representam domínios de responsabilidade e não estágios de processamento.

> Physical organization should reflect information responsibility.

O armazenamento histórico de longo prazo permanece responsabilidade do ADLS, conforme estratégia definida no ADR-03.

---

### 4. Identity and Relationships

As identidades lógicas do DM-06 serão materializadas por identificadores físicos próprios.

A estratégia inicial utiliza UUID para as principais entidades:
````
process_id
asset_id
variable_id
source_id
telemetry_id
event_id
context_definition_id
context_instance_id
kpi_definition_id
kpi_result_id
````
A estrutura industrial principal será materializada por PK/FK:
````
industrial.process
       │
       │ 1:N
       ▼
industrial.asset
       │
       │ 1:N
       ▼
industrial.variable
````
A hierarquia de Asset será implementada por autorreferência:
````
asset
│
├── asset_id
└── parent_asset_id ───► asset.asset_id
````
A relação entre Variable e Source será independente da identidade industrial:
````
variable
    │
    N
    │
variable_source
    │
    N
    ▼
 source
````
variable_source poderá preservar validade temporal da representação técnica:
````
variable_source
│
├── variable_id
├── source_id
├── valid_from
└── valid_to
````
Assim, alterações na origem técnica não exigem alteração da identidade da Variable.

---

### 5. Telemetry and Event

Telemetry será a principal estrutura física para observações temporais.

Estrutura essencial:
````
telemetry.telemetry
│
├── telemetry_id
├── variable_id
├── occurred_at
├── ingested_at
├── value
└── quality
````
Metadata estável da Variable, como unidade de engenharia, não deverá ser repetida em cada observação quando essa duplicação não for necessária para preservar correção histórica.

> Do not duplicate stable metadata in high-volume observations unless historical correctness requires it.

Event será materializado separadamente:
````
telemetry.event
│
├── event_id
├── event_type
├── occurred_at
├── started_at
├── ended_at
└── correlation
````
Quando a relação entre Telemetry e Event precisar ser persistida para rastreabilidade:
````
telemetry.event_evidence
│
├── event_id
└── telemetry_id
````
Nem toda relação conceitual deverá obrigatoriamente possuir uma associação física.

---

### 6. Operational Context

Operational Context será materializado conforme a separação estabelecida no DM-06:
````
context.context_definition
        │
        │ 1:N
        ▼
context.context_instance
````
Estrutura essencial:
````
context.context_definition
│
├── context_definition_id
├── name
└── semantic_definition

context.context_instance
│
├── context_instance_id
├── context_definition_id
├── valid_from
├── valid_to
└── scope
````
A associação entre Telemetry, Event e Context não deverá ser materializada individualmente quando puder ser reconstruída de forma confiável por:
````
Temporal Validity
        +
 Semantic Scope
````
Isso evita relações redundantes em estruturas de alto volume.

---

### 7. Analytical Data

KPI será materializado por meio da separação entre definição e resultado:
````
analytics.kpi_definition
        │
        │ 1:N
        ▼
analytics.kpi_result
````
Estrutura essencial:
````
analytics.kpi_definition
│
├── kpi_definition_id
├── name
├── calculation_semantics
└── version

analytics.kpi_result
│
├── kpi_result_id
├── kpi_definition_id
├── scope
├── period_start
├── period_end
├── value
└── quality
````
Operational Context poderá ser associado ao resultado quando fizer parte de seu Analytical Grain.

A estrutura deverá preservar a distinção entre:
````
KPI Definition
      │
      └── what is measured?

KPI Result
      │
      └── measured value.
````
Dessa forma, diferentes resultados permanecem associados à mesma definição sem duplicar sua semântica.

---

### 8. Data Types and Integrity

Os tipos físicos serão escolhidos de acordo com o significado e o uso de cada atributo.

Diretrizes iniciais:

|   Responsabilidade	|                  Representação                   |
|---------------------|--------------------------------------------------|
| Identity	          | UUID                                             |
| Industrial Time     |	TIMESTAMPTZ                                      |
| Numeric Measure     |	NUMERIC ou DOUBLE PRECISION conforme necessidade |
| Boolean State       |	BOOLEAN                                          |
| Textual Information |	TEXT ou VARCHAR quando justificado               |
| Quality	            | Representação controlada                         |

TIMESTAMPTZ será utilizado para referências temporais que representem instantes, preservando uma interpretação temporal inequívoca.

Constraints físicas deverão proteger invariantes estruturais por meio de mecanismos como:
````
NOT NULL
FOREIGN KEY
UNIQUE
CHECK
````
quando aplicáveis.

Exemplo:
````
valid_to >= valid_from
````
Regras de engenharia ou interpretação operacional não deverão ser transferidas indiscriminadamente para constraints do banco.

---

### 9. Indexing and Partitioning

Indexação deverá ser orientada pelos padrões reais de acesso.

Consultas relevantes provavelmente envolverão:
````
Variable
Asset
Occurrence Time
Time Range
Context
KPI
````
Telemetry, devido ao seu volume e natureza temporal, poderá utilizar particionamento por tempo.

Exemplo conceitual:
````
telemetry
│
├── 2026-09
├── 2026-10
└── 2026-11
````
A granularidade das partições e os índices específicos deverão ser definidos com base em volume, retenção e workload observados.

> Optimize for observed access patterns, not hypothetical scale.

O modelo físico deverá permitir evolução conforme o comportamento real do IMS se torne conhecido.

---

### 10. Physical Data Model

A estrutura física principal pode ser representada como:
````
                         PostgreSQL
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
      industrial         telemetry           context
          │                  │                  │
       process            telemetry       context_definition
          │                  │                  │
        asset              event          context_instance
          │
       variable
          │
   variable_source
          │
        source


                         analytics
                             │
                      kpi_definition
                             │
                         kpi_result
````
A persistência de longo prazo permanece separada:
````
Operational / Queryable Data
          │
          ▼
      PostgreSQL

Long-Term Historical Data
          │
          ▼
         ADLS
````
O modelo físico preserva as responsabilidades estabelecidas pelos modelos conceitual e lógico sem transformar a tecnologia de persistência em definição do domínio.

---

### 11. Boundaries

O DM-07 não define:

* scripts SQL;
* valores definitivos de constraints;
* granularidade definitiva de particionamento;
* estratégia física detalhada no ADLS;
* estruturas Avro;
* Kafka Topics;
* payloads de eventos;
* views ou materialized views.

Essas decisões pertencem à implementação, operação ou especificações técnicas correspondentes.

---

### 12. Related Engineering and Architecture

| Documento	|                                Relação                                      |
|--------|--------------------------------------------------------------------------------|
| DM-01	 | Define as entidades fundamentais do domínio industrial                         |
| DM-02	 | Estabelece identidade independente de localização técnica                      |
| DM-03	 | Define temporalidade, qualidade e identidade das ocorrências                   |
| DM-04	 | Define Operational Context, validade temporal e escopo                         |
| DM-05	 | Define KPI, Analytical Grain e rastreabilidade analítica                       |
| DM-06	 | Estabelece entidades, relacionamentos e estrutura lógica                       |
| ADR-03 | Define PostgreSQL e ADLS como responsabilidades complementares de persistência |
| ADR-04 | Define contratos de informação independentes da persistência                   |

---

### 13. Considerações Finais

O DM-07 materializa fisicamente as decisões construídas ao longo da família Data Model.
````
Conceptual
    │
    ▼
 Identity
    │
    ▼
 Temporal
    │
    ▼
 Context
    │
    ▼
 Analytical
    │
    ▼
 Logical
    │
    ▼
 Physical
````
PostgreSQL representa a persistência estruturada operacional e analítica do IMS, enquanto o armazenamento histórico de longo prazo permanece desacoplado.

Schemas, identidades, relacionamentos, temporalidade e estruturas analíticas são organizados fisicamente sem alterar o significado industrial estabelecido pelos modelos anteriores.

As otimizações deverão evoluir a partir de requisitos e workloads reais, evitando complexidade antecipada.
