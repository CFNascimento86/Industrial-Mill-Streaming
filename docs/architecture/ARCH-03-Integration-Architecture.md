### 1. Introdução

O **Integration Architecture** estabelece como as informações circulam entre as capacidades do Industrial Mill Streaming (IMS).

Seu objetivo é definir um modelo de integração que permita a comunicação entre componentes da plataforma de forma desacoplada, rastreável e escalável, preservando a independência entre produtores e consumidores.

Este documento define princípios arquiteturais de integração.

A seleção de tecnologias, protocolos e ferramentas será formalizada posteriormente por meio dos respectivos Architecture Decision Records (ADR).

---

### 2. Architectural Question

> **Como as informações circulam entre as capacidades da arquitetura IMS preservando desacoplamento, confiabilidade e rastreabilidade?**

Essa pergunta orienta toda a arquitetura de integração.

---

### 3. Princípio Arquitetural

*Communication Through Events*

> **As capacidades da arquitetura IMS devem trocar informações por meio de eventos e contratos bem definidos, reduzindo dependências diretas entre produtores e consumidores.**

Esse princípio garante que cada capacidade evolua de forma independente, preservando estabilidade, escalabilidade e flexibilidade para futuras integrações.

---

### 4. Objetivos da Integração

A arquitetura de integração do IMS deve:

* desacoplar produtores e consumidores;
* preservar o contexto da informação;
* permitir evolução independente entre componentes;
* minimizar dependências diretas;
* favorecer integração incremental;
* suportar múltiplos consumidores;
* preservar rastreabilidade;
* possibilitar escalabilidade horizontal.

---

### 5. Modelo Conceitual de Integração

A arquitetura organiza o fluxo de informações por meio de uma camada intermediária de integração.

```text
    Produtores
        │
        ▼
     Eventos
        │
        ▼
Camada de Integração
        │
        ▼
   Consumidores
```

Os produtores não conhecem seus consumidores.

Da mesma forma, consumidores não dependem da implementação específica dos produtores.

Ambos compartilham apenas contratos de informação.

---

### 6. Papéis Arquiteturais

#### *6.1 - Produtores*

São responsáveis por disponibilizar informações relevantes para a arquitetura.

Exemplos:

* aquisição de dados;
* processamento;
* geração de eventos;
* monitoramento da plataforma.

Sua responsabilidade termina no momento em que a informação é publicada.


#### *6.2 - Camada de Integração*

Representa o mecanismo responsável por intermediar a comunicação.

Suas responsabilidades incluem:

* distribuição das informações;
* desacoplamento entre componentes;
* preservação dos contratos;
* entrega para múltiplos consumidores;
* suporte à evolução da arquitetura.

Essa camada constitui o núcleo da arquitetura de integração.


#### *6.3 - Consumidores*

São responsáveis por utilizar as informações produzidas pela arquitetura.

Podem incluir:

* persistência;
* processamento;
* analytics;
* APIs;
* aplicações corporativas;
* dashboards;
* modelos analíticos.

Novos consumidores podem ser incorporados sem exigir alterações nos produtores.

---

### 7. Contratos de Informação

A comunicação entre componentes deve ocorrer por meio de contratos claramente definidos.

Os contratos estabelecem:

* significado da informação;
* estrutura lógica;
* regras de compatibilidade;
* identificação das entidades;
* metadados essenciais.

Dessa forma, produtores e consumidores permanecem independentes da implementação interna uns dos outros.

---

### 8. Fronteira OT/IT

O IMS estabelece uma fronteira lógica entre os ambientes operacional (OT) e corporativo (IT).

```text
OT
(Processo Industrial)
        │
        ▼
     Aquisição
        │
──────── Fronteira OT / IT ────────
        │
        ▼
     Integração
        │
        ▼
   Processamento
        │
        ▼
     Analytics
        │
        ▼
    Consumidores
```

Essa separação preserva a estabilidade da automação e reduz impactos sobre os sistemas responsáveis pelo controle do processo.

---

### 9. Diretrizes Arquiteturais

A arquitetura de integração deve garantir que:

* componentes permaneçam desacoplados;
* consumidores possam evoluir independentemente;
* novos produtores possam ser incorporados sem impacto significativo;
* contratos permaneçam estáveis;
* eventos preservem o contexto industrial;
* integrações sejam rastreáveis;
* falhas permaneçam isoladas sempre que possível.

---

### 10. Relação com os Próximos Documentos

O ARCH-03 estabelece **como** as capacidades da arquitetura se comunicam.

Os documentos seguintes definirão:

| Documento                                 | Responsabilidade                                            |
| ----------------------------------------- | ----------------------------------------------------------- |
| **ARCH-04 — Infrastructure Architecture** | Onde essas capacidades serão executadas                     |
| **ARCH-05 — Security Architecture**       | Como a integração será protegida                            |
| **ARCH-06 — Analytics Architecture**      | Como as informações serão disponibilizadas aos consumidores |
| **ADR**                                   | Qual tecnologia implementará essa arquitetura de integração |

---

### 11. Considerações Finais

O Integration Architecture estabelece que a comunicação dentro do IMS deve ocorrer por meio de uma arquitetura orientada a eventos, preservando baixo acoplamento entre produtores e consumidores.

Ao adotar contratos de informação e uma camada dedicada de integração, a arquitetura favorece escalabilidade, reutilização e evolução contínua sem comprometer a estabilidade dos sistemas industriais existentes.

Dessa forma, o IMS consolida uma arquitetura capaz de integrar o ambiente operacional e o ambiente analítico sem romper as fronteiras entre Engenharia de Controle e Automação e Engenharia de Dados Industrial.

```text
    Produtores
        │
        ▼
     Eventos
        │
        ▼
    Integração
        │
        ▼
   Consumidores
        │
        ▼
   Investigação
        │
        ▼
     Decisão
```
