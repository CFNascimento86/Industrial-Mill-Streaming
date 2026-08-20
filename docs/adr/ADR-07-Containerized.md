## ADR-07 — Containerized Runtime Architecture

| Campo             | Valor                                                         |
| ----------------- | ------------------------------------------------------------- |
| **Documento**     | ADR-07                                                        |
| **Título**        | Containerized Runtime Architecture                            |
| **Versão**        | 1.0                                                           |
| **Status**        | Accepted                                                      |
| **Projeto**       | Industrial Mill Streaming — IMS                               |
| **Especificação** | Architecture Decision Records — ADR                           |
| **Derivação**     | ARCH-04 / ADR-01 / ADR-02 / ADR-03 / ADR-04 / ADR-05 / ADR-06 |

---

### 1. Context

O Industrial Mill Streaming (IMS) é composto por diferentes capacidades independentes responsáveis por aquisição, integração, processamento, governança de contratos e persistência das informações industriais.

Essas capacidades possuem:

* dependências próprias;
* ciclos de execução independentes;
* requisitos distintos de configuração;
* diferentes responsabilidades arquiteturais.

A execução direta de todos os componentes no sistema operacional hospedeiro aumentaria o acoplamento entre dependências e dificultaria:

* reprodução do ambiente;
* instalação;
* atualização;
* isolamento;
* testes;
* onboarding;
* portabilidade.

O IMS necessita, portanto, de uma estratégia de execução capaz de empacotar seus componentes de forma previsível e reproduzível, sem introduzir uma plataforma de orquestração cuja complexidade exceda os requisitos atuais do projeto.

---

### 2. Decision Drivers

A decisão considera os seguintes direcionadores:

* isolamento entre componentes;
* reprodutibilidade;
* portabilidade;
* padronização do ambiente;
* preservação de dados persistentes;
* facilidade de integração;
* onboarding simplificado;
* compatibilidade com tecnologias abertas;

---

### 3. Architectural Decision

*Containerized Services*

> **Os componentes executáveis do IMS serão organizados como serviços containerizados, preservando isolamento de dependências e responsabilidades independentes de execução.**

Cada serviço deverá corresponder a uma responsabilidade arquitetural coerente.

Conceitualmente:

```text
┌───────────────────────────┐
│    Acquisition Service    │
│         Container         │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│       Apache Kafka        │
│        Container(s)       │
└─────────────┬─────────────┘
              │
        ┌─────┴─────┐
        ▼           ▼
┌──────────────┐ ┌──────────────┐
│ Processing   │ │ Persistence  │
│ Service      │ │ Consumer     │
└──────────────┘ └──────┬───────┘
                        ▼
                 ┌──────────────┐
                 │ PostgreSQL   │
                 └──────────────┘
```

A containerização deverá materializar as responsabilidades definidas na arquitetura, e não introduzir novas divisões sem justificativa.

---

### 4. Service Boundaries

A fronteira de um container deverá refletir uma **responsabilidade executável coerente**.

O IMS não adotará inicialmente uma estratégia de fragmentação excessiva como:

```text
temperature-validator
pressure-validator
unit-converter
telemetry-mapper
event-enricher
quality-checker
```

quando essas capacidades fizerem parte do mesmo ciclo de processamento.

Será preferida uma organização como:

```text
ims-acquisition

ims-processing

ims-persistence
```

Cada serviço poderá possuir módulos internos responsáveis por funções relacionadas.

Exemplo:

```text
ims-processing/
│
├── validation/
├── transformation/
├── contextualization/
├── correlation/
└── derivation/
```

A criação de novos serviços deverá ser justificada por critérios como:

* escalabilidade independente;
* isolamento de falhas;
* ciclo de vida distinto;
* ownership diferente;
* responsabilidade arquitetural própria.

---

### 5. Technology Decision - A

*Docker*

> **Docker será adotado como tecnologia de containerização dos componentes executáveis do IMS.**

A escolha fundamenta-se principalmente em:

* isolamento de dependências;
* ambientes reproduzíveis;
* portabilidade;
* padronização de runtime;
* facilidade de distribuição;
* amplo suporte ao ecossistema tecnológico utilizado pelo IMS;
* baixo custo de adoção;
* adequação ao ambiente de desenvolvimento e referência do projeto.

