### 1. Introdução

A crescente digitalização dos processos industriais tem ampliado significativamente a necessidade de integrar ambientes de Tecnologia Operacional (Operational Technology – OT) e Tecnologia da Informação (Information Technology – IT). Sensores, controladores programáveis, sistemas supervisórios e demais dispositivos de automação passaram a gerar grandes volumes de dados que, quando devidamente estruturados, tornam-se ativos estratégicos para monitoramento operacional, análise de desempenho e suporte à tomada de decisão.

Nesse contexto, o Industrial Mill Streaming (IMS) foi concebido como um projeto open source de Engenharia de Dados Industrial, cujo objetivo é demonstrar como dados provenientes de um processo industrial podem ser adquiridos, transmitidos, processados, armazenados e disponibilizados por meio de uma arquitetura moderna, orientada a eventos e baseada em tecnologias abertas.

Como domínio de referência, o projeto utiliza a Área de Extração de uma usina sucroenergética, modelando equipamentos, instrumentação, telemetria, eventos operacionais e indicadores de desempenho inspirados em um ambiente industrial real.

Mais do que apresentar um conjunto de tecnologias, o IMS busca demonstrar uma forma estruturada de projetar soluções de Engenharia de Dados Industrial, colocando o domínio do processo como elemento central da arquitetura.

---

### 2. Visão

O Industrial Mill Streaming tem como visão tornar-se um projeto de referência para estudos, pesquisas e demonstrações de Engenharia de Dados Industrial, evidenciando como ativos industriais, eventos operacionais e dados de processo podem ser representados por meio de modelos bem definidos, arquitetura desacoplada e boas práticas de engenharia de software.

O conhecimento, os padrões arquiteturais e os componentes desenvolvidos ao longo da evolução do IMS servirão como base para a futura construção da Industrial Data Platform (IDP), iniciativa de maior abrangência destinada à modelagem de diferentes domínios industriais.

---

### 3. Objetivos
#### *Objetivo Geral*

Desenvolver um projeto de referência capaz de representar, de forma realista, o fluxo de dados da Área de Extração de uma usina sucroenergética utilizando princípios de Engenharia de Dados Industrial e Arquitetura Orientada a Eventos.

#### *Objetivos Específicos*
- Modelar um processo industrial baseado em equipamentos e instrumentação reais.
- Demonstrar a integração entre ambientes OT e IT.
- Implementar um pipeline completo de aquisição, processamento e disponibilização de dados industriais.
- Aplicar conceitos de Event-Driven Architecture (EDA).
- Demonstrar boas práticas de Engenharia de Dados Industrial.
- Produzir uma documentação técnica estruturada que sirva como referência para estudantes e profissionais.
- Estabelecer os fundamentos arquiteturais para evolução futura da Industrial Data Platform (IDP).

---

### 4. Escopo

A primeira versão do IMS contempla exclusivamente a modelagem da Área de Extração de uma usina sucroenergética.

O projeto abrangerá:

- modelagem da planta industrial;
- modelagem dos ativos industriais;
- modelagem da instrumentação;
- aquisição de telemetria;
- processamento de eventos;
- arquitetura de streaming de dados;
- persistência em banco de dados;
- disponibilização de APIs;
- geração de indicadores operacionais;
- visualização de dados por dashboards.

---

### 🎯 5. Público-Alvo

O Industrial Mill Streaming foi desenvolvido para profissionais e estudantes interessados na integração entre Automação Industrial e Engenharia de Dados.

O projeto destina-se principalmente a:

- Engenheiros de Dados;
- Engenheiros de Automação;
- Engenheiros de Controle;
- Engenheiros de Processos;
- Arquitetos de Soluções;
- Profissionais envolvidos com iniciativas de Indústria 4.0.

---

### 🧩 6. Organização da Especificação

O Industrial Process & Event Model (IPEM) constitui a especificação técnica oficial do Industrial Mill Streaming.

A especificação está organizada em capítulos independentes, cada um responsável por descrever um aspecto específico do domínio industrial ou da arquitetura da solução.

Cada capítulo responde a uma única pergunta de engenharia, permitindo que a evolução da documentação ocorra de forma incremental, organizada e rastreável.

Documento	*->* Pergunta respondida:
- IPEM-01 ->	Por que o projeto existe?
- IPEM-02	-> Qual contexto industrial está sendo modelado?
- IPEM-03	-> Como a planta está organizada?
- IPEM-04	-> Como o processo industrial funciona?
- IPEM-05	-> Quais ativos compõem o domínio?
- IPEM-06	-> Como esses ativos são instrumentados?
- IPEM-07	-> Quais dados são produzidos?
- IPEM-08	-> Como os dados tornam-se eventos?
- IPEM-09	-> Como os eventos geram informação para o negócio?

---

### 🧠 7. Filosofia do Projeto

O desenvolvimento do Industrial Mill Streaming fundamenta-se em princípios que priorizam o entendimento do domínio industrial antes da implementação tecnológica.

Esses princípios orientam todas as decisões arquiteturais do projeto.

 **Domain First**
 
O domínio industrial orienta a arquitetura, e não o contrário.

**Event First**

Eventos representam o principal mecanismo de integração entre os componentes da solução.

**Asset Centric**

Todo dado produzido pela plataforma está associado a um ativo industrial claramente identificado.

**Documentation as Code**

A documentação evolui juntamente com a implementação, garantindo rastreabilidade entre especificação e código.

**Open Technologies**

A solução utiliza tecnologias abertas, amplamente adotadas pela comunidade e alinhadas às práticas modernas de Engenharia de Dados.

---

### 🧱 8. Evolução da Arquitetura

O Industrial Mill Streaming representa a primeira implementação prática da visão arquitetural que dará origem à Industrial Data Platform (IDP).

Durante sua evolução, os modelos de domínio, padrões arquiteturais, contratos de eventos e componentes reutilizáveis desenvolvidos neste projeto poderão ser incorporados à IDP, preservando continuidade técnica e reduzindo retrabalho.

Dessa forma, o IMS não deve ser entendido como uma plataforma isolada, mas como um projeto de referência que estabelece as bases conceituais e arquiteturais para uma plataforma industrial mais abrangente.

---

###  🏁 Considerações Finais

O Industrial Mill Streaming não tem como objetivo reproduzir integralmente uma planta industrial específica nem competir com soluções comerciais existentes.

Seu propósito é demonstrar, de maneira estruturada e tecnicamente consistente, como princípios de Engenharia de Dados Industrial podem ser aplicados à integração entre OT e IT, utilizando um domínio industrial realista, arquitetura orientada a eventos e documentação tratada como um ativo de engenharia.

Ao evoluir incrementalmente, o projeto consolidará conhecimentos, padrões e componentes que servirão de fundamento para a futura Industrial Data Platform.
