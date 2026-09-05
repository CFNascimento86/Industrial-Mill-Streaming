### 1. Contexto

O *Information Catalog* define as informações industriais reconhecidas pelo Industrial Mill Streaming (IMS) no domínio da Moenda.

Sua finalidade é estabelecer uma especificação semântica, canônica e versionada das informações utilizadas pelo sistema, preservando seu significado industrial independentemente da representação técnica adotada.

O catálogo estabelece a transição entre os modelos de engenharia definidos pelo IMS e sua implementação.

```text
Industrial Engineering
        │
        ▼
      IPEM
        │
        ▼
    Data Model
        │
        ▼
Information Catalog
        │
        ▼
Technical Implementation
```
> O Information Catalog define o que a informação significa, não onde ela está tecnicamente localizada.

---

### 2. Objetivo

O Information Catalog tem como objetivo identificar e descrever as informações industriais que fazem parte do escopo do IMS.

Cada informação é representada segundo seu significado no domínio industrial, permitindo que diferentes componentes da implementação utilizem uma referência semântica comum.

O catálogo deverá permitir que uma informação permaneça identificável mesmo quando sua representação técnica for alterada.

Exemplos de alterações que não necessariamente modificam o significado industrial:

- endereço no PLC;
- protocolo de aquisição;
- tecnologia de armazenamento;
- estrutura de mensageria;
- estratégia de aquisição.

Essa separação preserva a independência entre o modelo industrial e sua implementação tecnológica.

---

### 3. Escopo

O Information Catalog contempla inicialmente o domínio da *Moenda (Milling)*.

As informações industriais são organizadas em cinco grupos:

1. Mechanical Load & Drives
2. Extraction Process
3. Equipment Condition & Safety
4. Operational State
5. Derived Information

Esses grupos representam perspectivas complementares do processo industrial:

```text
Milling
│
├── Mechanical Behavior
├── Process Condition
├── Equipment Condition
├── Operational State
└── Production & Performance
```

O catálogo não representa a base de tags do PLC e não reproduz a estrutura física da Automação Industrial.

Sua organização é orientada pelo significado da informação dentro do processo.

---

### 4. Classificação da Informação

Cada item do catálogo deverá possuir uma classificação correspondente ao seu papel semântico dentro do IMS.

As classificações iniciais são:

- `telemetry`
- `state`
- `event`
- `operational_context`
- `derived_measure`
- `kpi`

*4.1 - Telemetry*

Representa uma observação temporal de uma variável industrial.

Exemplos:

- pressão hidráulica;
- velocidade dos rolos;
- corrente de motor;
- temperatura do caldo;
- temperatura de mancal.

Telemetry responde:

> O que foi observado?

.

*4.2 - State*

Representa uma condição existente durante determinado período.

Exemplos:

- estado operacional do equipamento;
- estado de intertravamento;
- estado de proteção;
- condição de segurança.

State responde:

> Qual condição existe?

.

*4.3 - Event*

Representa uma ocorrência industrial significativa.

Exemplos:

- trip;
- alarme;
- partida;
- parada;
- atuação de segurança;
- embuchamento.

Event responde:

> O que aconteceu?

.

*4.4 - Operational Context*

Representa as circunstâncias sob as quais uma informação industrial deve ser interpretada.

Exemplos:

- operação manual ou automática;
- comando local ou remoto;
- regime operacional;
- condição produtiva.

Operational Context responde:

> Sob quais condições o processo estava operando?

.

*4.5 - Derived Measure*

Representa uma informação calculada a partir de uma ou mais evidências industriais.

Exemplos:

- tempo de operação;
- relação de embebição;
- vazão de cana quando calculada a partir de outra grandeza.

Derived Measure responde:

> O que foi calculado a partir das evidências industriais?

.

*4.6 - KPI*

Representa uma medida derivada e semanticamente definida utilizada para avaliar desempenho industrial.

Exemplos:

