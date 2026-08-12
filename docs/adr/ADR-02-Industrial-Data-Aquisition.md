## ADR-02 — Industrial Data Acquisition

| Campo             | Valor                                 |
| ----------------- | ------------------------------------- |
| **Documento**     | ADR-02                                |
| **Título**        | Industrial Data Acquisition           |
| **Versão**        | 1.0                                   |
| **Status**        | Accepted                              |
| **Projeto**       | Industrial Mill Streaming — IMS       |
| **Especificação** | Architecture Decision Records — ADR   |
| **Derivação**     | IPEM-06 / IPEM-07 / ARCH-01 / ARCH-03 |

---

### 1. Context

O Industrial Mill Streaming (IMS) necessita adquirir dados de processo provenientes de um CLP Siemens S7-1500 sem interferir nas responsabilidades da Engenharia de Controle e Automação.

A infraestrutura de automação já existe e constitui a autoridade sobre o processo industrial.

O IMS deve utilizar os dados disponibilizados por essa infraestrutura como fonte para sua arquitetura de dados, preservando a separação entre controle e digitalização.

Nesta fase do projeto, o domínio de referência utiliza uma única arquitetura principal de aquisição.

---

### 2. Decision Drivers

A decisão considera os seguintes direcionadores:

* integração não intrusiva com a automação;
* aquisição predominantemente read-only;
* preservação da autoridade do sistema de controle;
* baixo acoplamento entre protocolo e modelo lógico;
* compatibilidade com Siemens S7-1500;
* simplicidade arquitetural;
* rastreabilidade até a fonte;
* facilidade de manutenção;
* capacidade de evolução futura;
* aderência ao princípio Incremental Industrial Adoption.

---

### 3. Architectural Decision

*Decoupled Acquisition Boundary*

> **O IMS adotará uma fronteira de aquisição desacoplada, responsável por receber dados da infraestrutura industrial e convertê-los de sua representação técnica para o modelo lógico da plataforma.**

A camada de aquisição permanecerá isolada das demais capacidades da arquitetura.

Sua responsabilidade será limitada a:

* conectar-se à fonte industrial;
* adquirir os dados autorizados;
* preservar origem e timestamp;
* executar validações iniciais;
* converter a representação técnica para o modelo lógico do IMS;
* encaminhar a informação para a camada de integração.

```text id="7khp93"
 Siemens S7-1500
        │
        ▼
 Protocol Client
        │
        ▼
Raw Observation
        │
        ▼
     Mapping
        │
        ▼
IMS Telemetry Model
        │
        ▼
Event Streaming
```

O conhecimento específico da fonte deve permanecer concentrado na fronteira de aquisição.

---

### 4. Operational Boundary

A aquisição será **predominantemente read-only**.

> **O IMS consome informações do sistema de controle; ele não assume autoridade sobre o processo industrial.**

Esta decisão não autoriza a plataforma a:

* alterar lógica de controle;
* modificar parâmetros operacionais;
* escrever comandos diretamente no PLC;
* alterar permissivos;
* modificar intertravamentos;
* substituir funções de supervisão;
* atuar sobre estratégias de controle.

Qualquer futura necessidade de escrita ou atuação sobre sistemas OT deverá ser tratada por decisão arquitetural específica.

---

### 5. Technology Decision

*OPC UA*

> **OPC UA será adotado como protocolo principal de aquisição de dados entre o Siemens S7-1500 e o IMS, considerando sua disponibilidade no controlador e sua aderência à integração padronizada entre OT e IT.**

A escolha busca reduzir a dependência de estruturas internas de memória do controlador e utilizar uma interface mais adequada à exposição estruturada de informações industriais.

A utilização de OPC UA permite que o IMS trabalhe sobre identificadores e variáveis expostas pela automação sem propagar detalhes de endereçamento interno para as demais camadas da arquitetura.

```text id="sw3dsn"
 S7-1500
   │
   ▼
OPC UA
   │
   ▼
Acquisition Service
   │
   ▼
IMS Logical Model
   │
   ▼
 Kafka
```

---

### 6. Internal Acquisition Structure

A implementação da aquisição deverá preservar separação de responsabilidades.

```text id="olrn2j"
Protocol Client
      │
      ▼
    Mapper
      │
      ▼
Telemetry Model
      │
      ▼
  Publisher
```

**Protocol Client**

Responsável exclusivamente pela comunicação com a fonte industrial.

.

**Mapper**

Responsável por converter a representação disponibilizada pela fonte para o modelo lógico do IMS.

.

**Telemetry Model**

Representa a informação de forma padronizada e contextualizada.

.

**Publisher**

Responsável por encaminhar a telemetria para a arquitetura de integração definida no ADR-01.

Essa estrutura preserva o desacoplamento entre aquisição, modelagem e event streaming.

---

### 7. Alternatives Considered

*7.1 - S7 Protocol*

