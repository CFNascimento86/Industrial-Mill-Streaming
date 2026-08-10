## ADR-01 — Event-Driven Integration

|    Campo	    |             Valor                   |
|---------------|-------------------------------------|
| Documento	    | ADR-01                              |
| Título	      | Event-Driven Integration            |
| Versão	      | 1.0                                 |
| Status	      | Accepted                            |
| Projeto       |	Industrial Mill Streaming — IMS     |
| Especificação |	Architecture Decision Records — ADR |
| Derivação     |	IPEM-08 / ARCH-03                   |

---

### 1. Context

O Industrial Mill Streaming (IMS) necessita distribuir informações industriais entre diferentes capacidades da arquitetura sem estabelecer dependências diretas entre produtores e consumidores.

Uma mesma informação pode ser utilizada simultaneamente por persistência, processamento, contextualização, analytics ou novos consumidores incorporados posteriormente.

```text
Aquisição Industrial
        │
        ▼
      Evento
        │
        ├────► Persistência
        ├────► Processamento
        ├────► Contextualização
        ├────► Analytics
        └────► Novos Consumidores
```

Uma arquitetura predominantemente baseada em integrações ponto a ponto aumentaria progressivamente o acoplamento entre componentes e dificultaria sua evolução independente.

O IMS necessita, portanto, de um modelo de integração capaz de distribuir eventos de forma assíncrona, desacoplada e escalável, preservando a possibilidade de reprocessamento quando necessário.

---

### 2. Decision Drivers

A decisão considera os seguintes direcionadores:

* desacoplamento entre produtores e consumidores;
* comunicação assíncrona;
* suporte a múltiplos consumidores independentes;
* retenção de eventos;
* capacidade de replay;
* ordenação quando requerida pelo contexto;
* escalabilidade horizontal;
* resiliência;
* integração incremental de novos consumidores;
* aderência a tecnologias abertas e ecossistemas consolidados.

---

### 3. Architectural Decision

*Event-Driven Architecture*

> **O IMS adotará Event-Driven Architecture como modelo predominante para distribuição assíncrona de eventos entre capacidades desacopladas da plataforma.**

Produtores devem publicar acontecimentos relevantes sem conhecer os consumidores que utilizarão essas informações.

Consumidores devem reagir aos eventos de acordo com suas próprias responsabilidades e manter independência em relação à implementação dos produtores.

```text
 Produtor
    │
    ▼
  Evento
    │
    ▼
Integração
    │
    ├────► Consumidor A
    ├────► Consumidor B
    └────► Consumidor N
```

A arquitetura orientada a eventos será **predominante, mas não exclusiva**.

Comunicações síncronas, APIs e processamento em lote poderão ser utilizados quando apresentarem maior adequação à responsabilidade arquitetural.

O IMS não estabelece que toda interação deva ser representada como evento.

---

### 4. Technology Decision

*Apache Kafka*

> **Apache Kafka será adotado como plataforma de event streaming responsável pela distribuição e retenção dos eventos assíncronos do IMS.**

A escolha fundamenta-se nas seguintes capacidades:

#### *Durable Event Log*

Eventos podem permanecer disponíveis após seu consumo, preservando histórico dentro das políticas de retenção estabelecidas.


#### *Replay*

Consumidores podem reprocessar eventos anteriormente publicados quando necessário.


#### *Consumer Independence*

Diferentes consumidores podem processar os mesmos eventos de forma independente.


#### *Partitioning*

Eventos podem ser distribuídos entre partições para suportar paralelismo e preservar ordenação dentro dos limites definidos pela estratégia de particionamento.


#### *Horizontal Scalability*

A plataforma permite expansão conforme aumentam volume de eventos, processamento e quantidade de consumidores.


#### *Open Ecosystem*

Apache Kafka possui ecossistema aberto e consolidado, alinhado ao posicionamento tecnológico do IMS.

---

### 5. Alternatives Considered

*5.1 - RabbitMQ*

RabbitMQ oferece um modelo maduro de message broker e apresenta forte aderência a cenários de filas, roteamento e entrega de mensagens.

Entretanto, o IMS necessita tratar eventos também como registros reutilizáveis por consumidores independentes, com retenção e capacidade de replay como propriedades relevantes.

Por essa razão, RabbitMQ não foi selecionado como backbone principal de event streaming.

.

*5.2 - MQTT*

MQTT apresenta forte aderência a cenários industriais, IoT, gateways e publicação eficiente de telemetria.

Entretanto, conectividade com fontes e distribuição interna de eventos representam responsabilidades arquiteturais distintas.

MQTT poderá ser utilizado futuramente em pontos específicos da aquisição sem substituir necessariamente a plataforma de event streaming.

```text
Dispositivo / Gateway
        │
       MQTT
        │
        ▼
   Aquisição IMS
        │
        ▼
  Apache Kafka
        │
        ├────► Persistência
        ├────► Processamento
        └────► Analytics
```

Portanto, MQTT não é considerado incompatível com a decisão adotada.

