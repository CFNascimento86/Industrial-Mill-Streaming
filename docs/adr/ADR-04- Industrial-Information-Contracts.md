## ADR-04 — Industrial Information Contracts

| Campo | Valor |
|---|---|
| **Documento** | ADR-04 |
| **Título** | Industrial Information Contracts |
| **Versão** | 1.0 |
| **Status** | Accepted |
| **Projeto** | Industrial Mill Streaming — IMS |
| **Especificação** | Architecture Decision Records — ADR |
| **Derivação** | ARCH-02 / ARCH-03 / ARCH-05 / ADR-01 / ADR-02 / ADR-03 |

---

### 1. Context

O Industrial Mill Streaming (IMS) utiliza uma arquitetura orientada a eventos para desacoplar aquisição, processamento, persistência e consumo das informações industriais.

Entretanto, o desacoplamento técnico entre produtores e consumidores não garante, por si só, que ambos interpretem uma informação da mesma maneira.

Uma mensagem contendo apenas:

````
{
  "tag": "PT_101",
  "value": 42.7
}
````
pode ser tecnicamente válida, mas permanece insuficiente para determinar de forma inequívoca:

* qual ativo originou a informação;
* qual variável está sendo representada;
* qual unidade de engenharia está sendo utilizada;
* quando a observação ocorreu;

Dessa forma, uma arquitetura orientada a eventos sem contratos explícitos pode reduzir o acoplamento técnico enquanto mantém dependências semânticas implícitas.

> Technical decoupling does not guarantee semantic consistency.

O IMS necessita, portanto, estabelecer contratos explícitos para as informações compartilhadas entre suas capacidades.

---

### 2. Decision Drivers

A decisão considera os seguintes direcionadores:

* desacoplamento entre produtores e consumidores;
* consistência estrutural das mensagens;
* preservação do significado industrial;
* versionamento explícito;
* preservação do contexto ao longo do fluxo informacional.

---

### 3. Architectural Decision
*Contract-Driven Information Exchange*

Toda informação compartilhada entre capacidades desacopladas do IMS deverá possuir um contrato explícito e versionado, responsável por estabelecer sua estrutura e o contexto mínimo necessário à sua interpretação.

Produtores e consumidores não deverão depender diretamente das respectivas implementações.

Eles deverão depender do contrato compartilhado.
````
Producer
   │
   ▼
Information Contract
   │
   ▼
 Kafka
   │
   ▼
Information Contract
   │
   ▼
Consumer
````
Essa decisão transforma o contrato em uma fronteira arquitetural entre capacidades independentes.

---

### 4. Structural Contract and Semantic Context

O IMS distingue explicitamente estrutura de significado.
````
Industrial Information Contract
          │
          ├── Structural Contract
          │
          │    fields
          │    types
          │    required attributes
          │    validation rules
          │
          └── Semantic Context
               asset
               variable
               unit
               quality
               source
               event type
````
*Structural Contract*

Define como a informação é representada tecnicamente.

Inclui aspectos como:

* campos;
* tipos;
* obrigatoriedade;
* estrutura;
* versão;
* regras de validação.

.

*Semantic Context*

Define elementos mínimos necessários para interpretar a informação no domínio industrial.

Pode incluir referências como:

* ativo;
* variável;
* unidade de engenharia;
* qualidade;
* origem;
* tipo de evento.

> Schema defines structure. Context preserves meaning.

O schema não deverá substituir o modelo de domínio industrial.

---

### 5. Canonical Event Envelope

Os eventos compartilhados pelo IMS deverão possuir um envelope comum para metadados essenciais.

Conceitualmente:
````
Canonical Event Envelope
│
├── Event Identity
├── Event Type
├── Contract Version
├── Occurrence Time
├── Source / Provenance
│
└── Payload
     │
     └── Domain-Specific Information
````
O envelope deverá permitir que qualquer consumidor identifique minimamente:

* o evento;
* sua natureza;
* sua versão;
* quando ocorreu;
* sua origem;
* o conteúdo específico transportado.

Uma representação conceitual poderá assumir a seguinte forma:
````
{
  "event_id": "...",
  "event_type": "telemetry.observed",
  "event_version": "1.0",
  "occurred_at": "...",
  "source": "...",
  "asset_id": "...",
  "payload": {}
}
````
Os nomes definitivos dos campos e suas estruturas serão estabelecidos posteriormente pelo Event Model.

Este ADR define a existência e a responsabilidade do envelope, não sua implementação física definitiva.

---

