# Industrial Mill Streaming (IMS)

> **Industrial Data Engineering for Smart Manufacturing**

O **Industrial Mill Streaming (IMS)** é um projeto de referência em Engenharia de Dados Industrial que demonstra como construir uma arquitetura de dados industriais moderna utilizando tecnologias abertas, reduzindo a dependência de plataformas proprietárias e oferecendo uma alternativa flexível, escalável e economicamente sustentável para projetos de integração OT/IT.

Utilizando como domínio de referência a **Área de Extração** de uma usina sucroenergética, o projeto apresenta uma implementação completa do fluxo de dados industriais desde a aquisição em campo até sua disponibilização para aplicações analíticas.

O objetivo não é apenas demonstrar tecnologias, mas apresentar uma abordagem estruturada para modelar processos industriais, organizar eventos de negócio e construir soluções escaláveis para a Indústria 4.0.

![Arquitetura geral](https://github.com/CFNascimento86/Industrial-Mill-Streaming/blob/main/images/digital%20twin.jpg)
---

## Sobre o Projeto

A transformação digital da indústria tem ampliado a necessidade de integrar, de forma eficiente, os ambientes de **Tecnologia Operacional (OT)** e **Tecnologia da Informação (IT)**. Embora existam soluções consolidadas para esse desafio, muitas delas estão associadas a ecossistemas proprietários, que podem limitar a flexibilidade arquitetural, a personalização da solução e a independência tecnológica.

O **Industrial Mill Streaming (IMS)** nasceu para demonstrar uma abordagem complementar: projetar uma arquitetura moderna de dados industriais utilizando **tecnologias abertas**, amplamente adotadas pela comunidade, sem abrir mão de robustez, escalabilidade e boas práticas de engenharia.

Mais do que integrar tecnologias, o IMS parte de um princípio fundamental: **a arquitetura deve ser construída a partir do domínio industrial**. Por isso, todo o projeto é desenvolvido com base na modelagem de um processo produtivo real, permitindo que ativos, instrumentação, telemetria, eventos e indicadores sejam representados de forma consistente antes mesmo da implementação.

O resultado é um projeto de referência em Engenharia de Dados Industrial que demonstra como soluções abertas podem apoiar iniciativas de integração OT/IT, servir como base para estudos, prototipação e desenvolvimento de arquiteturas personalizadas, mantendo o foco na engenharia do domínio e não na dependência de um fornecedor específico.

## Arquitetura em Alto Nível

O Industrial Mill Streaming organiza o fluxo de dados industriais em etapas bem definidas, desde a aquisição das informações em campo até sua disponibilização para aplicações analíticas e suporte à tomada de decisão.

```text
Processo Industrial
        │
        ▼
Aquisição de Dados
        │
        ▼
Streaming de Eventos
        │
        ▼
Persistência
        │
        ▼
Disponibilização
        │
        ▼
Consumo dos Dados
```

Cada etapa representa uma responsabilidade arquitetural específica e permanece desacoplada das tecnologias utilizadas em sua implementação.

Essa abordagem permite que a solução evolua ao longo do tempo sem comprometer seus princípios de engenharia.

Os componentes, tecnologias e decisões arquiteturais que materializam esse fluxo encontram-se documentados na seção **Architecture** do projeto.

## Diferenciais

O Industrial Mill Streaming foi concebido para demonstrar que projetos de Engenharia de Dados Industrial podem ser desenvolvidos com foco no domínio do processo, utilizando arquiteturas modernas e tecnologias abertas.

Seus principais diferenciais incluem:

### Modelagem orientada ao domínio industrial

O projeto é estruturado a partir de um processo produtivo real. Ativos, instrumentação, telemetria, eventos e indicadores são modelados antes da implementação da solução.

### Arquitetura orientada a eventos

A integração entre os componentes é baseada em eventos, favorecendo desacoplamento, escalabilidade e evolução contínua da arquitetura.

### Arquitetura baseada em tecnologias abertas

O IMS demonstra como arquiteturas modernas de integração OT/IT podem ser construídas utilizando tecnologias abertas, reduzindo a dependência de ecossistemas proprietários e ampliando a flexibilidade para desenvolvimento de soluções personalizadas.

### Engenharia antes da implementação

Toda a solução é especificada antes do desenvolvimento por meio do **Industrial Process & Event Model (IPEM)** e dos documentos de arquitetura, promovendo rastreabilidade entre requisitos, decisões técnicas e código.

### Projeto com abordagem profissional

O IMS não busca apenas demonstrar tecnologias. Seu propósito é demonstrar como projetar arquiteturas de dados industriais consistentes, sustentáveis e orientadas ao domínio, utilizando tecnologias abertas e boas práticas de engenharia.

---

**Explore a documentação para conhecer a modelagem do domínio, a arquitetura da solução e as decisões de engenharia que sustentam o projeto.**
````
├── README.md     
│
├── docs/
│   │
│   ├── specifications/
│   │      └── IPEM/
│   │          ├── IPEM-01-Introduction.md
|   │          ├── IPEM-02-Business-Context.md
|   │          ├── IPEM-03-Plant-Model.md
|   │          ├── IPEM-04-Process-Model.md
|   │          ├── IPEM-05-Asset-Model.md
|   │          ├── IPEM-06-Instrumentation-Model.md
|   │          ├── IPEM-07-Telemetry-Model.md
|   │          ├── IPEM-08-Event-Model.md
|   │          └── IPEM-09-KPI-Model.md    
|   |
│   ├── architecture/
│   │
│   ├── adr/
│   │
|   ├── data-model/
│   │
|   ├── api/
|   |
│   └── guides/
│   
├── src/
│
├── docker/
│
├── simulator/
│
└── ...
````