Conceitualmente:

```text
Application
    +
Dependencies
    +
 Runtime
    │
    ▼
Container Image
    │
    ▼
 Container
```

A imagem deverá representar o comportamento executável do serviço de forma independente das configurações específicas do ambiente.

---

### 6. Technology Decision - B

*Docker Compose*

> **Docker Compose será adotado como mecanismo de orquestração do ambiente de desenvolvimento e da implantação de referência inicial do IMS.**

Seu objetivo será permitir que os principais componentes do projeto sejam inicializados e integrados de forma reproduzível.

Conceitualmente:

```text
docker compose up
        │
        ▼
┌──────────────────────────────┐
│ IMS Reference Environment    │
│                              │
│ Apache Kafka                 │
│ Apicurio Registry            │
│ PostgreSQL                   │
│ Acquisition Service          │
│ Processing Service           │
│ Persistence Consumer         │
└──────────────────────────────┘
```

Docker Compose será utilizado porque atende ao nível atual de complexidade do projeto sem exigir uma plataforma distribuída de orquestração.

---

### 7. Externalized Configuration

As imagens dos serviços não deverão possuir configurações específicas de ambiente incorporadas diretamente ao código ou à imagem.

A arquitetura adotará o princípio:

> **Images package behavior. Configuration defines environment.**

Conceitualmente:

```text
Container Image
     │
     ├── Application
     ├── Dependencies
     └── Runtime

Environment Configuration
     │
     ├── Environment Variables
     ├── Configuration Files
     └── Secrets
```

Essa abordagem permitirá reutilizar uma mesma imagem em diferentes ambientes.

```text
Development
      │
      ▼
   Testing
      │
      ▼
Reference Deployment
```

Alterações entre ambientes deverão ocorrer prioritariamente por configuração e não por modificação do código ou reconstrução específica da aplicação.

---

### 8. Secrets

Credenciais, senhas, tokens, certificados e outras informações sensíveis não deverão ser incorporadas ao código-fonte ou às imagens dos containers.

```text
Application Image
      │
      X
Hardcoded Secret
```

O IMS deverá utilizar mecanismos externos de configuração para disponibilização de informações sensíveis durante a execução.

A tecnologia definitiva para gestão centralizada de segredos poderá evoluir conforme a infraestrutura do projeto.

Este ADR estabelece apenas a responsabilidade arquitetural.

---

### 9. Persistent State

Containers serão tratados como unidades de execução descartáveis.

Dados persistentes não deverão depender do ciclo de vida do container.

Conceitualmente:

```text
Container
   │
   X Removed / Recreated
   │

Persistent Storage
   │
   └── Data remains available
```

Componentes stateful, como PostgreSQL e serviços que necessitem preservar estado, deverão utilizar mecanismos externos de persistência apropriados.

A estratégia física de volumes será definida durante a implementação.

---

### 10. Stateless and Stateful Responsibilities

O IMS deverá distinguir componentes principalmente stateless daqueles que mantêm estado persistente.

*Stateless Components*

Exemplos conceituais:

* Acquisition Service;
* Processing Service, quando não possuir estado persistente;
* consumidores de eventos sem armazenamento próprio.

Esses componentes devem poder ser recriados sem perda de informações persistentes.

*Stateful Components*

Exemplos:

* PostgreSQL;
* event streaming;
* Schema Registry quando possuir estado próprio.

Sua execução requer mecanismos capazes de preservar informações independentemente da instância do container.

```text
Runtime Components
      │
      ├── Stateless
      │      │
      │      └── Replaceable Runtime
      │
      └── Stateful
             │
             └── External Persistent State
```

Essa distinção deverá orientar a implementação e futuras estratégias de infraestrutura.

---

### 11. Service Health

A arquitetura deverá distinguir entre:

```text
Container Started
```

e:

```text
Service Ready
```

Um container em execução não significa necessariamente que seu serviço esteja pronto para receber tráfego ou processar eventos.

Por esse motivo, os componentes deverão fornecer mecanismos apropriados de verificação de saúde sempre que aplicável.