### 6. Context Propagation

O IMS deverá preservar contexto suficiente para que uma informação permaneça identificável durante seu trânsito entre capacidades.
````
Industrial Source
       │
       ▼
  Acquisition
       │
       ▼
Industrial Identity
       │
       ▼
 Event Contract
       │
       ▼
     Kafka
       │
       ├──► Processing
       ├──► Persistence
       └──► Analytics
````
O contexto transportado pelo evento deverá ser suficiente para correlacionar a informação ao modelo lógico do IMS. Entretanto, o evento não deverá replicar integralmente o modelo de domínio.
````
Event
│
├── asset_id ───────────────┐
├── variable_id             │
├── timestamp               │
├── value                   │
├── quality                 │
└── unit                    │
                            ▼
                       Domain Model
                            │
                            ├── Asset
                            ├── Process
                            ├── Equipment
                            └── Operational Context
````
Essa separação mantém os eventos enxutos sem perder sua identidade industrial.

---

### 7. Technology Decision A
*Apache Avro — Event Schema Definition*

Apache Avro será adotado como formato principal para definição dos contratos estruturais dos eventos internos.

A escolha considera:

* schema explícito;
* tipagem;
* suporte à evolução de schemas;
* interoperabilidade;
* ampla integração com ecossistemas orientados a eventos;
* separação entre definição do contrato e implementação dos produtores e consumidores.
````
IMS Event Model
      │
      ▼
  Avro Schema
      │
      ▼
   Producer
      │
      ▼
    Kafka
      │
      ▼
   Consumer
````
Avro será responsável pela representação estrutural do contrato.

Ele não será utilizado como substituto do modelo semântico ou do modelo de domínio do IMS.

---

### 8. Technology Decision B
*Schema Registry*

O IMS utilizará um Schema Registry para centralizar, versionar e validar os contratos utilizados na comunicação orientada a eventos.

O registry será responsável por:

* registro dos schemas;
* identificação de versões;
* disponibilização dos contratos;
* validação de compatibilidade;
* suporte à evolução controlada;
* governança estrutural dos eventos.
````
                  Schema Registry
                   ▲           ▲
                   │           │
              validation   contract
                   │           │
                   │           │
Producer ─────────► Kafka ─────────► Consumer
````
A introdução do registry evita que schemas sejam tratados como definições locais e independentes dentro de cada serviço.

---

### 9. Registry Implementation

A implementação deverá priorizar uma solução que preserve interoperabilidade e aderência à estratégia de tecnologias abertas do IMS.

Apicurio Registry será adotado como implementação inicial do Schema Registry.

A escolha permite centralizar e governar artefatos de contrato sem tornar a arquitetura conceitualmente dependente de um formato único de schema.
````
                 Apicurio Registry
                       │
                       ▼
                 Contract Governance
                       │
              ┌────────┴────────┐
              ▼                 ▼
          Producers          Consumers
              │                 ▲
              └────► Kafka ─────┘
````
A decisão arquitetural de utilizar um Schema Registry permanecerá desacoplada da implementação escolhida.

---

### 10. Schema Evolution

Os contratos deverão evoluir de maneira controlada.

> Mudanças nos contratos devem preservar compatibilidade sempre que possível; breaking changes deverão resultar em uma nova versão explícita do contrato.

Conceitualmente:
````
Contract v1
    │
    ├──── Compatible Evolution ───► v1.x
    │
    └──── Breaking Change ─────────► v2
````
Mudanças compatíveis poderão incluir, conforme regras definidas posteriormente:

* inclusão de campos opcionais;
* expansão controlada de estruturas;
* inclusão de metadados sem quebra de consumidores existentes.

Mudanças incompatíveis deverão resultar em uma nova versão claramente identificável.

A política específica de compatibilidade backward, forward ou full será estabelecida conforme a natureza de cada contrato e os requisitos de implementação.

---

### 11. Contract Validation

A validade de um evento não deverá depender apenas da capacidade do produtor de publicá-lo no Kafka.

O fluxo deverá considerar validação contra o contrato correspondente.
````
Producer
   │
   ▼
Contract Validation
   │
   ├── Invalid ───► Rejected / Controlled Handling
   │
   ▼
 Valid
   │
   ▼
 Kafka
````
Da mesma forma, consumidores deverão utilizar contratos para interpretar corretamente os eventos recebidos.

Essa disciplina reduz a propagação de mensagens estruturalmente inconsistentes pela plataforma.

---

### 12. Relationship with Progressive Information Enrichment

