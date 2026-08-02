### 1. Introdução

O **Overall Architecture** estabelece a visão arquitetural de alto nível do Industrial Mill Streaming (IMS).

Este documento define como as capacidades da plataforma devem ser organizadas para transformar dados provenientes de uma infraestrutura industrial existente em informações contextualizadas, governadas e disponíveis para processamento, análise e tomada de decisão.

O IMS é concebido como uma arquitetura de digitalização industrial aplicada predominantemente a ambientes existentes, nos quais os ativos, instrumentos, controladores, redes, sistemas supervisórios e tecnologias de automação já foram previamente definidos pela Engenharia de Controle e Automação.

Consequentemente, a arquitetura IMS não parte de uma infraestrutura física projetada especificamente para a plataforma de dados.

Seu ponto de partida é a realidade operacional existente.

A responsabilidade do IMS consiste em construir sobre essa realidade uma camada lógica capaz de:

* abstrair particularidades físicas e tecnológicas;
* preservar a rastreabilidade até as fontes;
* contextualizar dados segundo o processo industrial;
* desacoplar produtores e consumidores de informação;
* organizar o fluxo de dados ao longo da plataforma;
* sustentar eventos, indicadores e aplicações analíticas;
* disponibilizar informações confiáveis para investigação e decisão.

O ARCH-01 não especifica produtos, serviços ou configurações de implementação.

Seu objetivo é estabelecer a estrutura lógica da arquitetura, suas capacidades, limites, princípios e relacionamentos fundamentais.

---

### 2. Architectural Question

> **Como organizar logicamente os dados provenientes de uma infraestrutura industrial existente, preservando seu contexto e disponibilizando-os para processamento, análise e decisão?**

Essa pergunta delimita o propósito do ARCH-01.

O documento não busca definir como projetar a automação industrial nem como implementar cada componente da plataforma.

Ele define como as capacidades de Engenharia de Dados Industrial devem ser organizadas para representar digitalmente uma operação física já estabelecida.

---

### 3. Contexto Arquitetural

O IMS é concebido para ambientes industriais caracterizados pela coexistência de diferentes gerações de tecnologia.

Esses ambientes podem apresentar:

* controladores legados;
* sistemas modernos de automação;
* redes industriais heterogêneas;
* diferentes protocolos de comunicação;
* nomenclaturas não padronizadas;
* estruturas proprietárias de dados;
* restrições de conectividade;
* sistemas locais e aplicações em nuvem;
* diferentes níveis de maturidade digital;
* dependência de sistemas críticos de operação.

Essa condição é especialmente relevante em projetos de digitalização industrial realizados sobre instalações existentes.

A arquitetura deve, portanto, ser capaz de evoluir sem exigir a substituição integral da infraestrutura de controle e automação.

O IMS adota uma abordagem compatível com ambientes brownfield, reconhecendo que a transformação digital industrial frequentemente ocorre por meio da integração progressiva de tecnologias novas com ativos e sistemas preexistentes.

---

### 4. Escopo

O ARCH-01 abrange a organização lógica das capacidades necessárias para o funcionamento da arquitetura IMS.

O documento contempla:

* integração com fontes industriais existentes;
* aquisição de dados;
* abstração das estruturas técnicas de origem;
* contextualização industrial;
* ingestão e movimentação de dados;
* comunicação desacoplada;
* persistência;
* processamento;
* modelagem de dados;
* governança;
* observabilidade;
* disponibilização;
* consumo analítico;
* rastreabilidade entre as camadas.

---

### 5. Princípio Arquitetural

*Logical Abstraction Over Existing Infrastructure*

> **O IMS deve construir uma camada lógica orientada ao processo sobre a infraestrutura industrial existente, abstraindo particularidades físicas e tecnológicas sem perder a rastreabilidade até as fontes de origem.**

Esse princípio reconhece que a infraestrutura responsável pela execução, controle e supervisão do processo industrial antecede a arquitetura IMS.

O IMS não substitui essa infraestrutura nem redefine sua organização física.

Sua função é transformar dados originados em estruturas técnicas específicas em representações lógicas estáveis, compreensíveis e reutilizáveis.

A abstração deve impedir que consumidores analíticos e aplicações corporativas dependam diretamente de detalhes como:

