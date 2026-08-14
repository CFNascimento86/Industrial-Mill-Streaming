## ADR-03 — Industrial Data Persistence

| Campo | Valor |
|---|---|
| **Documento** | ADR-03 |
| **Título** | Industrial Data Persistence |
| **Versão** | 1.0 |
| **Status** | Accepted |
| **Projeto** | Industrial Mill Streaming — IMS |
| **Especificação** | Architecture Decision Records — ADR |
| **Derivação** | ARCH-02 / ARCH-04 / ARCH-05 / ADR-01 |

---

### 1. Context

O Industrial Mill Streaming (IMS) necessita preservar informações industriais para diferentes finalidades ao longo de seu ciclo de vida.

Após a aquisição e publicação dos eventos, as informações poderão ser utilizadas para processamento, investigação operacional, contextualização, análise histórica e recuperação futura.

A retenção de eventos fornecida pela plataforma de event streaming não deve ser confundida com persistência histórica.

> **Event retention is not historical persistence.**

Kafka mantém eventos disponíveis para distribuição, desacoplamento e replay conforme políticas de retenção.

A persistência industrial possui outra responsabilidade: preservar informações de forma consultável e adequada à sua finalidade de uso.

````
Industrial Data
      │
      ▼
    Kafka
      │
      ├──────────────► Event Consumers
      │
      ▼
Persistence Consumer
      │
      ▼
Persistence Architecture
````
A arquitetura necessita, portanto, separar informações operacionais de acesso frequente dos dados históricos de longo prazo.

---

### 2. Decision Drivers

A decisão considera os seguintes direcionadores:

* separação entre event streaming e persistência;
* consultas operacionais eficientes;
* preservação histórica;
* relacionamentos entre ativos, eventos, contexto e telemetria;
* rastreabilidade;
* escalabilidade do armazenamento;
* controle do crescimento do banco operacional;
* eficiência de custo para histórico de longo prazo;
* possibilidade de reprocessamento.

---

### 3. Architectural Decision

*Purpose-Oriented Persistence*

> O IMS adotará uma arquitetura de persistência orientada à finalidade da informação, separando retenção de eventos, persistência operacional e armazenamento histórico de longo prazo.

Cada mecanismo deverá assumir uma responsabilidade específica.
````
                     Industrial Information
                              │
                              ▼
                            Kafka
                     Event Retention / Replay
                              │
                              ▼
                     Persistence Consumer
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
           PostgreSQL                    ADLS
        Operational Store          Historical Store
````
Essa separação impede que uma única tecnologia seja utilizada como repositório universal para responsabilidades distintas.

---

### 4. Information Lifecycle

A persistência seguirá conceitualmente a temperatura e a finalidade da informação.
````
EVENT STREAM
Kafka
   │
   ▼
OPERATIONAL DATA
PostgreSQL
   │
   ▼
HISTORICAL DATA
ADLS
 ````
Essa progressão não representa necessariamente camadas de transformação de dados.

Ela representa diferentes responsabilidades de armazenamento ao longo do ciclo de vida da informação.

---

### 5. Technology Decision A

*PostgreSQL — Operational Data Store*

> PostgreSQL será adotado como mecanismo principal de persistência operacional e histórica recente do IMS.

O banco armazenará informações que necessitem de acesso estruturado e frequente, incluindo, conforme definido posteriormente pelo Data Model:

* telemetria recente;
* ativos;
* variáveis;
* eventos;
* contexto operacional;
* metadados;
* relacionamentos industriais;
* informações necessárias à investigação operacional.

A escolha do modelo relacional decorre da necessidade de correlacionar informações industriais além da dimensão temporal.
````
Asset
  │
  ├──── Variable
  │        │
  │        └──── Observation
  │
  ├──── Event
  │
  └──── Operational Context
````
O PostgreSQL possui ainda mecanismos nativos de particionamento que podem ser utilizados posteriormente caso o volume e os padrões de acesso justifiquem essa estratégia. A própria documentação do projeto destaca que o particionamento pode beneficiar grandes tabelas e facilitar a remoção ou migração de dados antigos, mas sua adoção depende do workload real.

---

### 6. Technology Decision B

*Azure Data Lake Storage — Historical Data Store*

> Azure Data Lake Storage será adotado como repositório de longo prazo para informações históricas que não necessitem permanecer no armazenamento operacional.

O ADLS terá como responsabilidades principais:

* preservação histórica;
* armazenamento de grande volume;
* redução da pressão de crescimento sobre o banco operacional;
* suporte a análises históricas futuras;
* disponibilização de dados para workloads analíticos.
  
````
PostgreSQL
Operational / Recent
      │
      ▼
Historical Export
      │
      ▼
     ADLS
      │
      ├── Hot
      ├── Cool
      └── Archive
````
Os níveis específicos e seus períodos de permanência serão definidos posteriormente conforme padrões reais de acesso e requisitos de custo.

O Azure Storage permite automatizar transições entre tiers por meio de Lifecycle Management Policies.

---

### 7. Persistence Flow

O serviço de aquisição não deverá persistir diretamente no PostgreSQL ou ADLS.

A persistência ocorrerá através de consumidores especializados do event stream.
````
S7-1500
   │
 OPC UA
   │
   ▼
