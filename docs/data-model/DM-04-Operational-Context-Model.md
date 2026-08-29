### 1. Contexto

O DM-03 estabelece como Telemetry e Event representam observações e ocorrências ao longo do tempo.

Uma informação industrial não adquire significado completo apenas por possuir identidade, valor e timestamp.

Sua interpretação depende das condições operacionais sob as quais foi produzida.

O *DM-04* estabelece como **Operational Context representa essas condições**, permitindo interpretar Telemetry, Event e posteriormente KPI dentro de uma realidade operacional explícita.

---

### 2. Princípios de Modelagem de Contexto

O modelo estabelece quatro princípios fundamentais.

-> *Context Is a First-Class Entity*

Operational Context deverá ser modelado explicitamente, e não tratado apenas como metadata descritiva anexada aos dados.

-> *Context Has Temporal Validity*

Um contexto operacional existe durante determinado período e sua aplicabilidade depende dessa validade temporal.

-> *Context Has Semantic Scope*

Um contexto deverá possuir um escopo industrial reconhecível, indicando a quais Process, Asset ou demais entidades ele se aplica.

-> *Meaning Depends on Context*

A mesma observação ou ocorrência poderá possuir significados operacionais diferentes sob diferentes condições.

---

### 3. Operational Context

*Operational Context* representa uma condição operacional sob a qual informações industriais devem ser interpretadas.

Exemplo:

