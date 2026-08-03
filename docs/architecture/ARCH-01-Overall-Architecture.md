### 1. Introdução

O **Overall Architecture** apresenta a organização lógica de alto nível do Industrial Mill Streaming (IMS).

O IMS é concebido para operar sobre uma infraestrutura industrial existente composta por ativos, instrumentos, controladores, redes e sistemas previamente definidos pela Engenharia de Controle e Automação.

Sua responsabilidade consiste em abstrair os dados disponibilizados por essa infraestrutura, preservar seu contexto industrial e transformá-los em informações organizadas para processamento, análise e tomada de decisão.

Este documento estabelece apenas a visão geral da arquitetura. Tecnologias, produtos, configurações e modelos físicos serão definidos nos documentos arquiteturais posteriores e nos Architecture Decision Records (ADRs).

---

### 2. Architectural Question

> **Como organizar logicamente os dados provenientes de uma infraestrutura industrial existente, preservando seu contexto e disponibilizando-os para processamento, análise e decisão?**

Essa pergunta orienta toda a camada arquitetural do IMS.

---

### 3. Contexto e Limites

O IMS é direcionado principalmente a ambientes industriais brownfield, nos quais coexistem tecnologias de diferentes gerações, protocolos heterogêneos e sistemas críticos de operação.

A arquitetura deve respeitar a infraestrutura existente e atuar de forma não intrusiva, sem comprometer:

* segurança operacional;
* disponibilidade dos sistemas de controle;
* determinismo;
* desempenho dos controladores;
* continuidade da produção.

O IMS não projeta instrumentação, redes industriais, estratégias de controle, intertravamentos ou filosofias de alarmes.

Seu escopo inicia-se quando os dados industriais tornam-se disponíveis para consumo pela arquitetura de dados.

---

### 4. Princípio Arquitetural

#### *Logical Abstraction Over Existing Infrastructure*

> **O IMS deve construir uma camada lógica orientada ao processo sobre a infraestrutura industrial existente, abstraindo particularidades físicas e tecnológicas sem perder a rastreabilidade até as fontes de origem.**

A arquitetura deve separar o significado industrial da informação de sua representação técnica.

Exemplo:

```text
Representação técnica:
PLC-01 / DB101 / Offset 4 / REAL

Representação lógica:
Moenda 01 / Motor Principal / Corrente Elétrica / A
```

A representação técnica informa onde e como o dado está disponível.

A representação lógica informa o que esse dado significa no processo.

---

### 5. Fronteira entre Automação e IMS

A Engenharia de Controle e Automação é responsável por disponibilizar os dados do processo por meio da infraestrutura operacional existente.

O IMS utiliza esses dados como origem para sua arquitetura lógica.

```text
Processo Industrial
        │
        ▼
Engenharia de Controle e Automação
        │
        ├── Instrumentação
        ├── Controladores
        ├── Redes Industriais
        ├── Sistemas Supervisórios
        ├── Controle
        └── Alarmes
        │
        ▼
Dados Disponíveis
        │
        ─────────────────────────
        │
        ▼
Industrial Mill Streaming — IMS
        │
        ├── Aquisição
        ├── Abstração
        ├── Contextualização
        ├── Processamento
        ├── Governança
        └── Disponibilização
```

Essa separação preserva os limites entre as disciplinas e evita que a arquitetura de dados redefina conceitos já estabelecidos pela engenharia da planta.

---

### 6. Visão de Alto Nível

A arquitetura IMS é organizada como um fluxo de capacidades responsáveis por transformar dados técnicos em informações contextualizadas.

```text
Infraestrutura Industrial Existente
        │
        ▼
Aquisição e Integração
        │
        ▼
Abstração e Contextualização
        │
        ▼
Persistência e Processamento
        │
        ▼
Governança e Observabilidade
        │
        ▼
Disponibilização e Analytics
        │
        ▼
   Investigação
        │
        ▼
     Decisão
        │
        ▼
      Ação
```

O diagrama representa a progressão lógica da informação e não necessariamente uma sequência física linear.

As capacidades podem operar de forma distribuída, paralela, contínua, em lote ou orientada a eventos.

---

### 7. Domínios Arquiteturais

#### *7.1 - Infraestrutura Industrial Existente*

Representa as fontes que originam ou disponibilizam os dados industriais.

Inclui conceitualmente:

* ativos;
* instrumentação;
* PLCs;
* sistemas supervisórios;
* historiadores;
* gateways;
* sistemas de alarmes.

Esse domínio não é controlado pelo IMS.


#### *7.2 - Aquisição e Integração*

Responsável por conectar a arquitetura às fontes industriais existentes e encaminhar os dados para a plataforma.

Suas principais responsabilidades incluem:

* conexão com as fontes;
* leitura dos dados;
* captura da origem e do timestamp;
* validações iniciais;
* proteção dos sistemas de automação;
* comunicação entre produtores e consumidores.


#### *7.3 - Abstração e Contextualização*