- consumo específico de energia;
- desempenho de extração;
- índice de embuchamento;
- disponibilidade operacional.

KPI responde:

> O que o desempenho representa dentro de determinado contexto industrial?

---

### 5. Estrutura do Catálogo

A definição canônica do catálogo será armazenada em:

```text
information-catalog/
    ├── README.md
    └── milling-information-catalog.yaml
```

O arquivo `README.md` estabelece a finalidade, estrutura e regras de governança do catálogo.

O arquivo `milling-information-catalog.yaml` contém a especificação semântica das informações industriais reconhecidas pelo IMS.

Cada item deverá possuir uma definição mínima.

Exemplo:

```yaml
- logical_name: hydraulic_pressure
  display_name: Hydraulic Pressure

  information_group: mechanical_load_and_drives
  information_class: telemetry

  process: milling
  asset: mill_01

  engineering_unit: bar
  temporal_behavior: continuous

  source_type: observed
  quality_required: true

  implementation_priority: core

  description: >
    Pressão hidráulica associada à compressão dos rolos
    e ao carregamento mecânico da moenda.
```
A estrutura poderá evoluir conforme novos requisitos forem identificados durante a implementação.

---

### 6. Identidade Lógica

O atributo `logical_name` estabelece uma referência lógica estável para cada informação industrial.

Exemplo:

```text
hydraulic_pressure
```

Essa identidade deve permanecer independente de sua localização técnica.

Alterações como:

```text
PLC Address Change
Protocol Change
Database Change
Kafka Topology Change
Acquisition Technology Change
```

não devem gerar automaticamente uma nova identidade industrial.

Se o significado industrial permanecer o mesmo, a identidade lógica deverá permanecer estável.

> **Identity Is Not Location.**

A continuidade da identidade é determinada pelo significado da informação, e não por sua representação tecnológica.

---

### 7. Identidade Industrial e Identidade Técnica

O Information Catalog define a identidade semântica da informação.

A implementação poderá utilizar identificadores técnicos, como UUIDs, para representar entidades persistentes.

Conceitualmente:

```text
logical_name
     │
     ▼
Semantic Identity
     │
     ▼
variable_id
     │
     ▼
Persistent Identity
```

Exemplo:

```text
hydraulic_pressure
        │
        ▼
variable_id
        │
        ▼
       UUID
```

A estratégia de geração, persistência e gerenciamento desses identificadores pertence à camada de implementação e ao ciclo de vida do banco de dados.

O UUID não define o significado industrial da informação.

---

### 8. Mapeamento da Fonte Técnica

Informações relacionadas à localização técnica de uma variável não pertencem ao Information Catalog.

Exemplos:

- número de DB do PLC;
- byte offset;
- bit offset;
- endereço de memória;
- OPC UA NodeId;
- Kafka Topic;
- coluna de banco de dados;
- endereço de rede.

Essas informações pertencem à configuração específica de aquisição.

A relação conceitual será:

```text
Information Catalog
        │
        ▼
Industrial Identity
        │
        ▼
Source Mapping
        │
        ▼
Technical Location
```

Por exemplo:

```text
Information Catalog

hydraulic_pressure
        │
        ▼
Industrial Identity


Source Mapping

Industrial Identity
        │
        ▼
Siemens S7-1500
        │
        ▼
    DB / Offset
```

Uma alteração na localização técnica não deverá alterar a identidade industrial quando o significado permanecer inalterado.

---

### 9. Grupos de Informação

*9.1 - Mechanical Load & Drives*

Agrupa informações relacionadas ao carregamento mecânico e ao comportamento dos acionamentos.

Exemplos:

- velocidade dos rolos;
- torque dos acionamentos;
- corrente dos motores;
- potência ativa;
- potência aparente;
- pressão hidráulica.

Esse grupo permite observar como os equipamentos respondem às condições de carregamento impostas pelo processo.

.

*9.2 - Extraction Process*