Os contratos deverão respeitar o princípio Progressive Information Enrichment estabelecido no ARCH-02.

Isso significa que diferentes estágios do IMS poderão produzir informações com níveis distintos de contextualização.
````
Observation
     │
     ▼
Structured Telemetry
     │
     ▼
Contextualized Information
     │
     ▼
Analytical Information
````
Cada estágio poderá possuir contratos específicos conforme sua responsabilidade.

O objetivo não será criar um único schema universal para toda a plataforma.

Essa abordagem permite enriquecimento progressivo sem destruir rastreabilidade ou significado.

---

### 13. Rationale

A decisão estabelece uma cadeia explícita entre significado, estrutura e transporte.
````
Industrial Meaning
       │
       ▼
Information Model
       │
       ▼
 Event Contract
       │
       ▼
  Avro Schema
       │
       ▼
Schema Registry
       │
       ▼
     Kafka
       │
       ▼
   Consumers
````
Cada elemento possui responsabilidade distinta.

| Elemento              | Responsabilidade          |
| --------------------- | ------------------------- |
| **Information Model** | Significado industrial    |
| **Event Contract**    | Interface compartilhada   |
| **Apache Avro**       | Representação estrutural  |
| **Schema Registry**   | Governança e evolução     |
| **Apache Kafka**      | Transporte e distribuição |

Essa separação evita que tecnologia, estrutura e semântica sejam tratadas como conceitos equivalentes.

---

### 14. Consequences
*14.1 - Positive*

A decisão proporciona:

* contratos explícitos;
* versionamento;
* redução de ambiguidades;
* menor acoplamento entre produtores e consumidores;
* governança centralizada;
* preservação do contexto industrial.

.

*14.2 - Negative*

A decisão introduz:

* necessidade de manutenção dos schemas;
* disciplina de versionamento;
* novo componente de infraestrutura;
* necessidade de governança de contratos;
* maior rigor no desenvolvimento de produtores e consumidores;
* necessidade de tratar compatibilidade durante evolução.

.

*14.3 - Risks / Trade-offs*

A adoção de contratos explícitos aumenta a disciplina e a complexidade de evolução das interfaces.

Esse trade-off é conscientemente aceito.

> O IMS aceita maior disciplina na produção e evolução dos eventos para reduzir ambiguidade e acoplamento entre capacidades independentes.

---

### 15. Boundaries

*Este ADR não define:*

* schemas Avro completos;
* tipos definitivos de eventos;
* estrutura definitiva dos payloads;
* estratégia de particionamento Kafka;
* IDs definitivos dos ativos;
* política universal de backward, forward ou full compatibility.

Esses elementos serão definidos pelo Event Model, Data Model, implementação ou decisões arquiteturais posteriores quando necessário.

---

### 16. Related Architecture

| Documento   | Relação                                                          |
| ----------- | ---------------------------------------------------------------- |
| **IPEM-07** | Estabelece o Telemetry Model                                     |
| **IPEM-08** | Define Event Model e preservação do conhecimento de engenharia   |
| **ARCH-00** | Estabelece tecnologia como consequência da arquitetura           |
| **ARCH-02** | Define Progressive Information Enrichment                        |
| **ARCH-03** | Define comunicação e desacoplamento entre capacidades            |
| **ARCH-05** | Estabelece identidade, rastreabilidade e confiança da informação |
| **ADR-01**  | Define Event-Driven Integration e Apache Kafka                   |
| **ADR-02**  | Define Industrial Data Acquisition                               |
| **ADR-03**  | Define Industrial Data Persistence                               |

---

### 17. Considerações Finais

O ADR-04 estabelece que o desacoplamento arquitetural do IMS não termina no transporte das mensagens.

Para que capacidades independentes possam evoluir sem perder consistência, a informação compartilhada deverá possuir estrutura explícita, identidade preservada, contexto mínimo e evolução governada.
````
Industrial Process
       │
       ▼
  Acquisition
       │
       ▼
Information Model
       │
       ▼
 Event Contract
       │
       ▼
  Apache Avro
       │
       ▼
Apicurio Registry
       │
       ▼
 Apache Kafka
       │
       ├──► Processing
       ├──► Persistence
       └──► Analytics
````
Apache Avro materializa o contrato estrutural.

Apicurio Registry governa sua existência e evolução.

Kafka distribui os eventos.

O modelo informacional preserva seu significado industrial.

> Dados podem atravessar tecnologias diferentes. Seu significado não pode se perder durante o caminho.
