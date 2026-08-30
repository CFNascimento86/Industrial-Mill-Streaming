### 1. Contexto

Os modelos anteriores estabelecem identidade industrial, temporalidade e contexto operacional como dimensões explícitas da informação no IMS.

Entretanto, compreender o comportamento de um processo também exige transformar essas evidências em medidas capazes de representar desempenho e apoiar análise.

O DM-05 estabelece como **KPI representa informação analítica derivada**, preservando significado, referência temporal, escopo, contexto e rastreabilidade.

---

### 2. Princípios de Modelagem Analítica

O modelo estabelece cinco princípios fundamentais.

-> *KPI Is Derived Information*

KPI representa uma síntese analítica produzida a partir de informações industriais.

-> *Aggregation Is Not Meaning*

Uma operação matemática isolada não define, por si só, um indicador industrial.

-> *Context Qualifies Performance*

A interpretação de desempenho torna-se mais significativa quando realizada sob condições operacionais explícitas.

-> *Analytical Results Must Be Explainable*

Resultados derivados deverão preservar informação suficiente para compreender sua origem de cálculo.

-> *Comparability Requires Semantic Compatibility*

Resultados somente deverão ser comparados quando definição, escopo, referência temporal e contexto relevante forem semanticamente compatíveis.

---

### 3. KPI

*KPI* representa uma medida derivada, semanticamente definida e contextualizada, utilizada para avaliar determinado aspecto do desempenho industrial.

Conceitualmente:

