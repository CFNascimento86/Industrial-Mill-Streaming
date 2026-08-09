### 1. Introdução

O **Architecture Decision Records Governance** estabelece como decisões arquiteturais relevantes devem ser registradas, justificadas e preservadas ao longo da evolução do Industrial Mill Streaming (IMS).

Os ADRs constituem o elo entre os princípios definidos na arquitetura e as escolhas responsáveis por sua materialização.

Seu propósito não é documentar tecnologias individualmente, mas preservar o contexto, os critérios, as alternativas e as consequências das decisões que influenciam significativamente a arquitetura do IMS.

---

### 2. Decision Question

> **Como registrar decisões arquiteturais do IMS de forma concisa, rastreável e capaz de preservar seu contexto ao longo da evolução do projeto?**

Essa pergunta orienta a governança dos Architecture Decision Records.

---

### 3. Princípio de Governança

*Decision in Context*

> **Toda decisão arquitetural relevante deve ser registrada juntamente com o contexto que a originou, os critérios que a orientaram e as consequências decorrentes de sua adoção.**

Uma decisão isolada informa **o que foi escolhido**. Uma decisão contextualizada preserva **por que foi escolhida**.

---

### 4. Unidade de Decisão

Um ADR deve representar uma **unidade arquitetural coerente**.

Isso significa que decisões conceitualmente relacionadas podem permanecer no mesmo documento quando fizerem parte da mesma cadeia de raciocínio.

```text id="8qf37c"
     Context
        │
        ▼
Decision Drivers
        │
        ▼
Architectural Decision
        │
        ▼
Technology Decision
        │
        ▼
    Consequences
```

A decisão tecnológica, quando existente, deve materializar a decisão arquitetural e não substituí-la.

---

### 5. Architectural Decision e Technology Decision

O IMS distingue dois níveis de decisão dentro de um mesmo contexto.

*5.1 - Architectural Decision*

Define **qual abordagem arquitetural será adotada** para responder ao problema identificado.

Exemplos conceituais:

* comunicação orientada a eventos;
* estratégia de persistência;
* abordagem de aquisição;
* modelo de execução distribuída.

.  

*5.2 - Technology Decision*

Define **qual tecnologia materializará a decisão arquitetural**, quando essa escolha possuir relevância suficiente para ser registrada.

Exemplo:

```text id="d5v7ax"
    Problema
        │
        ▼
Necessidade de comunicação
desacoplada e assíncrona
        │
        ▼
Architectural Decision
Event-Driven Architecture
        │
        ▼
Technology Decision
Apache Kafka
```

Nem todo ADR precisa conter uma Technology Decision. Da mesma forma, a simples utilização de uma tecnologia no projeto não justifica a criação de um ADR.

---

### 6. Critérios para Criação de um ADR

Uma decisão deve ser registrada quando apresentar impacto relevante sobre pelo menos um dos seguintes aspectos:

* estrutura da arquitetura;
* integração entre componentes;
* modelo de dados;
* interoperabilidade;
* escalabilidade;
* disponibilidade;
* confiabilidade;
* governança;
* evolução futura;
* custo ou complexidade operacional;
* dependência tecnológica;
* trade-offs significativos.

Decisões locais, reversíveis e de baixo impacto devem permanecer na documentação de implementação.

---

### 7. Estrutura Padrão

Os ADRs do IMS devem seguir, sempre que aplicável, a seguinte estrutura:

```text id="20vnpu"
ADR-XXX — Título

1. Context
2. Decision Drivers
3. Architectural Decision
4. Technology Decision
5. Alternatives Considered
6. Rationale
7. Consequences
8. Related Architecture
9. Decision Status
```

Seções que não forem aplicáveis podem ser omitidas, desde que a decisão permaneça compreensível.

---

### 8. Context

O **Context** descreve o problema ou condição que exige uma decisão.

Deve responder:

> **Por que precisamos decidir?**

O contexto deve apresentar apenas as informações necessárias para compreender a decisão, evitando transformar o ADR em documentação técnica extensa.

---

### 9. Decision Drivers

Os **Decision Drivers** representam os critérios que influenciam a escolha.

Podem incluir:

* requisitos arquiteturais;
* restrições industriais;
* interoperabilidade;
* desempenho;
* disponibilidade;
* escalabilidade;
* maturidade tecnológica;
* simplicidade operacional;
* custo;
* capacidade de evolução.