Acquisition Service
   │
   ▼
 Kafka
   │
   ├────────► Processing Consumers
   │
   └────────► Persistence Consumer
                    │
                    ▼
                PostgreSQL
                    │
                    ▼
              Historical Export
                    │
                    ▼
                  ADLS
````
Essa decisão preserva o desacoplamento estabelecido no ADR-01.

---

### 8. Replay and Recovery

A retenção de eventos do Kafka permitirá reprocessamento dentro da janela disponível de retenção.

Caso o mecanismo de persistência esteja temporariamente indisponível:
````
Kafka
  │
  │ retained events
  ▼
Persistence Consumer
  │
  X
PostgreSQL
````
após sua recuperação:
````
Kafka
  │
  │ replay
  ▼
Persistence Consumer
  │
  ▼
PostgreSQL
````
A implementação deverá garantir idempotência suficiente para evitar persistências duplicadas durante cenários de replay. Essa capacidade não substitui uma estratégia de backup.

---

### 9. Historical Data and Backup

O IMS distingue explicitamente Historical Storage de Backup.

*Historical Storage*

Existe para preservar informações para:

* investigação;
* análise histórica;
* comparação entre períodos;
* rastreabilidade;
* ciência de dados;
* estudos futuros.
  
*Backup*

Existe para recuperação diante de:

* falha;
* corrupção;
* perda acidental;
* indisponibilidade;
* desastre.
  
````
PostgreSQL
    │
    ├────► Historical Export ───► ADLS Historical Store
    │
    └────► Backup Strategy ─────► Recovery Repository
````
> Historical persistence preserves information for use. Backup preserves systems and data for recovery.

As duas responsabilidades não devem ser tratadas como equivalentes.

---

### 10. Rationale

A decisão estabelece responsabilidades claras:

| Tecnologia            | Responsabilidade                                         |
| --------------------- | -------------------------------------------------------- |
| **Apache Kafka**      | Event streaming, retenção operacional e replay           |
| **PostgreSQL**        | Persistência operacional e histórico recente consultável |
| **ADLS**              | Persistência histórica de longo prazo                    |
| **Backup Repository** | Recuperação e continuidade                               |

A arquitetura evita transformar qualquer tecnologia em solução universal.

````
Event
  │
  ▼
Kafka
  │
  ▼
Operational Information
  │
  ▼
PostgreSQL
  │
  ▼
Historical Information
  │
  ▼
ADLS
  │
  ▼
Archive
````
Cada transição ocorre porque a finalidade da informação mudou.

---

### 11. Consequences
*11.1 - Positive*

A decisão proporciona:

* controle do crescimento do banco operacional;
* armazenamento histórico escalável;
* consultas operacionais desacopladas do histórico profundo;
* suporte futuro a analytics e ciência de dados;
* capacidade de replay.

.

*11.2 - Negative*

A decisão introduz:

* múltiplos mecanismos de armazenamento;
* necessidade de movimentação de dados entre PostgreSQL e ADLS;
* necessidade de controle de consistência;
* maior responsabilidade sobre pipelines de persistência;
* dependência de infraestrutura cloud para histórico de longo prazo.

.
  
*11.3 - Risks / Trade-offs*

A distribuição da persistência aumenta a complexidade em relação a uma estratégia baseada em banco único.

Esse trade-off é conscientemente aceito.

O IMS aceita maior complexidade na gestão do ciclo de vida da informação para separar eficiência operacional, preservação histórica e custo de armazenamento.

---

### 12. Boundaries

Este ADR não define:

* estratégia definitiva de particionamento;
* formato físico dos arquivos históricos;
* período de retenção no PostgreSQL;
* estrutura de diretórios no ADLS;
* políticas de backup.

Esses elementos serão definidos no Data Model, na implementação ou em ADRs posteriores quando possuírem relevância arquitetural própria.

---

### 13. Related Architecture

| Documento   | Relação                                                |
| ----------- | ------------------------------------------------------ |
| **ARCH-00** | Estabelece tecnologia como consequência da arquitetura |
| **ARCH-02** | Define Progressive Information Enrichment              |
| **ARCH-04** | Distribui capacidades conforme responsabilidade        |
| **ARCH-05** | Estabelece rastreabilidade e confiança na informação   |
| **ARCH-06** | Define disponibilização contextualizada para consumo   |
| **ADR-01**  | Define Event-Driven Integration e Apache Kafka         |
| **ADR-02**  | Define Industrial Data Acquisition                     |

---

### 14. Considerações Finais

O ADR-03 estabelece que persistência industrial não deve ser tratada como uma responsabilidade única.

O IMS distingue fluxo, operação, histórico e recuperação, atribuindo a cada necessidade uma responsabilidade arquitetural específica.

````
S7-1500
   │
 OPC UA
   │
   ▼
Acquisition
   │
   ▼
 Kafka
   │
   ▼
Persistence Consumer
   │
   ▼
PostgreSQL
   │
   ▼
Historical Export
   │
   ▼
 ADLS
   │
   ▼
Lifecycle
   │
   ├── Hot
   ├── Cool
   └── Archive
````
A arquitetura permanece preparada para incorporar capacidades especializadas de séries temporais quando evidências demonstrarem sua necessidade, sem antecipar complexidade.

> Persistir não significa simplesmente armazenar. Significa preservar a informação no lugar adequado, pelo tempo adequado e para a finalidade adequada.
