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
* serialização eficiente;
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