```text
    Telemetry
        +
      Event
        +
Operational Context
        │
        ▼
    Derivation
        │
        ▼
       KPI
````

KPI não representa uma observação primária.

Ele sintetiza informações produzidas ou interpretadas ao longo do ciclo de vida dos dados industriais.

---

### 4. KPI Definition × KPI Result

O modelo distingue conceitualmente a definição de um indicador de seus resultados.

-> *KPI Definition*

Representa aquilo que está sendo medido e sua semântica analítica.

Exemplo:
````
KPI Definition

Extraction Efficiency
KPI Result
````
Representa um valor produzido a partir dessa definição em determinado escopo e referência temporal.

-> *KPI Result*
````
Extraction Efficiency = 94.7%

Scope:
Mill 01

Period:
08:00–09:00
````
Conceitualmente:
````
KPI Definition
      │
      └── what is measured
              │
              ▼
         KPI Result
              │
              └── measured value
````
O DM-05 não determina ainda se Definition e Result serão materializados como entidades físicas distintas.

---

### 5. KPI Identity

A definição de um KPI deverá possuir identidade semanticamente estável.

Essa identidade não deverá depender diretamente de:
````
SQL Query
Database Column
Dashboard Name
Power BI Measure
Application Code
````
Esses elementos representam implementações técnicas.

Conceitualmente:
````
KPI Identity
     │
     ├── Meaning
     ├── Scope
     ├── Definition
     └── Calculation Semantics
````
A implementação poderá evoluir sem necessariamente alterar o significado industrial do indicador.

---

### 6. Calculation Semantics and Versioning

A metodologia utilizada para calcular um KPI faz parte de sua interpretação.

Uma alteração técnica que preserve a mesma regra conceitual não implica necessariamente uma nova definição.

Entretanto, uma alteração material na semântica do cálculo deverá permanecer rastreável.
````
KPI Identity
     │
     ▼
KPI Definition
     │
     ▼
Calculation Version
````
Por exemplo:
````
Extraction Efficiency
        │
        ├── Calculation Version 1
        └── Calculation Version 2
````
Resultados produzidos sob metodologias semanticamente diferentes não deverão ser tratados como automaticamente equivalentes.

Essa separação preserva comparabilidade histórica e explicabilidade analítica.

---

### 7. Temporal Reference

Um KPI Result deverá possuir referência temporal.

Um valor isolado:
````
Extraction Efficiency = 94.7%
````
é analiticamente incompleto sem indicar a qual período ou ocorrência se refere.

A referência poderá representar, por exemplo:
````
Interval
Shift
Batch
Campaign
Rolling Window
Event-related Period
````
Exemplo:
````
08:00 ├───────────────────┤ 09:00

Extraction Efficiency
94.7%
````
Conceitualmente:
````
KPI Result
    │
    ├── Value
    ├── Time Reference
    └── Scope
````
> A KPI result without temporal reference is analytically incomplete.

---

### 8. Industrial Scope

Todo KPI Result deverá possuir um escopo industrial semanticamente reconhecível.

Por exemplo:
````
OEE = 82%
````
não possui significado completo sem indicar se representa:
````
Mill 01
Mill 02
Milling Process
Industrial Area
````
O escopo deverá relacionar o resultado às identidades industriais estabelecidas nos modelos anteriores.

Conceitualmente:
````
KPI Result
     │
     ├── Process
     ├── Asset
     └── broader analytical scope
````
Assim, a interpretação do indicador não dependerá exclusivamente de convenções presentes em dashboards ou estruturas de armazenamento.

---

### 9. KPI × Operational Context

Operational Context permite interpretar desempenho sob condições operacionais explícitas.

Por exemplo:
````
Extraction Efficiency
94.7%
````
poderá ser analisado como:
````
Extraction Efficiency
under Normal Load
````
ou:
````
Extraction Efficiency
under High Load
````
Conceitualmente:
````
KPI Result
     │
     │ evaluated under
     ▼
Operational Context
````
Isso permite evoluir de:
````
How much?
````
para:
````
How much, under which conditions?
````
Assim, diferentes contextos não exigem necessariamente a criação de diferentes indicadores.
````
                  ┌── Normal Load
                  │
Extraction        ├── High Load
Efficiency ───────┤
                  ├── Automatic Mode
                  │
                  └── Manual Mode
````
A identidade do KPI permanece preservada enquanto o contexto qualifica sua interpretação.

---

### 10. Analytical Grain

Todo resultado analítico possui um nível de granularidade que determina exatamente aquilo que representa.

Conceitualmente:
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
Exemplo:
````
Mill 01
08:00–09:00
High Load

Extraction Efficiency = 94.7%
````
representa um resultado diferente de:
````
Mill 01
Daily

Extraction Efficiency = 93.9%
````
O Analytical Grain estabelece a unidade semântica de cada resultado analítico.

Esse conceito será posteriormente utilizado para orientar a estrutura lógica dos dados analíticos.

---

### 11. KPI × Metric

Nem toda medida analítica representa necessariamente um KPI.

Por exemplo:
````
Average Hydraulic Pressure
185.2 bar
````
pode representar uma métrica analítica.

Enquanto:
````
Extraction Efficiency
94.7%
````
poderá representar um KPI quando associado a um objetivo relevante de desempenho industrial.

Conceitualmente:
````
ANALYTICAL MEASURE
        │
        ├── Metric
        │
        └── KPI
````
O DM-05 não introduz Metric como uma nova entidade fundamental do modelo conceitual.

A distinção estabelece apenas que:

> Not every analytical measure is a KPI.

KPI possui relevância operacional ou de negócio explicitamente reconhecida.

---

### 12. KPI × Event

Event e KPI podem representar informações derivadas, mas possuem naturezas distintas.
````
EVENT
   │
   └── significant occurrence


KPI
   │
   └── performance synthesis
````
Exemplo:
````
Event
High Load Condition Detected
````
não é equivalente a:
````
KPI
Extraction Efficiency = 91.3%
````
Events poderão contribuir para, delimitar ou contextualizar resultados analíticos.

---

### 13. Analytical Quality

A confiabilidade de um resultado analítico depende também da qualidade das evidências em sua derivação.

Por exemplo:
````
Telemetry
   │
   ├── GOOD
   ├── GOOD
   ├── BAD
   └── BAD
       │
       ▼
   Derivation
       │
       ▼
   KPI Result
````
Um resultado poderá existir matematicamente mesmo quando parte significativa de suas evidências possuir qualidade comprometida.

O modelo deverá permitir representar conceitualmente a confiabilidade do resultado.
````
KPI Result
    │
    ├── Value
    └── Analytical Quality / Confidence
````
O DM-05 não define categorias, percentuais ou algoritmos específicos para essa avaliação.

---

### 14. Analytical Traceability

Um resultado analítico deverá possuir rastreabilidade suficiente para explicar sua origem.

Conceitualmente:
````
Telemetry ───────────┐
Event ───────────────┼────► KPI Result
Operational Context ─┘
````
Entretanto, rastreabilidade analítica não implica necessariamente relacionar fisicamente cada resultado a todas as observações individuais utilizadas em seu cálculo.
````
Analytical Traceability
          ≠
Physical Row-Level Relationship
````
A rastreabilidade poderá ser preservada por meio de elementos como:

* KPI Definition;
* variáveis de origem;
* escopo industrial;
* referência temporal;
* contexto operacional;
* lineage de processamento.

---

### 15. Analytical Comparability

Dois resultados não deverão ser considerados comparáveis apenas porque possuem o mesmo nome de KPI.

Por exemplo:
````
94.7%  vs  92.1%
````
somente representa uma comparação válida quando houver compatibilidade suficiente entre:
````
KPI Definition
Calculation Semantics
Industrial Scope
Temporal Reference
Analytical Grain
Relevant Context
````
Conceitualmente:
````
Result A ──┐
           │
           ├──► Semantic Compatibility
           │            │
Result B ──┘            ▼
                  Valid Comparison
````
> Analytical comparability requires semantic compatibility.

Essa regra evita comparações entre resultados que possuem aparência semelhante, mas significados diferentes.

---

### 16. Modelo Conceitual Analítico

O núcleo conceitual do DM-05 pode ser representado como:
````
                INDUSTRIAL EVIDENCE

Telemetry ──────────────┐
Event ──────────────────┤
Operational Context ────┤
                        │
                        ▼
                   DERIVATION
                        │
                        ▼
                   KPI RESULT
                  ┌─────┼─────┐
                  │     │     │
                  ▼     ▼     ▼
                Value  Time  Scope
                         │
                         ▼
                 Analytical Grain
````
A dimensão semântica pode ser representada como:
````
KPI Identity
     │
     ▼
KPI Definition
     │
     ├── Meaning
     ├── Calculation Semantics
     └── Version
             │
             ▼
         KPI Result
          ┌──┼───────────┐
          │  │           │
          ▼  ▼           ▼
       Context       Analytical
       Quality       Traceability
````
O modelo conceitual completo começa então a formar uma cadeia de enriquecimento:
````
PROCESS
   │
   ▼
 ASSET
   │
   ▼
VARIABLE
   │
   ▼
TELEMETRY
   │
   ▼
 EVENT
   │
   ├────────────────┐
   ▼                │
OPERATIONAL         │
CONTEXT             │
   │                │
   └───────┬────────┘
           ▼
          KPI
           │
           ▼
Analytical Understanding
````
Essa representação descreve uma progressão semântica possível, e não um pipeline obrigatório.

Nem todo KPI depende de Event.

Nem toda Telemetry participa de um KPI.

Nem todo Event estabelece Operational Context.

As relações existem conforme o significado e a necessidade analítica.

---

### 17. Boundaries

O DM-05 não define:

* fórmulas definitivas de KPI;
* estrutura física de KPI Definition e KPI Result;
* Primary Keys ou Foreign Keys;
* tabelas PostgreSQL;
* views ou materialized views;
* Star Schema;
* estrutura Avro;
* tópicos Kafka.

Essas decisões pertencem aos modelos lógico e físico, ao processamento analítico ou às respectivas regras de engenharia e negócio.

---

### 18. Related Engineering and Architecture

| Documento |                           	Relação                                            |
|---------|------------------------------------------------------------------------------------|
| IPEM-09 |	Estabelece análise e gestão orientadas por contexto operacional                    |
| ARCH-02 |	Define Progressive Information Enrichment                                          |
| ARCH-06 |	Define Analytics and Knowledge como camada de geração de conhecimento para decisão | 
| ADR-05  |	Estabelece processamento e derivação de novas informações                          |
| DM-01   |	Define KPI como entidade derivada do modelo conceitual                             |
| DM-02   |	Estabelece as identidades industriais utilizadas para definir escopo               |
| DM-03	  | Estabelece temporalidade e qualidade das evidências industriais                    |
| DM-04	  | Estabelece Operational Context como dimensão explícita de interpretação            |

---

### 20. Considerações Finais

O DM-05 estabelece KPI como uma síntese analítica semanticamente definida e derivada de evidências industriais.
````
Industrial Evidence
        │
        ▼
    Derivation
        │
        ▼
    KPI Result
   ┌────┼────┐
   │    │    │
   ▼    ▼    ▼
 Value Time Scope
        │
        ▼
     Context
        │
        ▼
Analytical Understanding
````
Um KPI não é definido apenas por sua fórmula ou valor.

Seu significado depende da combinação entre definição, semântica de cálculo, escopo industrial, referência temporal, granularidade e contexto operacional.

A rastreabilidade permite explicar como o resultado foi produzido, enquanto a compatibilidade semântica determina quando diferentes resultados podem ser comparados.

Dessa forma, o IMS não trata Analytics apenas como produção de números, mas como transformação de evidências industriais em informação interpretável para suporte à decisão.