Os drivers permitem compreender quais critérios tiveram maior influência sobre a decisão.

---

### 10. Alternatives Considered

Alternativas tecnicamente plausíveis devem ser registradas quando contribuírem para compreender a decisão.

O objetivo não é produzir comparações exaustivas.

A seção deve responder:

> **Quais opções relevantes foram consideradas e por que não foram adotadas?**

Alternativas evidentemente incompatíveis com os requisitos não precisam ser documentadas.

---

### 11. Rationale

O **Rationale** registra por que a decisão adotada apresenta o melhor equilíbrio diante do contexto, dos drivers e das alternativas consideradas.

Uma decisão arquitetural não precisa representar a solução perfeita.

Ela deve representar a solução mais adequada às condições conhecidas no momento da decisão.

---

### 12. Consequences

Toda decisão arquitetural produz consequências.

Elas devem ser registradas de forma explícita.

```text id="ky3a5j"
Consequences
     │
     ├── Positive
     │
     ├── Negative
     │
     └── Risks / Trade-offs
```

Consequências negativas não invalidam uma decisão. Sua documentação demonstra que os trade-offs foram conscientemente aceitos.

---

### 13. Related Architecture

Todo ADR deve manter rastreabilidade com os documentos arquiteturais que justificam a decisão.

Exemplo:

```text id="20f8kq"
ARCH
Princípio Arquitetural
        │
        ▼
       ADR
     Decisão
        │
        ▼
  Implementation
  Materialização
```

Sempre que aplicável, o ADR deve referenciar:

* IPEM relacionado;
* ARCH relacionado;
* outros ADRs relacionados;
* modelos de dados afetados;
* componentes de implementação relevantes.

---

### 14. Decision Status

Os ADRs devem possuir estado explícito.

```text id="vqp80a"
 Proposed
    │
    ▼
 Accepted
    │
    ├────────► Deprecated
    │
    └────────► Superseded
```

*Proposed*

Decisão em avaliação.

.

*Accepted*

Decisão aprovada e válida para a arquitetura.

.

*Deprecated*

Decisão que deixou de ser recomendada, mas permanece registrada historicamente.

.

*Superseded*

Decisão substituída total ou parcialmente por outro ADR.

---

### 15. Evolução das Decisões

ADRs aceitos constituem registros históricos e não devem ser reescritos para representar novas decisões.

Quando uma decisão relevante mudar, um novo ADR deve registrar:

* o novo contexto;
* a nova decisão;
* sua justificativa;
* o ADR substituído.

O documento anterior deve permanecer preservado e receber apenas a referência para a decisão que o substituiu.

---

### 16. Supersession Parcial

Uma decisão tecnológica pode ser substituída sem invalidar a decisão arquitetural que a originou.

Exemplo:

```text id="lwh06r"
     ADR-01
        │
        ├── Architectural Decision
        │       Event-Driven Architecture
        │       Status: Accepted
        │
        └── Technology Decision
                Apache Kafka
                Status: Superseded
                        │
                        ▼
                     ADR-XX
```

Essa abordagem permite evolução tecnológica sem perda do histórico ou da coerência arquitetural.

---

### 17. Rastreabilidade das Decisões

As decisões do IMS devem seguir, sempre que aplicável, a seguinte cadeia:

```text id="bwxhps"
Processo Industrial
        │
        ▼
    IPEM
    Engenharia
        │
        ▼
ARCH
Princípio Arquitetural
        │
        ▼
     ADR
     Decisão
        │
        ▼
    Tecnologia
        │
        ▼
  Implementation
        │
        ▼
      Código
```

Essa rastreabilidade permite compreender não apenas **como** uma solução foi implementada, mas **por que ela existe**.

---

### 18. Considerações Finais

Os Architecture Decision Records constituem a memória decisória do IMS.

Seu valor não está na quantidade de documentos produzidos, mas na capacidade de preservar decisões que influenciam significativamente a arquitetura.

Um ADR deve registrar contexto suficiente para que uma decisão possa ser compreendida mesmo quando as pessoas, tecnologias e condições que participaram de sua criação tiverem mudado.

> **Arquitetura define princípios. ADRs preservam decisões. Implementação materializa consequências.**

Dessa forma, o IMS mantém uma cadeia contínua entre engenharia, arquitetura, decisão e implementação, preservando conhecimento técnico ao longo de toda a evolução do projeto.