* endereço de memória;
* número de bloco de dados;
* nome interno de tag;
* fabricante do controlador;
* protocolo de comunicação;
* estrutura física da rede;
* convenções específicas do sistema de automação.

Entretanto, abstrair não significa eliminar a origem.

A arquitetura deve preservar os metadados necessários para rastrear qualquer informação até sua fonte física e técnica.

---

### 6. Fronteira entre Automação e IMS

A arquitetura IMS respeita a separação entre a Engenharia de Controle e Automação e a Engenharia de Dados Industrial.

 *6.1 - Responsabilidades da Engenharia de Controle e Automação*

Pertencem à Engenharia de Controle e Automação, entre outras responsabilidades:

* definição da instrumentação;
* especificação dos controladores;
* configuração das redes industriais;
* definição dos sistemas supervisórios;
* disponibilização dos protocolos;
* implementação das estratégias de controle;
* programação das lógicas operacionais;
* estabelecimento de permissivos e intertravamentos;
* definição da filosofia de alarmes;
* garantia do determinismo e da continuidade do controle.

 *6.2 - Responsabilidades do IMS*

Pertencem à arquitetura IMS:

* integração não intrusiva com fontes existentes;
* aquisição dos dados disponibilizados pela automação;
* abstração das particularidades técnicas;
* contextualização segundo os modelos IPEM;
* organização lógica das informações;
* persistência e processamento;
* governança e rastreabilidade;
* disponibilização para aplicações analíticas;
* suporte à investigação e à tomada de decisão.

Essa fronteira pode ser representada da seguinte forma:

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
        ├── Intertravamentos
        └── Alarmes
        │
        ▼
Interfaces e Dados Disponíveis
        │
        ─────────────────────────────
        │
        ▼
Industrial Mill Streaming — IMS
        │
        ├── Aquisição
        ├── Abstração
        ├── Contextualização
        ├── Ingestão
        ├── Persistência
        ├── Processamento
        ├── Governança
        └── Disponibilização
```

O IMS começa onde a informação industrial se torna tecnicamente disponível para consumo externo ao sistema de controle.

---

### 7. Architectural Decision Drivers

As decisões arquiteturais do IMS devem ser orientadas por um conjunto explícito de direcionadores.


*7.1 - Brownfield by Design*

A arquitetura deve ser adequada a ambientes industriais existentes.

Ela deve ser capaz de integrar tecnologias legadas e modernas sem exigir a reconstrução da automação da planta.

Essa diretriz implica considerar:

* diversidade tecnológica;
* restrições dos sistemas existentes;
* baixa tolerância a interrupções;
* dependência de fornecedores;
* ciclos longos de vida dos ativos;
* evolução incremental da digitalização.
  

*7.2 - Non-Intrusive Integration*

A integração do IMS deve minimizar qualquer interferência sobre os sistemas responsáveis pelo controle do processo.

A arquitetura de dados não deve comprometer:

* segurança operacional;
* disponibilidade da automação;
* determinismo;
* desempenho dos controladores;
* capacidade das redes industriais;
* continuidade da produção.

A aquisição deve respeitar os limites operacionais e técnicos estabelecidos pela automação.


*7.3 - Source Decoupling*

Consumidores de informação não devem depender diretamente da estrutura técnica das fontes industriais.

Mudanças em controladores, protocolos, endereços ou sistemas de origem não devem exigir alterações generalizadas em toda a plataforma.

A dependência técnica deve permanecer concentrada nas capacidades responsáveis pela aquisição e integração.


*7.4 - Context Preservation*

Os dados devem manter sua relação com o processo, os ativos, a instrumentação, os eventos e os indicadores definidos nos modelos IPEM.

A movimentação entre componentes não deve eliminar o significado industrial da informação.


*7.5 - Stable Logical Identity*

Entidades industriais devem possuir identidades lógicas estáveis.

A identidade de um ativo, de uma variável ou de uma telemetria não deve depender exclusivamente do endereço físico ou do nome técnico utilizado pelo sistema de origem.

Por exemplo:

```text
Identidade técnica variável:
DB101.DBD4

