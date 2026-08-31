### 1. Contexto

Os modelos anteriores definem o significado das principais entidades de informação do IMS, suas identidades, comportamento temporal, contexto operacional e representação analítica.

O DM-06 transforma essas definições conceituais em uma **estrutura lógica de dados**, estabelecendo entidades, responsabilidades, relacionamentos e cardinalidades sem assumir uma implementação física específica.

---

### 2. Princípio de Modelagem

O modelo lógico segue o princípio:

> **Meaning Before Structure**

A estrutura lógica deverá ser consequência do significado estabelecido nos modelos conceituais.

```text
Conceptual Meaning
       │
       ▼
Logical Structure
       │
       ▼
Physical Implementation
````
O DM-06 define como a informação é estruturada logicamente.

O DM-07 definirá como essa estrutura será materializada fisicamente.

---

### 3. Entidades Lógicas

O modelo lógico do IMS estabelece as seguintes entidades principais:

|     Entidade	     |                       Responsabilidade                                |
|--------------------|-----------------------------------------------------------------------|
| Process	           | Representar o processo industrial                                     |
| Asset	             | Representar elementos funcionais ou físicos participantes do processo |
| Variable	         | Representar propriedades industriais observáveis                      |
| Source	           | Representar a origem técnica de uma informação                        |
| Telemetry	         | Representar observações temporais de Variables                        |
| Event              | Representar ocorrências industriais significativas                    |
| Context Definition | Representar o significado de uma condição operacional                 |
| Context Instance	 | Representar uma ocorrência temporal dessa condição                    |
| KPI Definition	   | Representar a definição semântica de um indicador                     |
| KPI Result	       | Representar um resultado analítico produzido a partir dessa definição |

O desdobramento de Operational Context e KPI transforma distinções conceituais dos modelos anteriores em responsabilidades lógicas explícitas.
````
Operational Context
        │
        ├── Context Definition
        └── Context Instance


KPI
 │
 ├── KPI Definition
 └── KPI Result
````

---

### 4. Identidade Lógica

Cada entidade logicamente independente deverá possuir identidade própria e estável.

Conceitualmente:
````
Process            → process_id
Asset              → asset_id
Variable           → variable_id
Source             → source_id
Telemetry          → telemetry_id
Event              → event_id
Context Definition → context_definition_id
Context Instance   → context_instance_id
KPI Definition     → kpi_definition_id
KPI Result         → kpi_result_id
````
Esses identificadores representam responsabilidades lógicas.

O DM-06 não determina sua implementação como UUID, ULID, sequência numérica ou qualquer outro mecanismo físico.

Nomes, caminhos semânticos, endereços de PLC, OPC UA NodeIds, Kafka Topics ou referências de armazenamento não constituem identidade industrial.

---

### 5. Relacionamentos Centrais

A estrutura industrial principal permanece:
````
PROCESS
   │
   │ 1:N
   ▼
 ASSET
   │
   │ 1:N
   ▼
VARIABLE
   │
   │ 1:N
   ▼
TELEMETRY
````
Asset admite composição hierárquica:
````
ASSET
  │
  └── contains
         │
         ▼
       ASSET
````
Essa relação permite representar diferentes níveis funcionais sem criar entidades específicas para Equipment, Subsystem ou Component.

Variable poderá possuir associação com Source:
````
VARIABLE
    │
    └────────── SOURCE
````
Essa associação representa a ligação entre identidade industrial e representação técnica.

A cardinalidade física dessa relação não é definida neste documento.

---

### 6. Estrutura Temporal

Telemetry materializa logicamente uma observação temporal de uma Variable.

Sua responsabilidade lógica inclui:
````
Telemetry
│
├── Identity
├── Variable
├── Observation
├── Engineering Unit
├── Quality
├── Occurrence Time
└── Ingestion Time
````
Event representa uma ocorrência significativa:
````
Event
│
├── Identity
├── Event Type
├── Occurrence Time
├── Temporal Duration
└── Correlation
````
Um Event poderá representar uma ocorrência pontual ou um intervalo.

Telemetry e Event poderão possuir relações N:N quando semanticamente necessário.
````
TELEMETRY
     N
     │
     │ contributes to
     │
     N
   EVENT
````
O DM-06 reconhece essa relação sem determinar ainda sua materialização física.

---

### 7. Estrutura de Contexto

Operational Context é estruturado logicamente em duas responsabilidades:
````
CONTEXT DEFINITION
        │
        │ 1:N
        ▼
CONTEXT INSTANCE
````
Context Definition representa o significado da condição:
````
HIGH_LOAD
AUTOMATIC_OPERATION
STABLE_PRODUCTION
````
Context Instance representa quando essa condição esteve válida:
````
HIGH_LOAD
   │
   ├── 10:00 ───── 10:45
   └── 13:20 ───── 13:52
````
Uma Context Instance possui logicamente:
````
Context Instance
│
├── Identity
├── Context Definition
├── Temporal Validity
└── Semantic Scope
````
A associação de Telemetry ou Event com contexto poderá ser determinada por compatibilidade entre:
````
Temporal Validity
        +
 Semantic Scope
````
Não é exigida uma referência física de contexto em cada observação.

---

### 8. Estrutura Analítica

KPI é estruturado logicamente em:
````
KPI DEFINITION
      │
      │ 1:N
      ▼
  KPI RESULT
````
KPI Definition representa:
````
Meaning
Calculation Semantics
Calculation Version
````
KPI Result representa:
````
Value
Time Reference
Industrial Scope
Relevant Context
Analytical Quality
````
O resultado analítico possui granularidade determinada pela combinação de:
````
Industrial Scope
       +
Time Reference
       +
Relevant Context
       │
       ▼
Analytical Grain
````
Essa separação permite preservar a identidade e a definição do indicador independentemente dos resultados produzidos.

---

### 9. Modelo Lógico

O núcleo lógico do IMS pode ser representado como:
````
                         PROCESS
                            │
                            │ 1:N
                            ▼
                          ASSET
                            │
                     ┌──────┴──────┐
                     │ hierarchy   │
                     └──────► ASSET
                            │
                            │ 1:N
                            ▼
                         VARIABLE ◄──── SOURCE
                            │
                            │ 1:N
                            ▼
                        TELEMETRY
                            │
                            ├────────────► EVENT
                            │
                            │
                            └──── interpreted under ───┐
                                                       ▼
                                              CONTEXT DEFINITION
                                                       │
                                                       │ 1:N
                                                       ▼
                                               CONTEXT INSTANCE


                         KPI DEFINITION
                               │
                               │ 1:N
                               ▼
                           KPI RESULT
                               │
                      ┌────────┼────────┐
                      ▼        ▼        ▼
                    Scope     Time    Context
````
O modelo representa estrutura e relacionamentos lógicos.

Ele não representa obrigatoriamente um pipeline de processamento ou uma estrutura física de armazenamento.

---

### 10. Boundaries

O DM-06 não define:

* Primary Keys ou Foreign Keys físicas;
* tabelas PostgreSQL;
* schemas;
* índices;
* particionamento;
* constraints;
* estruturas Avro;
* Kafka Topics.

Essas decisões pertencem ao Physical Data Model e às respectivas decisões de implementação.

---

### 11. Related Engineering and Architecture

| Documento	|                    Relação                          |
|---------|-------------------------------------------------------|
| DM-01	  | Define as entidades fundamentais do modelo industrial |
| DM-02	  | Estabelece identidade industrial estável              |
| DM-03	  | Define Telemetry, Event e semântica temporal          |
| DM-04	  | Define Operational Context e sua aplicabilidade       |
| DM-05	  | Define KPI, granularidade e semântica analítica       |
| ARCH-02 | Estabelece Progressive Information Enrichment         |
| ADR-03  |	Define responsabilidades de persistência              |
| ADR-04  |	Define contratos de informação                        |
| ADR-05	| Define processamento e derivação de informações       |

---

### 12. Considerações Finais

O DM-06 transforma o modelo conceitual do IMS em uma estrutura lógica explícita.
````
Conceptual Model
       │
       ▼
Logical Entities
       │
       ▼
Relationships
       │
       ▼
Cardinalities
       │
       ▼
Logical Data Model
````
As decisões conceituais permanecem preservadas enquanto identidade, temporalidade, contexto e analytics passam a possuir responsabilidades estruturais claras.

O modelo lógico permanece independente de PostgreSQL, Kafka, Avro ou qualquer outra tecnologia de implementação.