O acesso nativo por S7 Protocol permite comunicação direta com estruturas internas do controlador.

Essa abordagem pode ser adequada em cenários brownfield ou quando OPC UA não estiver disponível.

Entretanto, no contexto atual do IMS, sua utilização aumentaria a dependência de elementos como:

* blocos de dados;
* offsets;
* tipos internos;
* organização específica do programa do PLC.

Por esse motivo, S7 Protocol não foi selecionado como interface principal nesta versão.

Ele permanece uma alternativa válida para cenários futuros em que as restrições da infraestrutura assim exigirem.

.

*7.2 - MQTT*

MQTT é adequado para publicação de telemetria em gateways, dispositivos IoT e arquiteturas distribuídas.

Entretanto, no cenário atual, ele não representa a interface natural entre o controlador S7-1500 e o IMS.

MQTT poderá ser utilizado futuramente em outras topologias de aquisição, sem alterar a decisão de integração interna orientada a eventos definida no ADR-01.

---

### 8. Rationale

A decisão combina simplicidade operacional com desacoplamento arquitetural.

```text id="lfxorn"
Infraestrutura Existente
        │
        ▼
Necessidade de Aquisição Segura
        │
        ▼
Architectural Decision
Decoupled Acquisition Boundary
        │
        ▼
Technology Decision
OPC UA
```

A fronteira de aquisição impede que particularidades técnicas da fonte se propaguem pela arquitetura.

OPC UA atende ao cenário atual do Siemens S7-1500 e permite uma integração mais estruturada sem exigir uma abstração genérica multiprotocolo.

A escolha preserva a possibilidade de evolução futura sem antecipar complexidade.

---

### 9. Consequences

*9.1 - Positive*

A decisão proporciona:

* separação entre Automação e Engenharia de Dados;
* integração não intrusiva;
* menor dependência da estrutura interna do PLC;
* simplificação da aquisição.

.

*9.2 - Negative*

A decisão introduz:

* dependência da disponibilidade e configuração adequada do OPC UA no controlador;
* necessidade de mapeamento entre nós OPC UA e entidades IMS;
* necessidade de tratar disponibilidade, qualidade e reconexão;
* dependência parcial da interface exposta pela automação.

---

### 10. Boundaries

Este ADR não define:

* configuração do servidor OPC UA;
* configuração do PLC;
* arquitetura de redes industriais;
* políticas de OT Cybersecurity;
* configuração de firewalls;
* frequência definitiva de coleta;
* estrutura física dos nós OPC UA;
* contratos Kafka;
* estrutura física de persistência.

Esses elementos pertencem à Automação, OT Cybersecurity, implementação ou decisões arquiteturais posteriores.

---

### 11. Related Architecture

| Documento   | Relação                                                     |
| ----------- | ----------------------------------------------------------- |
| **IPEM-06** | Estabelece a instrumentação como origem da informação       |
| **IPEM-07** | Define o Telemetry Model                                    |
| **ARCH-00** | Define tecnologia como consequência da arquitetura          |
| **ARCH-01** | Estabelece Logical Abstraction Over Existing Infrastructure |
| **ARCH-03** | Define a integração entre aquisição e event streaming       |
| **ARCH-04** | Define a proximidade da aquisição com o processo industrial |
| **ADR-01**  | Define Event-Driven Integration e Apache Kafka              |

---

### 12. Decision Status

*Architectural Decision*

**Decoupled Acquisition Boundary — Accepted**

.

*Technology Decision*

**OPC UA — Accepted**

As duas decisões possuem ciclos de vida relacionados, porém independentes.

Uma futura mudança de protocolo não invalida necessariamente a decisão arquitetural de manter a aquisição desacoplada do restante da plataforma.

Caso o IMS evolua para múltiplas fontes e protocolos, uma nova decisão poderá estabelecer uma arquitetura de adapters sem alterar os princípios fundamentais definidos neste documento.

---

### 13. Considerações Finais

O ADR-02 estabelece que a aquisição industrial do IMS deve permanecer simples, desacoplada e não intrusiva.

A arquitetura reconhece que o sistema de Controle e Automação permanece como autoridade sobre o processo, enquanto o IMS atua exclusivamente sobre as informações disponibilizadas por essa infraestrutura.

OPC UA será utilizado como protocolo principal para a integração com o Siemens S7-1500, enquanto a fronteira de aquisição impedirá que particularidades técnicas da fonte contaminem o restante da arquitetura.

```text id="881nlc"
Processo Industrial
        │
        ▼
 Siemens S7-1500
        │
        ▼
     OPC UA
        │
        ▼
Acquisition Boundary
        │
        ▼
IMS Telemetry Model
        │
        ▼
      Kafka
        │
        ▼
   Consumidores
```

Dessa forma, o IMS implementa apenas a complexidade necessária para o domínio atual, mantendo sua arquitetura preparada para evoluir quando novos requisitos surgirem.

> **Design for extension. Implement for the current requirement.**