Identidade lógica estável:
1º Terno / Nível do Donelly
```

A origem técnica pode ser alterada sem modificar o significado da entidade lógica.

---

*7.6 - Traceability by Design*

A rastreabilidade deve ser incorporada desde a aquisição.

Toda informação relevante deve poder ser relacionada a:

* fonte física;
* interface técnica;
* ativo;
* processo;
* telemetria;
* evento;
* indicador;
* transformação aplicada;
* instante de processamento.

A rastreabilidade não deve ser adicionada apenas nas camadas analíticas.


*7.7 - Loose Coupling*

As capacidades da arquitetura devem possuir baixo acoplamento.

Aquisição, comunicação, persistência, processamento e consumo devem evoluir com o mínimo possível de dependências rígidas entre si.


*7.8 - Technology as an Enabler*

As tecnologias devem materializar capacidades arquiteturais previamente definidas.

Produtos e serviços não devem determinar o significado do dado, os limites das responsabilidades ou a organização conceitual da plataforma.


*7.9 - Engineering Knowledge Preservation*

A arquitetura deve preservar o conhecimento estabelecido pelas disciplinas responsáveis pela planta.

Eventos, alarmes, classificações, contextos operacionais e indicadores não devem ser reinterpretados de forma conflitante pela plataforma de dados.


*7.10 - Context Before KPI*

Indicadores devem permanecer relacionados às condições operacionais que produziram seus resultados.

A arquitetura deve permitir que o consumidor navegue do KPI até eventos, telemetrias, ativos e processos associados.

---

### 8. Representações da Informação

O IMS distingue diferentes formas de representação do mesmo fenômeno industrial.

*8.1 - Representação Física*

Responde à pergunta:

> **Onde o dado é produzido ou armazenado?**

Exemplos:

* instrumento de campo;
* controlador;
* bloco de dados;
* endereço de memória;
* servidor supervisório;
* equipamento de borda.


*8.2 - Representação Técnica*

Responde à pergunta:

> **Como o dado é acessado, codificado ou transportado?**

Exemplos:

* protocolo;
* tipo de dado;
* método de leitura;
* frequência de coleta;
* formato de mensagem;
* interface de comunicação.


*8.3 - Representação Lógica*

Responde à pergunta:

> **O que o dado representa no processo industrial?**

Exemplos:

* temperatura da embebição;
* pressão de vapor;
* vazão de alimentação;
* disponibilidade de um ativo.


*8.4 - Representação Analítica*

Responde à pergunta:

> **Como a informação será utilizada para análise e decisão?**

Exemplos:

* consumo específico por tonelada;
* disponibilidade por turno;
* duração média do ciclo;
* impacto de paradas no OEE.


*8.5 - Relacionamento entre as representações*

```text
Representação Física
        │
        ▼
Representação Técnica
        │
        ▼
Representação Lógica
        │
        ▼
Representação Analítica
```

Exemplo:

```text
PLC-01 / DB101 / Offset 4
        │
        ▼
Leitura por protocolo industrial / REAL
        │
        ▼
Turbina 01 / Temperatura do Mancal / °C
        │
        ▼
Temperatura média por Turno
```

A arquitetura deve preservar o relacionamento entre todas essas representações.

---

### 9. Visão Geral da Arquitetura

A arquitetura IMS é organizada como uma sequência de capacidades responsáveis por transformar dados industriais em informações disponíveis para investigação e decisão.

```text
Infraestrutura Industrial Existente
        │
        ▼
    Aquisição
        │
        ▼
Abstração Lógica
        │
        ▼
Contextualização Industrial
        │
        ▼
Ingestão e Comunicação
        │
        ▼
   Persistência
        │
        ▼
Processamento e Transformação
        │
        ▼
Modelos de Informação
        │
        ▼
Disponibilização
        │
        ▼
Analytics e Aplicações
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

Essa sequência não representa obrigatoriamente uma cadeia física linear.

Algumas capacidades podem operar de forma distribuída, paralela, orientada a eventos ou em diferentes ambientes computacionais.

O diagrama representa a progressão lógica da informação.

---

### 10. Domínios Arquiteturais

Para fins de organização, a arquitetura IMS é dividida em domínios lógicos.

*10.1 - Industrial Source Domain*

Representa os sistemas e componentes industriais que originam ou disponibilizam dados.

Inclui conceitualmente:

* instrumentos;
* ativos;
* PLCs;
* sistemas supervisórios;
* historiadores;
* gateways;
* sistemas de gestão de alarmes;
* aplicações industriais existentes.

Esse domínio não é controlado pela arquitetura IMS, ele constitui sua principal origem de informação.


*10.2 - Edge and Acquisition Domain*