Agrupa informações relacionadas ao processo físico de alimentação, extração e embebição.

Exemplos:

- vazão de cana;
- nível de alimentação;
- vazão de caldo;
- temperatura do caldo;
- vazão de água de embebição;
- umidade do bagaço.

Esse grupo representa as principais condições materiais do processo de extração.

.

*9.3 - Equipment Condition & Safety*

Agrupa informações relacionadas à condição dos equipamentos, proteção e segurança operacional.

Exemplos:

- temperatura de mancais;
- pressão de óleo;
- indicadores de vibração;
- intertravamentos;
- trips;
- estados de segurança.

O IMS utiliza essas informações para preservar e contextualizar condições provenientes da engenharia existente.

O Information Catalog não redefine lógica de proteção, intertravamento ou segurança implementada pela Engenharia de Controle e Automação.

.

*9.4 - Operational State*

Agrupa informações que descrevem como os equipamentos e o processo estão operando.

Exemplos:

- modo de controle;
- local de controle;
- estado do equipamento;
- contador de partidas;
- alarmes;
- eventos operacionais.

Essas informações permitem interpretar Telemetry e Events dentro de seu estado operacional correspondente.

.

*9.5 - Derived Information*

Agrupa informações produzidas a partir de evidências industriais primárias.

Exemplos:

- tempo de operação;
- relação de embebição;
- desempenho de extração;
- consumo específico de energia;
- índice de embuchamento;
- disponibilidade operacional.

Derived Information representa o enriquecimento progressivo das informações industriais e deverá preservar rastreabilidade suficiente até suas evidências de origem.

---

### 10. Prioridade de Implementação

Cada item poderá possuir uma prioridade de implementação.

As classificações iniciais são:

```text
CORE
ENRICHMENT
DERIVED
FUTURE
```

*CORE*

Informação necessária para estabelecer e validar o fluxo industrial fundamental do IMS.

Exemplos:

```text
cane_flow
hydraulic_pressure
equipment_state
trip_occurred
```
.

*ENRICHMENT*

Informação que amplia a compreensão do processo ou da condição dos equipamentos, mas não é necessária para validar o primeiro fluxo executável.

Exemplos:

```text
bearing_temperature
vibration_rms
```
.

*DERIVED*

Informação produzida a partir de evidências industriais primárias.

Exemplos:

```text
imbibition_ratio
runtime
operational_availability
```
.

*FUTURE*

Informação reconhecida como relevante, mas deliberadamente mantida fora do escopo atual de implementação.

Exemplo:

```text
raw_vibration_waveform
```

A prioridade de implementação não representa importância industrial.

Ela representa exclusivamente o **sequenciamento da implementação**.

---

### 11. Tipos de Origem

A informação poderá possuir diferentes mecanismos de origem semântica.

As classificações iniciais são:

```text
observed
derived
inferred
```

*11.1 - Observed*

Informação diretamente adquirida de uma fonte industrial.

```text
Industrial Source
      │
      ▼
 Observation
```

Exemplos:

- pressão;
- temperatura;
- corrente;
- velocidade;
- estado proveniente da automação.

.

*11.2 - Derived*

Informação calculada a partir de outras informações industriais.

```text
Industrial Evidence
      │
      ▼
Calculation
      │
      ▼
Derived Information
```

Exemplos:

- relação de embebição;
- runtime;
- consumo específico de energia.

.

*11.3 - Inferred*

Informação determinada por meio da interpretação conjunta de observações, estados ou eventos.

```text
Industrial Evidence
      │
      ▼
  Inference
      │
      ▼
Operational Context
```

Exemplos futuros podem incluir condições operacionais inferidas a partir do comportamento conjunto de múltiplas variáveis.

A origem da informação deverá permanecer rastreável sempre que sua semântica exigir.

---

### 12. Qualidade da Informação

Observações industriais primárias poderão carregar informação de qualidade.

O modelo inicial de qualidade do IMS será:

