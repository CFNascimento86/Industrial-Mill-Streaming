### 1. Contexto

O IMS transforma dados provenientes do processo industrial em informações contextualizadas capazes de suportar processamento, persistência, análise e tomada de decisão.

Para que essa informação permaneça consistente ao longo de seu ciclo de vida, é necessário estabelecer um modelo conceitual independente das tecnologias utilizadas para aquisição, transporte ou armazenamento.

O DM-01 define as **entidades fundamentais do domínio informacional do IMS e seus principais relacionamentos**, formando a base para os modelos lógico e físico posteriores.

> **Modelar o significado antes de modelar sua representação.**

---

### 2. Princípio de Modelagem

*Identity Before Storage*

> **Uma entidade industrial deve possuir identidade lógica estável antes de qualquer decisão sobre onde ou como será armazenada.**

A identidade de um ativo ou variável não deverá depender de elementos técnicos como:

```text
OPC UA NodeId
Kafka Topic
PostgreSQL Key
ADLS Path
```

Esses elementos representam implementações ou referências técnicas.

A identidade industrial representa o **significado da entidade dentro do processo**.

```text
Industrial Identity
        │
        ├── OPC UA
        ├── Kafka
        ├── PostgreSQL
        └── ADLS
```

---

### 3. Entidades Fundamentais

O modelo conceitual do IMS estabelece sete entidades pertencentes ao domínio industrial e uma entidade pertencente ao domínio técnico.

*Industrial Domain*

| Entidade                | Responsabilidade                                              |
| ----------------------- | ------------------------------------------------------------- |
| **Process**             | Representa o processo industrial                              |
| **Asset**               | Representa um ativo físico ou funcional                       |
| **Variable**            | Representa uma propriedade observável                         |
| **Telemetry**           | Representa uma observação temporal                            |
| **Event**               | Representa um acontecimento significativo                     |
| **Operational Context** | Representa as condições operacionais associadas à informação  |
| **KPI**                 | Representa uma síntese mensurável do comportamento industrial |

*Technical Domain*

| Entidade   | Responsabilidade                                                  |
| ---------- | ----------------------------------------------------------------- |
| **Source** | Representa a origem técnica utilizada para obtenção da informação |

Essa separação evita que mudanças na infraestrutura de automação alterem a identidade conceitual das informações industriais.

---

### 4. Modelo Conceitual

```text
                         PROCESS
                            │
                            │
                            ▼
                          ASSET
                            │
                            │
                            ▼
                         VARIABLE
                            │
                        observed as
                            │
                            ▼
                        TELEMETRY
                       /         \
                      /           \
                     ▼             ▼
                  EVENT     OPERATIONAL CONTEXT
                     \             /
                      \           /
                       └─────┬────┘
                             ▼
                            KPI


                   TECHNICAL DOMAIN

                         SOURCE
                            │
                            │ provides
                            ▼
                     observations of
                         VARIABLE
```

O modelo representa a evolução conceitual da informação sem estabelecer sua materialização física.

---

### 5. Process e Asset

*Process* estabelece a fronteira de significado industrial.

*Asset* representa os elementos físicos ou funcionais que participam desse processo.

Ativos podem possuir relações hierárquicas:

```text
Process
   │
   ▼
  Mill
   │
   ├── Main Drive
   ├── Hydraulic System
   └── Roller Assembly
```

O modelo conceitual não exige que essa hierarquia reproduza diretamente a estrutura física da automação.

---

### 6. Variable e Telemetry

*Variable* representa aquilo que pode ser observado.

*Telemetry* representa aquilo que efetivamente foi observado em determinado instante.

```text
VARIABLE
Hydraulic Pressure
       │
       │ 1:N
       ▼
    TELEMETRY

178.2 bar
181.5 bar
185.4 bar
...
```

Portanto:

> **Variable defines what can be observed. Telemetry records what was observed.**

Essa separação impede que tags, endereços de PLC ou identificadores de protocolo sejam confundidos com a própria variável industrial.

---

### 7. Telemetry e Event

Telemetry e Event possuem significados distintos.

```text
Telemetry
Pressure = 185.4 bar
```

representa uma observação.

```text
Event
High Hydraulic Pressure Detected
```

representa um acontecimento significativo.

Um Event poderá resultar da interpretação ou correlação de múltiplas observações:

```text
Telemetry A ─┐
Telemetry B ─┼──► EVENT
Telemetry C ─┘
```

Por isso, a relação conceitual entre Telemetry e Event poderá assumir cardinalidade **N:N**.

> **Observation is not meaning.**

Nem toda Telemetry produz um Event e nem todo Event depende de uma única observação.

---

### 8. Operational Context

Operational Context representa as condições nas quais determinada informação industrial possui significado.