```text
Hydraulic Pressure = 185 bar
````
isoladamente descreve uma observação.

Entretanto:
````
Hydraulic Pressure = 185 bar

Context:
- Mill Running
- High Load
- Automatic Mode
````
permite interpretar essa mesma observação dentro de uma condição operacional específica.

O contexto não altera o valor observado.

Ele altera a capacidade de interpretar corretamente seu significado.

---

### 4. Context Identity

Um contexto deverá possuir identidade própria.

Por exemplo:
````
HIGH_LOAD
````
representa uma condição semanticamente reconhecível.

Essa mesma condição poderá ocorrer diversas vezes:
````
HIGH_LOAD
   │
   ├── Occurrence 01 → 10:00–10:45
   ├── Occurrence 02 → 13:20–13:52
   └── Occurrence 03 → 16:10–16:48
````
Conceitualmente, é útil distinguir:
````
Context Meaning
      │
      └── what the condition represents

Context Occurrence
      │
      └── when the condition was active
````
O DM-04 não determina ainda se essas dimensões serão materializadas como entidades distintas.

Estabelece apenas que significado e ocorrência temporal representam responsabilidades diferentes.

---

### 5. Temporal Validity

Operational Context possui validade temporal.

Exemplo:
````
High Load

10:00 ├──────────────────────────┤ 10:45
````
As informações produzidas dentro desse intervalo poderão ser interpretadas sob esse contexto quando o escopo semântico também for compatível.
````
Telemetry A ──┐
Telemetry B ──┼──► High Load Context
Telemetry C ──┤
Event X ──────┘
````
Assim:

> Operational Context has temporal validity.

A associação entre informação e contexto poderá ser determinada temporalmente, sem exigir necessariamente uma referência física direta em cada observação.

---

### 6. Semantic Scope

Nem todo contexto se aplica a toda a planta ou a todas as entidades do modelo.

Exemplos:
````
High Load
   │
   └── Mill 01

Production Mode
   │
   └── Milling Process

Manual Hydraulic Control
   │
   └── Hydraulic System
````
Operational Context deverá possuir um escopo industrial semanticamente reconhecível.

Conceitualmente:
````
Operational Context
       │
       ├── Process
       ├── Asset
       └── broader industrial scope
````
O escopo evita que uma condição local seja interpretada como global.

---

### 7. Context Applicability

A aplicabilidade de um contexto depende de duas condições principais:
````
Temporal Validity
        +
Semantic Scope
        │
        ▼
Context Applicability
````
Por exemplo:
````
Context:
High Load — Mill 01
````
não deverá automaticamente ser aplicado a informações de:
````
Mill 02
````
mesmo que os períodos temporais coincidam.

Da mesma forma, informações pertencentes ao mesmo Asset, mas fora do período de validade, não deverão ser interpretadas sob aquele contexto.

---

### 8. Context Composition

Uma condição operacional pode ser composta por diferentes dimensões simultâneas.

Em um mesmo instante:
````
Time T
 │
 ├── Production
 ├── Mill Running
 ├── High Load
 └── Automatic Mode
````
Portanto, o modelo não deverá assumir que existe apenas um único contexto operacional ativo.

Contextos poderão coexistir quando representarem dimensões diferentes da operação.

Exemplo conceitual:
````
Operational Context
│
├── Production State
│      ├── Running
│      └── Stopped
│
├── Operating Mode
│      ├── Automatic
│      └── Manual
│
├── Load Condition
│      ├── Normal
│      └── High
│
└── Process Condition
       ├── Stable
       └── Transient
````
O DM-04 não define uma taxonomia definitiva.

---

### 9. Operational Context × Event

Operational Context e Event representam conceitos diferentes.
````
EVENT
   │
   └── what happened

OPERATIONAL CONTEXT
   │
   └── under which condition it happened
````
Exemplo:
````
Event
Mill Started
````
pode estabelecer:
````
Operational Context
Mill Running
````
Da mesma forma, um Event poderá iniciar, alterar ou encerrar um contexto.
````
Event
High Load Detected
      │
      ▼
Operational Context
High Load
10:00 ├──────────────────┤ 10:45
````
Portanto:

> Event represents occurrence. Operational Context represents condition.

---

### 10. Observed × Inferred Context

Operational Context poderá possuir diferentes origens semânticas.

-> *Observed Context*

Deriva diretamente de uma informação explícita.

Exemplo:
````
Operating Mode = AUTO
````
gera ou representa:
````
Context
Automatic Operation
````

-> *Inferred Context*

É obtido por interpretação de múltiplas informações ou regras.

Exemplo:
````
Cane Flow
    +
Motor Load
     +
Roll Speed
     │
     ▼
High Load Context
````
Conceitualmente:
````
Operational Context
       │
       ├── Observed
       └── Inferred
````
O DM-04 não define algoritmos ou regras específicas de inferência.

---

### 11. Context Provenance

Quando um Operational Context for derivado, sua origem deverá permanecer rastreável.
````
Telemetry A ───┐
Telemetry B ───┼──► Operational Context X
Event C ───────┘
````
A proveniência permite compreender quais informações contribuíram para estabelecer determinada condição operacional.

> Derived context should preserve provenance.

Essa capacidade suporta rastreabilidade, interpretação analítica e preservação do conhecimento de engenharia.

---

### 12. Telemetry × Operational Context

Uma Telemetry poderá ser interpretada sob zero, um ou vários contextos simultaneamente.
````
Telemetry X
    │
    ├── Running
    ├── High Load
    └── Automatic Mode
````
Conceitualmente:
````
TELEMETRY
     N
     │
     │ interpreted under
     │
     N
OPERATIONAL CONTEXT
````
Essa cardinalidade conceitual não implica necessariamente uma relação física N:N.

A associação poderá ser determinada por:

* tempo;
* escopo;
* regras;
* materialização analítica.

---

### 13. Event × Operational Context

Events também deverão ser interpretáveis sob contexto operacional.

Exemplo:
````
Event
High Motor Current
       │
       │ occurred under
       ▼
Operational Context
Mill Start
````
O mesmo Event poderá possuir significado diferente sob outro contexto:
````
High Motor Current
       │
       │ occurred under
       ▼
Stable Production
````
Portanto:

> The same event may have different operational meaning under different contexts.

Essa relação permite distinguir uma ocorrência esperada de uma condição potencialmente anormal.

---

### 14. KPI × Operational Context

Operational Context será um elemento fundamental para o modelo analítico do IMS.

Um KPI isolado:
````
OEE = 82%
````
descreve desempenho.

Quando contextualizado:
````
OEE = 82%

Context:
- High Load
- Automatic Operation
- Stable Production
````
passa a permitir interpretação.

Da mesma forma:
````
OEE under Normal Load
        vs
OEE under High Load
````
permite compreender como diferentes condições operacionais influenciam o resultado.

Conceitualmente:
````
Telemetry
   +
 Event
   +
Operational Context
        │
        ▼
       KPI
````

---

### 15. Modelo Conceitual de Contexto

O núcleo conceitual do DM-04 pode ser representado como:
````
                 INDUSTRIAL IDENTITY

                     PROCESS
                        │
                      ASSET
                        │
                     VARIABLE
                        │
                        ▼
                    TELEMETRY
                        │
                        │ contributes to
                        ▼
                      EVENT
                        │
                        │ establishes / modifies
                        ▼
               OPERATIONAL CONTEXT
                 ┌──────┼──────┐
                 │      │      │
                 ▼      ▼      ▼
               Scope   Time  Meaning
                 │      │
                 └──┬───┘
                    ▼
              Applicability
````
Operational Context também atua transversalmente sobre a interpretação da informação:
````
Telemetry ───────┐
Event ───────────┼────► Operational Context
State ───────────┘              │
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
             Telemetry        Event            KPI
          interpretation   interpretation   interpretation
````
Essa representação demonstra que contexto não constitui apenas um estágio do fluxo.

Ele é uma dimensão transversal de interpretação.

---

### 16. Boundaries

O DM-04 não define:

* taxonomia definitiva de contextos;
* formato físico de context_id;
* estrutura de tabelas;
* Primary Keys ou Foreign Keys;
* estratégia física para associação temporal;
* thresholds operacionais;
* estrutura Avro;
* tópicos Kafka.

Essas decisões pertencem aos modelos lógico e físico, ao processamento ou às disciplinas específicas responsáveis pelas regras de engenharia.

---

### 17. Related Engineering and Architecture

| Documento	|                           Relação                                              |
|---------|----------------------------------------------------------------------------------|
| IPEM-08 |	Define Event Model e preservação do conhecimento de engenharia                   |
| IPEM-09	| Estabelece gestão e análise orientadas por contexto operacional                  |
| ARCH-02	| Define Progressive Information Enrichment                                        |
| ADR-05	| Estabelece processamento e derivação de novas informações                        |
| ADR-06	| Define rastreabilidade, replay e responsabilidades dos eventos                   |
| DM-01   |	Define Operational Context como entidade contextual de primeira classe           |
| DM-03	  | Estabelece a dimensão temporal necessária para validade e associação de contexto |

---

### 18. Considerações Finais

O DM-04 estabelece Operational Context como uma entidade explícita do modelo industrial do IMS.
````
Industrial Information
       │
       ├── Telemetry
       └── Event
              │
              ▼
      Operational Context
          ┌────┼────┐
          │    │    │
          ▼    ▼    ▼
        Scope Time Meaning
          │    │
          └─┬──┘
            ▼
      Applicability
````
Contexto possui identidade, validade temporal e escopo semântico.

Múltiplos contextos podem coexistir, serem observados ou inferidos e participar da interpretação das mesmas informações industriais.

Essa separação permite que Telemetry e Event sejam avaliados não apenas pelo que representam isoladamente, mas pelas condições sob as quais ocorreram.