Responsável por transformar estruturas técnicas de origem em representações lógicas orientadas ao processo industrial.

Suas responsabilidades incluem:

* identificação lógica de ativos e variáveis;
* associação com o domínio e o processo;
* padronização semântica;
* preservação da origem;
* aplicação dos modelos definidos no IPEM.

Esse domínio constitui o principal mecanismo de desacoplamento da arquitetura.


#### *7.4 - Persistência e Processamento*

Responsável por armazenar, transformar e organizar os dados industriais.

Suas responsabilidades incluem:

* preservação dos dados de origem;
* armazenamento histórico;
* validação;
* limpeza;
* padronização;
* enriquecimento;
* correlação;
* agregação;
* preparação de eventos, indicadores e modelos analíticos.


#### *7.5 - Governança e Observabilidade*

Responsável por garantir que os dados e a própria plataforma permaneçam rastreáveis, compreensíveis e confiáveis.

Suas responsabilidades incluem:

* metadados;
* qualidade dos dados;
* linhagem;
* auditoria;
* monitoramento;
* gestão de falhas;
* observabilidade dos pipelines;
* acompanhamento de latência e disponibilidade.

Esse domínio atua de forma transversal sobre toda a arquitetura.


#### *7.6 - Disponibilização e Analytics*

Responsável por entregar informações contextualizadas aos consumidores da plataforma.

Inclui conceitualmente:

* APIs;
* conjuntos analíticos;
* indicadores;
* relatórios;
* dashboards;
* aplicações corporativas;
* análise exploratória;
* suporte à investigação e decisão.

Os consumidores não devem acessar diretamente estruturas técnicas de aquisição ou armazenamento bruto.

---

### 8. Princípios Complementares

Além do princípio principal, a arquitetura IMS deve observar as seguintes diretrizes:

* **Brownfield by Design:** compatibilidade com ambientes industriais existentes.
* **Non-Intrusive Integration:** mínima interferência sobre os sistemas de controle.
* **Source Decoupling:** consumidores independentes das estruturas técnicas das fontes.
* **Context Preservation:** manutenção do significado industrial durante todo o fluxo.
* **Stable Logical Identity:** identidades lógicas independentes de endereços e protocolos.
* **Traceability by Design:** rastreabilidade incorporada desde a origem.
* **Loose Coupling:** evolução independente entre capacidades.
* **Engineering Knowledge Preservation:** preservação da semântica definida pela engenharia da planta.
* **Context Before KPI:** indicadores associados às condições operacionais que os produziram.
* **Architecture Before Implementation:** tecnologias escolhidas como consequência da arquitetura.

---

### 9. Relação com o IPEM

A arquitetura IMS deriva diretamente dos modelos de engenharia estabelecidos no Industrial Process & Event Model.

```text
Modelos IPEM
        +
Infraestrutura Industrial Existente
        │
        ▼
Arquitetura Lógica IMS
        │
        ▼
Decisões Arquiteturais
        │
        ▼
Implementação Tecnológica
```

O ARCH-01 não redefine domínio, processo, ativos, telemetrias, eventos ou KPIs.

Ele estabelece a estrutura lógica necessária para sustentá-los tecnicamente.

---

### 10. Próximos Documentos

| Documento                                 | Responsabilidade                                                     |
| ----------------------------------------- | -------------------------------------------------------------------- |
| **ARCH-02 — Data Architecture**           | Definir como os dados são organizados, transformados e persistidos   |
| **ARCH-03 — Integration Architecture**    | Definir como fontes, componentes e consumidores se comunicam         |
| **ARCH-04 — Infrastructure Architecture** | Definir ambientes, distribuição computacional e execução             |
| **ARCH-05 — Security Architecture**       | Definir identidade, acesso, proteção e auditoria                     |
| **ARCH-06 — Analytics Architecture**      | Definir como informações são disponibilizadas para análise e decisão |
| **ADR**                                   | Registrar e justificar decisões tecnológicas específicas             |
| **Data Model — DM**                       | Especificar modelos conceituais, lógicos e físicos dos dados         |
| **Implementation**                        | Materializar a arquitetura por meio de tecnologias e código          |

---

### 11. Considerações Finais

O ARCH-01 estabelece o IMS como uma camada lógica construída sobre uma realidade industrial existente.

A arquitetura não substitui a automação nem redefine o conhecimento operacional da planta.

Seu propósito é abstrair estruturas técnicas, preservar a origem dos dados e organizá-los segundo os modelos de domínio, processo, ativos, telemetrias, eventos e indicadores definidos no IPEM.

Dessa forma, o IMS atua como uma ponte entre a realidade física e a realidade informacional.

```text
Realidade Física e Operacional
        │
        ▼
Arquitetura Lógica IMS
        │
        ▼
Informação Contextualizada
        │
        ▼
   Investigação
        │
        ▼
     Decisão
        │
        ▼
      Ação
```

O ARCH-01 fornece a visão geral necessária para orientar os documentos arquiteturais posteriores, preservando objetividade, clareza e separação de responsabilidades.