As duas tecnologias podem coexistir quando atenderem responsabilidades distintas.

.

*5.3 - Integração Ponto a Ponto / REST*

Integrações síncronas são adequadas para requisições específicas e determinadas interações entre serviços.

Entretanto, sua utilização como mecanismo predominante para distribuição de eventos criaria dependências diretas entre produtores e consumidores.

REST poderá ser utilizado em integrações síncronas específicas, mas não será adotado como backbone da distribuição assíncrona do IMS.

---

### 6. Rationale

A decisão combina dois níveis complementares.

```text
Necessidade Arquitetural
        │
        ▼
Comunicação Assíncrona e Desacoplada
        │
        ▼
Architectural Decision
Event-Driven Architecture
        │
        ▼
Technology Decision
Apache Kafka
```

Event-Driven Architecture atende à necessidade de desacoplar produtores e consumidores e permitir evolução independente das capacidades.

Apache Kafka materializa essa decisão oferecendo retenção, replay, múltiplos consumidores independentes, particionamento e escalabilidade.

A escolha não decorre da popularidade da tecnologia, mas de sua aderência aos requisitos estabelecidos pela arquitetura IMS.

---

### 7. Consequences

*7.1 - Positive*

A decisão proporciona:

* desacoplamento entre produtores e consumidores;
* integração assíncrona;
* possibilidade de múltiplos consumidores;
* retenção e replay de eventos;
* expansão incremental da arquitetura;
* escalabilidade horizontal;
* isolamento entre diferentes responsabilidades de processamento.

.

*7.2 - Negative*

A decisão introduz:

* maior complexidade operacional;
* necessidade de monitoramento da plataforma de eventos;
* necessidade de governança de tópicos;
* necessidade de gestão dos contratos de eventos;
* maior exigência de conhecimento técnico da equipe;
* novos componentes de infraestrutura.

.

*7.3 - Risks / Trade-offs*

A utilização inadequada de Event-Driven Architecture pode gerar:

* proliferação excessiva de eventos;
* contratos inconsistentes;
* dependências semânticas implícitas;
* dificuldade de rastreamento entre fluxos;
* complexidade operacional desnecessária.

Por esse motivo, a arquitetura orientada a eventos deve ser aplicada onde gerar valor arquitetural e não como regra universal de integração.

> **O IMS aceita maior complexidade de infraestrutura em troca de desacoplamento, retenção de eventos, capacidade de replay e evolução independente dos consumidores.**

---

### 8. Boundaries

Esta decisão não estabelece:

* estrutura física dos tópicos;
* convenções de nomenclatura;
* número de partições;
* replication factor;
* políticas específicas de retenção;
* formato físico das mensagens;
* estratégia de serialização;
* configuração do cluster;
* parâmetros de produtores e consumidores.

Esses aspectos pertencem às especificações de implementação ou a decisões posteriores quando apresentarem relevância arquitetural própria.

---

### 9. Related Architecture

A decisão possui relação direta com os seguintes documentos:

| Documento   | Relação                                                           |
| ----------- | ----------------------------------------------------------------- |
| **IPEM-08** | Estabelece o EVENT-MODEL e preservação do contexto dos eventos    |
| **ARCH-00** | Estabelece tecnologia como consequência da arquitetura            |
| **ARCH-02** | Define o enriquecimento progressivo da informação                 |
| **ARCH-03** | Estabelece Communication Through Events                           |
| **ARCH-04** | Define a distribuição das capacidades entre ambientes de execução |
| **ARCH-05** | Estabelece confiança, rastreabilidade e governança da informação  |

---

### 10. Decision Status

*Architectural Decision*

**Event-Driven Architecture — Accepted**

*Technology Decision*

**Apache Kafka — Accepted**

As duas decisões permanecem relacionadas, porém possuem ciclos de vida independentes.

Uma futura substituição da tecnologia de event streaming não invalida necessariamente a decisão arquitetural por Event-Driven Architecture.

Quando uma mudança tecnológica relevante ocorrer, um novo ADR deverá registrar a decisão e referenciar parcialmente este documento como **Superseded**.

---

### 11. Considerações Finais

O ADR-01 estabelece Event-Driven Architecture como modelo predominante de integração assíncrona do IMS e Apache Kafka como tecnologia responsável por materializar suas capacidades de event streaming.

A decisão preserva o desacoplamento entre paradigma arquitetural e implementação tecnológica sem fragmentá-los em documentos independentes.

```text
   IPEM-08
   Event Model
        │
        ▼
ARCH-03
Communication Through Events
        │
        ▼
ADR-01
Event-Driven Integration
        │
        ├── Event-Driven Architecture
        │
        └── Apache Kafka
        │
        ▼
  Implementation
```

Dessa forma, Apache Kafka não constitui o ponto de partida da arquitetura.

Ele representa uma consequência tecnológica de uma necessidade previamente estabelecida pela Engenharia e formalizada pela Arquitetura.

> **Primeiro definimos como a informação deve circular. Depois escolhemos a tecnologia capaz de materializar essa decisão.**