```text
GOOD
UNCERTAIN
BAD
UNKNOWN
```

O catálogo indicará a necessidade de qualidade por meio do atributo:

```yaml
quality_required: true
```

Representações específicas provenientes de protocolos ou equipamentos deverão ser normalizadas na fronteira apropriada de integração.

O Information Catalog define a necessidade semântica da qualidade, não sua codificação específica em cada tecnologia.

---

### 13. Comportamento Temporal

Cada informação poderá possuir um comportamento temporal correspondente à sua natureza.

As classificações iniciais incluem:

```text
continuous
discrete
counter
point_event
interval
derived
```

*Continuous*

Observação cuja grandeza pode variar continuamente ao longo do tempo.

Exemplos:

- pressão;
- temperatura;
- corrente;
- velocidade;
- vazão.

.

*Discrete*

Informação representada por estados discretos.

Exemplos:

- ligado/parado;
- manual/automático;
- local/remoto;
- interlock ativo/inativo.

.

*Counter*

Informação acumulativa.

Exemplo:

```text
start_count
```
.

*Point Event*

Ocorrência associada a um instante específico.

Exemplos:

- trip;
- alarme;
- partida.

.

*Interval*

Informação ou ocorrência associada a um período de validade.

.

*Derived*

Informação cujo comportamento temporal resulta do cálculo ou agregação de outras informações.

O comportamento temporal não representa frequência de aquisição.

Parâmetros como:

- sampling rate;
- polling interval;
- acquisition frequency;

pertencem à implementação técnica.

---

### 14. Relação com os Data Models

O Information Catalog não substitui os Data Models do IMS.

Os Data Models definem entidades, relações, identidade, temporalidade, contexto e estruturas de persistência.

O Information Catalog instancia essas definições para o domínio industrial da Moenda.

Conceitualmente:

```text
Data Model
    │
    ▼
Defines what structures can exist
    │
    ▼
Information Catalog
    │
    ▼
Defines which industrial information exists in IMS
```

Exemplo:

```text
Data Model

Variable
   │
   ▼
Information Catalog

hydraulic_pressure
```

O Data Model define o conceito de `Variable`.

O Information Catalog identifica `hydraulic_pressure` como uma informação concreta reconhecida pelo IMS.

---

### 15. Relação com a Implementação

O Information Catalog poderá servir como entrada semântica para diferentes componentes da implementação.

```text
Information Catalog
        │
        ├──► Database Seeds
        │
        ├──► Acquisition Mapping
        │
        ├──► Industrial Data Generator
        │
        ├──► Validation
        │
        └──► Documentation
```

Cada componente poderá utilizar diferentes aspectos do catálogo.

Componentes de implementação não deverão redefinir o significado industrial estabelecido pelo catálogo.

A relação esperada é:

```text
Information Catalog
        │
        ▼
Semantic Definition
        │
        ├──► Source Mapping
        ├──► Contract
        ├──► Persistence
        └──► Engineering Tooling
```

> Technology materializes the model; it does not define its meaning.

---

### 16. Relação com os Contratos

O Information Catalog define informações industriais.

Os contratos definem como essas informações são representadas durante a comunicação entre componentes.

Exemplo:

```text
Information Catalog
        │
        ▼
hydraulic_pressure
        │
        ▼
 Telemetry Event
        │
        ▼
  Avro Contract
        │
        ▼
      Kafka
```

O contrato poderá utilizar identificadores associados à informação, mas não deverá se tornar sua fonte de significado industrial.

Assim:

```text
Information Catalog
      ≠
Avro Schema
```

Ambos possuem responsabilidades distintas e complementares.

---

### 17. Relação com a Persistência

O Information Catalog também não representa diretamente o modelo físico do banco de dados.

A relação será:

```text
Information Catalog
        │
        ▼
Industrial Identity
        │
        ▼
  Database Seed
        │
        ▼
Physical Data Model
```