Exemplos incluem:

```text
Operating Mode
Load Condition
Shift
Production Rate
Operational State
```

Conceitualmente:

```text
Telemetry
     +
Operational Context
     │
     ▼
Industrial Meaning
```

A mesma observação poderá possuir interpretações diferentes dependendo das condições operacionais existentes no momento em que ocorreu.

Por isso:

> **Context is a first-class entity.**

A forma física de associação entre Telemetry e Operational Context será definida posteriormente no Logical Data Model.

---

### 9. Source

Source representa a origem técnica utilizada para obter determinada informação.

Exemplos:

```text
PLC
OPC UA Server
OPC UA Node
```

Entretanto:

```text
Industrial Identity ≠ Technical Identity
```

Uma alteração em um endereço, NodeId ou mecanismo de aquisição não deverá alterar a identidade da variável industrial.

```text
VARIABLE
Hydraulic Pressure
       │
       └──────────── SOURCE
                     OPC UA Node
```

Source pertence, portanto, ao **Technical Domain**, mantendo integração tecnológica desacoplada da semântica industrial.

---

### 10. KPI

KPI representa uma síntese mensurável produzida a partir das informações do processo.

Ele não deverá ser interpretado isoladamente.

```text
Telemetry
     │
     ├──── Event
     │
     └──── Operational Context
                │
                ▼
               KPI
```

Conceitualmente:

> **Telemetry provides evidence.
> Events provide significance.
> Operational Context provides circumstances.
> KPI provides synthesis.**

Essa estrutura permite que indicadores sejam interpretados juntamente com as condições que contribuíram para seu resultado.

---

### 11. Cardinalidades Conceituais

As principais relações inicialmente estabelecidas são:

```text
Process ───────── Asset
                    │
                    ▼
                 Variable
                    │
                   1:N
                    ▼
                Telemetry
                    │
              ┌─────┴─────┐
              │           │
             N:N       Temporal
              │           │
              ▼           ▼
            Event     Operational
                       Context
              │           │
              └─────┬─────┘
                    ▼
                   KPI
```

Essas cardinalidades representam relações do domínio.

Elas *não determinam Foreign Keys, tabelas ou estruturas físicas*.

---

### 12. Classificação Conceitual

| Conceito            | Classificação             |
| ------------------- | ------------------------- |
| Process             | Entidade industrial       |
| Asset               | Entidade industrial       |
| Variable            | Entidade industrial       |
| Telemetry           | Entidade temporal         |
| Event               | Entidade temporal         |
| Operational Context | Entidade contextual       |
| KPI                 | Entidade derivada         |
| Source              | Entidade técnica          |
| Unit                | Metadado                  |
| Quality             | Propriedade da observação |
| OPC UA NodeId       | Referência técnica        |
| Kafka Topic         | Infraestrutura            |
| Avro Schema         | Contrato técnico          |

Essa classificação estabelece uma fronteira clara entre **semântica industrial e implementação tecnológica**.

---

### 13. Boundaries

O DM-01 não define:

* atributos definitivos das entidades;
* tipos de dados;
* Primary Keys ou Foreign Keys;
* schemas PostgreSQL;
* tabelas;
* índices;
* particionamento;
* estruturas Avro.

Essas decisões pertencem aos modelos lógico e físico posteriores.

---

### 14. Related Engineering and Architecture

| Documento   | Relação                                                            |
| ----------- | ------------------------------------------------------------------ |
| **IPEM-03** | Define a organização do processo industrial                        |
| **IPEM-05** | Define os ativos relevantes do processo                            |
| **IPEM-08** | Estabelece Event Model e preservação do conhecimento de engenharia |
| **IPEM-09** | Estabelece interpretação orientada ao contexto operacional         |
| **ARCH-01** | Define organização lógica independente da infraestrutura física    |
| **ARCH-02** | Define Progressive Information Enrichment                          |
| **ARCH-06** | Define transformação de informação contextualizada em conhecimento |
| **ADR-02**  | Define aquisição e desacoplamento da origem técnica                |
| **ADR-04**  | Define contratos para representação dos eventos                    |

---

### 15. Considerações Finais

O DM-01 estabelece a estrutura conceitual fundamental do IMS.

```text
Process
   ↓
Asset
   ↓
Variable
   ↓
Telemetry
   ↓
Context + Event
   ↓
  KPI
   ↓
Knowledge
```

A informação industrial passa a possuir identidade e significado independentes das tecnologias responsáveis por adquiri-la, transportá-la ou armazená-la.

A separação de **Source** como entidade técnica preserva essa independência e permite que a infraestrutura evolua sem comprometer o modelo industrial.

O DM-01 torna-se, portanto, a referência conceitual para os modelos subsequentes.