Responsável por estabelecer a interface entre as fontes industriais e a plataforma de dados.

Suas responsabilidades incluem:

* conexão com fontes;
* leitura dos dados;
* controle da frequência de aquisição;
* captura de timestamps;
* identificação da origem;
* validações iniciais;
* buffer temporário, quando necessário;
* proteção dos sistemas de automação contra excesso de requisições;
* encaminhamento dos dados para ingestão.

Esse domínio concentra as dependências técnicas das fontes.


*10.3 - Integration and Communication Domain*

Responsável pelo transporte e intercâmbio das informações entre as capacidades da arquitetura.

Suas responsabilidades incluem:

* desacoplamento entre produtores e consumidores;
* entrega de dados;
* comunicação assíncrona;
* movimentação em lote;
* comunicação por eventos;
* tratamento de falhas de entrega;
* controle de contratos de integração;
* interoperabilidade entre ambientes.

Esse domínio pode suportar diferentes padrões de comunicação conforme a natureza do dado e do caso de uso.


*10.4 - Storage Domain*

Responsável pela persistência dos dados ao longo de seus diferentes níveis de transformação.

Suas responsabilidades incluem:

* preservação dos dados de origem;
* armazenamento histórico;
* organização por camadas;
* suporte a diferentes formatos;
* retenção;
* recuperação;
* particionamento;
* disponibilidade para processamento;
* manutenção da rastreabilidade.

O armazenamento não deve ser tratado como uma única estrutura universal. Pois, diferentes necessidades podem exigir diferentes modelos de persistência.


*10.5 - Processing Domain*

Responsável por transformar dados adquiridos em informações contextualizadas e utilizáveis.

Suas responsabilidades incluem:

* limpeza;
* padronização;
* validação;
* enriquecimento;
* contextualização;
* correlação;
* agregação;
* detecção de inconsistências;
* geração de eventos da plataforma;
* preparação de modelos analíticos;
* cálculo de indicadores.

O processamento deve preservar a origem e as transformações realizadas.


*10.6 - Information Model Domain*

Responsável por materializar os conceitos definidos no IPEM dentro da arquitetura de dados.

Esse domínio organiza as representações de:

* domínio industrial;
* processos;
* ativos;
* instrumentação;
* telemetrias;
* eventos;
* indicadores;
* metadados;
* qualidade;
* linhagem.

O Information Model Domain constitui o elo entre a Engenharia de Processo e a arquitetura técnica.


*10.7 - Governance and Observability Domain*

Responsável por garantir que a plataforma permaneça compreensível, rastreável, segura e operacionalmente observável.

Suas responsabilidades incluem:

* metadados;
* catálogo;
* linhagem;
* qualidade de dados;
* auditoria;
* monitoramento;
* registro de falhas;
* gestão de acessos;
* políticas de retenção;
* versionamento de contratos;
* observabilidade de pipelines;
* acompanhamento de latência e disponibilidade.

A governança e a observabilidade são capacidades transversais e elas não devem ser tratadas como uma etapa executada apenas ao final do fluxo.


*10.8 - Data Serving Domain*

Responsável por disponibilizar informações para diferentes consumidores.

Suas responsabilidades incluem:

* exposição de dados contextualizados;
* fornecimento de conjuntos analíticos;
* disponibilização de indicadores;
* acesso por aplicações;
* integração com sistemas corporativos;
* atendimento a consultas;
* controle de contratos de consumo;
* isolamento entre modelos internos e interfaces externas.

Esse domínio deve evitar que consumidores acessem diretamente estruturas técnicas de aquisição ou armazenamento bruto.


*10.9 - Analytics and Decision Domain*

Responsável pelo uso das informações produzidas pela plataforma.

Inclui conceitualmente:

* Business Intelligence;
* relatórios operacionais;
* análise exploratória;
* investigação de causas;
* modelos estatísticos;
* ciência de dados;
* aplicações analíticas;
* suporte à decisão.

Esse domínio consome informações disponibilizadas pelo IMS, mas não define a estrutura fundamental da plataforma.

---

### 11. Capacidades Arquiteturais

A arquitetura IMS deve fornecer, de forma integrada, as seguintes capacidades principais.