Por exemplo:

```text
hydraulic_pressure
        │
        ▼
industrial.variable
        │
        ▼
   variable_id
```

O banco materializa a identidade e as relações definidas pelo modelo industrial.

O catálogo preserva seu significado.

---

### 18. Regras de Evolução

Uma nova informação poderá ser adicionada ao catálogo quando:

1. possuir significado industrial claramente definido;
2. sua relação com o domínio da Moenda for conhecida;
3. sua classe de informação puder ser determinada;
4. sua identidade puder ser separada da localização técnica;
5. sua inclusão possuir justificativa dentro do escopo do IMS.

Uma informação existente não deverá receber nova identidade lógica exclusivamente porque:

- seu endereço no PLC foi alterado;
- seu protocolo de aquisição mudou;
- sua representação no banco foi modificada;
- sua representação em Kafka mudou;
- sua estratégia de amostragem mudou;
- sua infraestrutura de origem foi substituída.

Uma nova identidade deverá ser considerada quando houver alteração efetiva do **significado industrial**.

---

### 19. Versionamento

O Information Catalog será tratado como uma especificação viva e versionada.

Exemplo:

```text
1.0
1.1
1.2
2.0
```

Alterações compatíveis, como inclusão de novas informações dentro do modelo existente, poderão resultar em evolução incremental.

Alterações que modifiquem significativamente a semântica ou estrutura do catálogo deverão justificar mudança de versão correspondente.

O histórico de alterações será preservado pelo controle de versão do repositório.

---

### 20. Princípios de Governança

O Information Catalog deverá permanecer:

- semanticamente orientado;
- independente de tecnologia;
- versionado;
- legível por pessoas;
- processável por software;
- rastreável ao modelo industrial do IMS;
- separado de configurações específicas de aquisição.

O catálogo não deverá se transformar em um repositório genérico de configurações técnicas.

A responsabilidade fundamental permanece:

> O catálogo descreve a informação industrial. A tecnologia apenas materializa sua representação.

---

### 21. Fluxo de Responsabilidades

A separação entre os diferentes artefatos do IMS pode ser representada por:

```text
Industrial Engineering
        │
        ▼
       IPEM
        │
        ▼
  Architecture
        │
        ▼
       ADR
        │
        ▼
    Data Model
        │
        ▼
Information Catalog
        │
        ▼
Technical Mapping
        │
        ▼
    Contract
        │
        ▼
Runtime Implementation
```

Cada camada responde a uma pergunta distinta:

| Artefato | Pergunta |
|---|---|
| IPEM | O que a informação significa industrialmente? |
| ARCH | Como o sistema é organizado? |
| ADR | Por que determinada decisão foi adotada? |
| Data Model | Como a informação é modelada? |
| Information Catalog | Quais informações industriais concretas o IMS reconhece? |
| Source Mapping | Onde a informação está tecnicamente disponível? |
| Contract | Como a informação é representada em trânsito? |
| Implementation | Como a arquitetura é executada? |

Essa separação preserva a rastreabilidade entre conhecimento industrial, arquitetura, modelo e tecnologia.

---

### 22. Considerações Finais

O Information Catalog estabelece uma referência semântica comum entre o domínio industrial e a implementação do IMS.

Ele não representa:

- uma lista de tags;
- uma configuração de PLC;
- um schema de banco de dados;
- um contrato de mensageria;
- uma configuração de aquisição.

Ele representa as **informações industriais reconhecidas pelo sistema e seus respectivos significados**.

Dessa forma, o IMS pode alterar tecnologias, protocolos, estruturas de armazenamento ou mecanismos de transporte sem perder a continuidade semântica das informações que representa.

```text
Industrial Meaning
        │
        ▼
Information Catalog
        │
        ├──► Acquisition
        ├──► Contracts
        ├──► Persistence
        ├──► Processing
        └──► Analytics
```
> **Technology materializes the model; it does not define its meaning.**