Conceitualmente:

```text
Container
    │
    ▼
Process Running
    │
    ▼
Dependency Check
    │
    ▼
Service Healthy
```

Exemplos de condições relevantes:

* Kafka disponível;
* PostgreSQL aceitando conexões;
* Registry disponível;
* serviço Python inicializado;
* dependências essenciais acessíveis.

Essa capacidade permitirá startup mais previsível e melhor tratamento de falhas.

---

### 12. Dependency Readiness

Dependências entre serviços deverão considerar disponibilidade real dos componentes necessários.

Uma sequência como:

```text
Start PostgreSQL
      │
      ▼
Start Persistence Consumer
```

não deverá assumir que o banco está imediatamente pronto apenas porque seu container foi iniciado.

Conceitualmente:

```text
Dependency
    │
    ▼
Health Check
    │
    ├── Not Ready
    │       │
    │       └── Wait / Retry
    │
    ▼
Ready
    │
    ▼
Dependent Service
```

A implementação deverá evitar dependências baseadas apenas na ordem de inicialização dos containers.

---

### 13. Networking

Os componentes containerizados deverão comunicar-se por interfaces e endpoints explicitamente definidos.

Conceitualmente:

```text
Acquisition Service
        │
        ▼
      Kafka
        │
        ▼
Processing Service
        │
        ▼
      Kafka
        │
        ▼
Persistence Consumer
        │
        ▼
    PostgreSQL
```

O networking interno não deverá expor desnecessariamente serviços ao ambiente externo.

Somente interfaces necessárias para desenvolvimento, administração ou consumo autorizado deverão ser publicadas externamente.

A configuração detalhada das redes Docker pertence à implementação.

---

### 14. Logging

Logs produzidos pelos serviços deverão ser tratados como saída operacional do componente e não armazenados exclusivamente dentro do filesystem efêmero do container.

```text
Container
   │
   ▼
Application Logs
   │
   ▼
External Log Access
```

A estratégia centralizada de observabilidade poderá ser definida posteriormente.

Este ADR estabelece apenas que a remoção ou substituição de um container não deverá impedir o acesso operacional aos logs necessários à investigação.

---

### 15. Reproducible Environment

O ambiente de referência deverá permitir que um desenvolvedor reproduza o núcleo do IMS com o menor número possível de etapas manuais.

Conceitualmente:

```text
Git Repository
      │
      ▼
Configuration
      │
      ▼
Docker Compose
      │
      ▼
IMS Runtime Environment
```

O objetivo é reduzir configurações manuais da máquina e tornar o repositório executável de forma previsível.

Essa característica é especialmente relevante para:

* desenvolvimento;
* testes;
* demonstração;
* onboarding;
* avaliação técnica do projeto.

---

### 16. Container Image Responsibilities

Cada imagem deverá conter somente os elementos necessários para executar sua responsabilidade.

O IMS evitará imagens que acumulem aplicações arquiteturalmente distintas.

Não será adotado um modelo como:

```text
ims-all-in-one
│
├── acquisition
├── processing
├── persistence
├── database
└── monitoring
```

quando esses componentes possuírem ciclos de vida e responsabilidades independentes.

A arquitetura deverá favorecer:

```text
ims-acquisition
ims-processing
ims-persistence
```

e utilizar imagens especializadas para componentes de infraestrutura.

---

### 17. Versioning of Images

As imagens produzidas pelo IMS deverão possuir identificação de versão suficiente para permitir reprodução e rastreabilidade.

A arquitetura não deverá depender exclusivamente de referências mutáveis como:

```text
latest
```

em ambientes nos quais reprodutibilidade seja relevante.

A convenção definitiva de versionamento será definida na implementação e no pipeline de CI/CD.

O objetivo arquitetural é permitir identificar qual versão de um componente estava sendo executada.

---

### 18. Local Development and Reference Deployment

O Docker Compose será utilizado principalmente para dois objetivos.

*Local Development*

Permitir execução integrada dos componentes durante desenvolvimento.

*Reference Deployment*

Fornecer uma implementação reproduzível da arquitetura IMS para demonstração e validação.

```text
Same Architecture
      │
      ├── Local Development
      │
      └── Reference Deployment
```