| Capacidade                  | Finalidade                                              |
| --------------------------- | ------------------------------------------------------- |
| **Aquisição**               | Obter dados das fontes industriais existentes           |
| **Identificação de Origem** | Preservar a relação com o sistema produtor              |
| **Abstração**               | Separar significado lógico de detalhes físicos          |
| **Contextualização**        | Associar dados ao processo, ativo e domínio             |
| **Ingestão**                | Receber e encaminhar dados para a plataforma            |
| **Comunicação**             | Conectar produtores e consumidores de forma desacoplada |
| **Persistência**            | Armazenar dados em diferentes estágios                  |
| **Processamento**           | Limpar, transformar, correlacionar e agregar            |
| **Modelagem**               | Organizar telemetrias, eventos, KPIs e metadados        |
| **Governança**              | Controlar significado, origem, qualidade e uso          |
| **Observabilidade**         | Monitorar a saúde e o desempenho da plataforma          |
| **Disponibilização**        | Entregar informações para diferentes consumidores       |
| **Analytics**               | Apoiar investigação, decisão e ação                     |

---

### 12. Arquitetura Híbrida

O IMS pode operar de forma distribuída entre ambientes industriais locais, ambientes de borda, data centers corporativos e plataformas de nuvem.

Essa organização deve ser determinada por requisitos como:

* latência;
* disponibilidade;
* segurança;
* conectividade;
* volume;
* frequência;
* custo;
* retenção;
* capacidade computacional;
* criticidade operacional;
* soberania dos dados.

A arquitetura híbrida não deve ser entendida apenas como a divisão entre on-premises e cloud.

Ela representa a distribuição consciente de responsabilidades entre diferentes ambientes.

```text
Ambiente Industrial
        │
        ├── Fontes e sistemas de controle
        ├── Aquisição próxima ao processo
        ├── Buffer e processamento local
        └── Continuidade diante de falhas externas
        │
        ▼
Ambiente Corporativo ou Cloud
        │
        ├── Armazenamento escalável
        ├── Processamento analítico
        ├── Governança centralizada
        ├── Integração corporativa
        └── Analytics
```

A indisponibilidade temporária de conectividade externa não deve comprometer o funcionamento dos sistemas de controle.

O processo industrial deve permanecer operacional independentemente da disponibilidade da plataforma analítica.

---

### 13. Fluxos de Dados

A arquitetura deve suportar diferentes padrões de fluxo.

*13.1 - Fluxo Contínuo*

Adequado para telemetrias e eventos que exigem baixa latência.

```text
Fonte
  ↓
Aquisição
  ↓
Ingestão contínua
  ↓
Processamento
  ↓
Disponibilização
```


*13.2 - Fluxo em Lote*

Adequado para consolidações periódicas, históricos, integrações com sistemas legados e processamento analítico.

```text
Fonte ou armazenamento
  ↓
Extração periódica
  ↓
Transformação
  ↓
Carga
  ↓
Consumo
```


*13.3 - Fluxo Orientado a Eventos*

Adequado para acontecimentos relevantes do processo ou da própria plataforma.

```text
Condição identificada
  ↓
Evento
  ↓
Publicação
  ↓
Consumidores interessados
```

*13.4 - Fluxo de Dados Industriais*

Representa a progressão lógica principal da informação.

```text
Dado Técnico
        │
        ▼
Dado Adquirido
        │
        ▼
Dado Contextualizado
        │
        ▼
    Telemetria
        │
        ▼
      Evento
        │
        ▼
       KPI
        │
        ▼
    Investigação
```

Os diferentes padrões podem coexistir na mesma arquitetura.

---

### 14. Desacoplamento Arquitetural

O desacoplamento é necessário para permitir que componentes, tecnologias e consumidores evoluam de maneira independente.

*14.1-  Desacoplamento da Fonte*

Os consumidores não devem acessar diretamente PLCs, blocos de memória ou estruturas internas de sistemas supervisórios.


*14.2 - Desacoplamento do Transporte*

O modelo conceitual da informação não deve depender do mecanismo utilizado para transportá-la.

Uma telemetria continua representando a mesma observação, independentemente de ser transportada por comunicação síncrona, mensageria, arquivo ou integração em lote.


*14.3 - Desacoplamento do Armazenamento*

Consumidores não devem depender desnecessariamente da organização interna das estruturas de persistência.

Interfaces de consumo devem proteger aplicações contra alterações nos modelos físicos.


*14.4 - Desacoplamento do Consumo*

Novos consumidores devem poder utilizar informações existentes sem provocar mudanças nas fontes industriais.

---

### 15. Rastreabilidade Arquitetural

A arquitetura IMS deve permitir a navegação entre as diferentes camadas de significado.

```text
Documento de Engenharia
        │
        ▼
     Domínio
        │
        ▼
    Processo
        │
        ▼
      Ativo
        │
        ▼
Instrumentação
        │
        ▼
   Fonte Técnica
        │
        ▼
    Telemetria
        │
        ▼
      Evento
        │
        ▼
       KPI
        │
        ▼
Aplicação Analítica
```

No sentido inverso, um indicador apresentado ao usuário deve poder ser investigado até as condições operacionais e os dados que contribuíram para seu resultado.

```text
KPI
  ↓
Eventos relacionados
  ↓
Telemetrias utilizadas
  ↓
Ativos envolvidos
  ↓
Processo industrial
  ↓
Fonte física
```

Essa capacidade é fundamental para transformar indicadores em instrumentos de investigação, e não apenas em números de acompanhamento.

---

### 16. Integração com o IPEM

A camada ARCH deriva diretamente dos modelos de engenharia estabelecidos no IPEM.

| Modelo IPEM               | Influência sobre a arquitetura                            |
| ------------------------- | --------------------------------------------------------- |
| **Domain Model**          | Define o contexto industrial de alto nível                |
| **Process Model**         | Organiza os fluxos e transformações do processo           |
| **Asset Model**           | Identifica os elementos responsáveis pela execução        |
| **Instrumentation Model** | Estabelece as origens das informações                     |
| **Telemetry Model**       | Define a representação contextualizada das observações    |
| **Event Model**           | Define acontecimentos relevantes e preserva sua semântica |
| **KPI Model**             | Estrutura indicadores contextualizados para decisão       |

A relação entre Engenharia e Arquitetura pode ser representada como:

```text
Modelos IPEM
        +
Infraestrutura Industrial Existente
        ↓
Arquitetura Lógica IMS
        ↓
Decisões Arquiteturais
        ↓
Implementação Tecnológica
```

O ARCH-01 não redefine os conceitos do IPEM.

Ele estabelece a estrutura capaz de sustentá-los tecnicamente.

---

### 17. Governança das Responsabilidades

Cada domínio arquitetural deve possuir responsabilidades claramente delimitadas.

Uma capacidade não deve assumir responsabilidades que pertencem a outra disciplina ou camada sem justificativa formal.

Exemplos:

* aquisição não deve definir o significado analítico do KPI;
* dashboards não devem corrigir problemas de qualidade na origem;
* sistemas analíticos não devem redefinir prioridades de alarmes;
* estruturas brutas não devem ser utilizadas como contratos permanentes de consumo;
* tecnologias de mensageria não devem determinar o modelo de telemetria;
* modelos físicos de banco não devem substituir o modelo conceitual do processo.

Exceções e decisões que alterem essas responsabilidades devem ser documentadas por meio de Architecture Decision Records.

---

### 18. Restrições Arquiteturais

A arquitetura IMS deve considerar as seguintes restrições:

* a infraestrutura industrial pode não ser modificável;
* os sistemas de controle possuem prioridade operacional;
* a conectividade pode ser intermitente;
* protocolos podem possuir limitações de desempenho;
* fontes podem utilizar estruturas proprietárias;
* timestamps podem apresentar diferenças de origem;
* dados podem possuir diferentes níveis de qualidade;
* mudanças em automação podem ocorrer sem sincronização imediata com a plataforma;
* alguns sistemas podem não disponibilizar histórico;
* ambientes industriais podem possuir restrições de segurança e acesso;
* dados e aplicações podem estar distribuídos entre ambientes locais e cloud.

Essas restrições devem orientar os documentos arquiteturais subsequentes e os ADRs.

---

### 19. Requisitos de Qualidade Arquitetural

A arquitetura IMS deve buscar os seguintes atributos de qualidade.

*19.1 - Disponibilidade*

A plataforma deve manter suas capacidades essenciais compatíveis com os requisitos de cada caso de uso.


*19.2 - Resiliência*

Falhas em componentes de dados não devem comprometer o controle do processo industrial.

Quando aplicável, a plataforma deve ser capaz de recuperar e reprocessar informações.


*19.3 - Escalabilidade*