Essa decisão não estabelece Docker Compose como plataforma definitiva para todos os cenários de produção.

A infraestrutura de produção poderá exigir outro modelo de execução conforme disponibilidade, escala e requisitos operacionais.

---

### 19. Rationale

A decisão busca equilibrar:

```text
Reproducibility
      │
      │
Isolation ─────── Simplicity
      │
      ▼
   Docker
     +
Docker Compose
```

O IMS precisa de um ambiente integrado capaz de reproduzir sua arquitetura sem introduzir complexidade de infraestrutura incompatível com seu estágio atual.

Docker fornece isolamento e empacotamento.

Docker Compose fornece coordenação suficiente para o ambiente inicial.

A arquitetura permanece preparada para migrar para outras plataformas de execução quando requisitos concretos justificarem essa mudança.

---

### 20. Consequences

*20.1 - Positive*

A decisão proporciona:

* isolamento de dependências;
* ambiente reproduzível;
* maior portabilidade;
* onboarding simplificado;
* implantação local consistente;
* independência entre serviços.

*20.2 - Negative*

A decisão introduz:

* necessidade de gerenciamento de imagens;
* networking entre containers;
* gerenciamento de volumes;
* configuração de health checks;
* maior quantidade de processos independentes;
* necessidade de compreender lifecycle dos containers.

*20.3 - Risks / Trade-offs*

Containerização simplifica reprodução, mas introduz uma nova camada operacional.

Docker Compose reduz complexidade, porém não fornece todas as capacidades de uma plataforma distribuída de produção.

Esse trade-off é conscientemente aceito.

> **O IMS aceita a complexidade operacional básica da containerização em troca de isolamento, reprodutibilidade e evolução independente dos componentes.**

---

### 21. Boundaries

Este ADR não define:

* configuração física das redes;
* volumes específicos;
* CPU limits;
* memory limits;
* políticas de restart;
* estratégia centralizada de logs;
* pipeline CI/CD;
* infraestrutura definitiva de produção.

Esses elementos pertencem à implementação ou a ADRs posteriores quando possuírem relevância arquitetural.

---

### 22. Related Architecture

| Documento   | Relação                                                                        |
| ----------- | ------------------------------------------------------------------------------ |
| **ARCH-00** | Estabelece tecnologia como consequência da arquitetura                         |
| **ARCH-04** | Define Distributed by Responsibility e ambientes de execução                   |
| **ARCH-05** | Estabelece responsabilidades relacionadas à confiança e proteção da plataforma |
| **ADR-01**  | Define Apache Kafka como backbone de eventos                                   |
| **ADR-02**  | Define o Acquisition Service                                                   |
| **ADR-03**  | Define PostgreSQL e responsabilidades de persistência                          |
| **ADR-04**  | Define Apicurio Registry e contratos                                           |
| **ADR-05**  | Define Python Processing Service                                               |
| **ADR-06**  | Define topologia e semântica operacional do Kafka                              |

---

### 23. Considerações Finais

O ADR-07 estabelece como os componentes do IMS serão executados de forma reproduzível, isolada e proporcional ao estágio atual do projeto.

Docker será utilizado para empacotar serviços e dependências.

Docker Compose coordenará o ambiente de desenvolvimento e a implantação de referência inicial.

Os containers refletirão responsabilidades arquiteturais coerentes, enquanto configuração e estado persistente permanecerão externos ao ciclo de vida das imagens e instâncias.

```text
                    IMS Runtime

                 Docker Compose
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
 Acquisition        Kafka         Apicurio
   Service                           Registry
        │              │
        └───────┬──────┘
                ▼
         Processing Service
                │
                ▼
              Kafka
                │
                ▼
       Persistence Consumer
                │
                ▼
           PostgreSQL
```

A arquitetura permanecerá preparada para evoluir para mecanismos de orquestração mais avançados sem introduzi-los antes que necessidades concretas de escala ou disponibilidade existam.

> **A infraestrutura deve materializar a arquitetura, não dominar sua complexidade.**

> **Empacotar para reproduzir. Isolar para evoluir. Orquestrar apenas na medida em que o problema exigir.**