A arquitetura deve permitir aumento de volume, frequência, número de ativos e consumidores sem exigir reconstrução completa.


*19.4 - Interoperabilidade*

A plataforma deve integrar fontes e consumidores heterogêneos por meio de interfaces e contratos bem definidos.


*19.5 - Manutenibilidade*

Componentes e modelos devem poder evoluir de forma controlada e desacoplada.


*19.6 - Observabilidade*

O estado dos pipelines, integrações, processamentos e serviços deve ser verificável.


*19.7 - Segurança*

A arquitetura deve aplicar controle de acesso, segmentação, auditoria e proteção adequada ao contexto industrial.


*19.8 - Qualidade dos Dados*

A plataforma deve identificar e tornar visíveis problemas de completude, validade, consistência, atualidade e unicidade.


*19.9 - Rastreabilidade*

As transformações e origens devem permanecer identificáveis durante todo o ciclo de vida dos dados.


*19.10 - Portabilidade*

Sempre que tecnicamente e economicamente apropriado, as capacidades lógicas devem reduzir dependências desnecessárias de um único produto ou fornecedor.

---

### 20. Limites do ARCH-01

O ARCH-01 estabelece:

* a visão geral da arquitetura;
* seus princípios;
* seus domínios;
* suas capacidades;
* os fluxos principais;
* as fronteiras entre disciplinas;
* os direcionadores de decisão;
* os requisitos gerais de qualidade.

---

### 21. Relação com os Próximos Documentos

| Documento                                 | Responsabilidade                                                             |
| ----------------------------------------- | ---------------------------------------------------------------------------- |
| **ARCH-02 — Data Architecture**           | Definir como os dados são organizados e transformados ao longo da plataforma |
| **ARCH-03 — Integration Architecture**    | Definir como fontes, componentes e consumidores se comunicam                 |
| **ARCH-04 — Infrastructure Architecture** | Definir a distribuição computacional e os ambientes de execução              |
| **ARCH-05 — Security Architecture**       | Definir controles de segurança, identidade, acesso e proteção                |
| **ARCH-06 — Analytics Architecture**      | Definir como informações são disponibilizadas para análise e decisão         |
| **ADR**                                   | Registrar e justificar decisões tecnológicas e arquiteturais específicas     |
| **Data Model — DM**                       | Especificar os modelos conceituais, lógicos e físicos dos dados              |
| **Implementation**                        | Materializar a arquitetura por meio de tecnologias e código                  |

---

### 22. Considerações Finais

O ARCH-01 estabelece a arquitetura IMS como uma camada lógica construída sobre uma realidade industrial existente.

Seu propósito não é redesenhar a automação, substituir sistemas de controle ou redefinir o conhecimento operacional da planta.

A arquitetura deve receber os dados disponibilizados por essa infraestrutura, abstrair suas particularidades técnicas, preservar sua origem e organizá-los segundo o contexto estabelecido nos modelos IPEM.

Essa abordagem permite que informações originadas em estruturas específicas de controladores, redes e sistemas industriais sejam transformadas em representações estáveis orientadas ao processo, aos ativos, às telemetrias, aos eventos e aos indicadores.

O IMS passa, assim, a atuar como uma ponte entre duas realidades:

```text
Realidade Física e Operacional
        │
        ▼
Arquitetura Lógica IMS
        │
        ▼
Realidade Informacional e Analítica
```

A arquitetura não elimina a complexidade industrial, ela a encapsula, organiza e torna utilizável.

Ao adotar os princípios **Logical Abstraction Over Existing Infrastructure**, **Brownfield by Design**, **Non-Intrusive Integration**, **Source Decoupling**, **Traceability by Design**, **Engineering Knowledge Preservation** e **Context Before KPI**, o IMS estabelece uma base coerente para a digitalização de ambientes industriais reais.

Essa base permitirá que as tecnologias selecionadas nas etapas posteriores sejam tratadas como meios de implementação de uma arquitetura previamente fundamentada, e não como elementos responsáveis por definir sua estrutura ou seu propósito.

Dessa forma, o ARCH-01 inaugura a camada arquitetural do Industrial Mill Streaming preservando a continuidade conceitual construída durante o IPEM:

```text
    Engenharia
        │
        ▼
   Arquitetura
        │
        ▼
     Decisões
        │
        ▼
   Implementação
        │
        ▼
    Informação
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
