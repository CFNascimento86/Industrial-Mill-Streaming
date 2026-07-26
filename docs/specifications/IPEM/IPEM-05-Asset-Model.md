### 1. Introdução

Este capítulo identifica e organiza os ativos industriais responsáveis pela execução do processo operacional descrito no IPEM-04 – Process Model.

No contexto do Industrial Mill Streaming (IMS), um ativo industrial não é tratado apenas como um equipamento físico pertencente à planta, mas como um elemento funcional indispensável para a realização das transformações que caracterizam o processo de moagem.

A modelagem apresentada estabelece a relação entre processo e ativos, servindo como base para a especificação da instrumentação, da telemetria e dos eventos industriais nos capítulos subsequentes.

---

### 2. Princípio de Modelagem

O IMS adota o princípio Function Before Asset, segundo o qual a identificação dos ativos industriais deve ser consequência direta das funções necessárias para executar o processo.

Assim, cada ativo existe para cumprir uma responsabilidade operacional claramente definida.

Essa abordagem evita que o modelo seja reduzido a um inventário de equipamentos, garantindo que a estrutura permaneça alinhada ao comportamento real do processo industrial.

---

### 3. Relação entre Processo e Ativos

A identificação dos ativos inicia-se pela análise das funções descritas no Process Model. Todo ativo identificado na modelagem deve possuir potencial de observação, permitindo que seu comportamento seja representado por meio de instrumentação, telemetria, eventos e indicadores.

Cada etapa do processo demanda capacidades físicas específicas, materializadas pelos ativos industriais correspondentes.

| Etapa do Processo       | Função                      | Ativo Principal    |
| ----------------------- | --------------------------- | ------------------ |
| Alimentação             | Conduzir a matéria-prima    | Mesa Alimentadora  |
| Compressão              | Extrair o caldo             | Conjunto de Rolos  |
| Transmissão de Potência | Transferir torque           | Redutor            |
| Acionamento             | Fornecer potência mecânica  | Motor Elétrico     |
| Sustentação             | Absorver esforços mecânicos | Mancais            |
| Controle Mecânico       | Regular pressão dos rolos   | Sistema Hidráulico |

Essa relação estabelece a primeira camada de rastreabilidade funcional do IMS.

---

### 4. Organização Hierárquica dos Ativos

Os ativos são organizados segundo sua contribuição para o domínio de referência.
````
Moenda
    │
    ├── Sistema de Alimentação
    │       └── Mesa Alimentadora
    │
    ├── Sistema de Moagem
    │       ├── Rolo Superior
    │       ├── Rolo Alimentador
    │       └── Rolo Descarga
    │
    ├── Sistema de Acionamento
    │       ├── Motor Elétrico
    │       └── Redutor
    │
    ├── Sistema Hidráulico
    │
    └── Estrutura Mecânica
            └── Mancais
````
Essa organização será utilizada como referência para todos os modelos derivados.

---

### 5. Classificação dos Ativos

Para facilitar a evolução da arquitetura, os ativos são agrupados segundo sua natureza funcional.

| Categoria   | Exemplos                           |
| ----------- | ---------------------------------- |
| Mecânicos   | Rolos, Mancais, Acoplamentos       |
| Elétricos   | Motores Elétricos                  |
| Hidráulicos | Cilindros, Bombas, Válvulas        |
| Estruturais | Chassi, Bases, Estruturas de Apoio |

Essa classificação facilita a associação futura entre ativos, instrumentação e variáveis de processo.

---

### 6. Responsabilidade Funcional dos Ativos

Cada ativo desempenha uma função específica dentro do processo operacional.

Sua importância é determinada pela contribuição para a transformação física da matéria-prima.

| Ativo              | Responsabilidade                                             |
| ------------------ | ------------------------------------------------------------ |
| Mesa Alimentadora  | Garantir alimentação uniforme da Moenda                      |
| Rolos              | Realizar a compressão da cana e promover a extração do caldo |
| Motor Elétrico     | Disponibilizar potência mecânica ao processo                 |
| Redutor            | Adequar velocidade e torque aos rolos                        |
| Mancais            | Sustentar os esforços mecânicos dos rolos                    |
| Sistema Hidráulico | Controlar a pressão aplicada durante a moagem                |

Essa modelagem reforça que os ativos são definidos por sua função no processo, e não apenas por sua presença física na planta.

---

### 7. Ativos como Origem da Observabilidade

Embora os ativos executem as transformações físicas do processo, eles também representam os pontos onde o comportamento operacional pode ser observado.

Cada ativo produz evidências que permitem avaliar seu estado operacional por meio de variáveis de engenharia, eventos e indicadores de desempenho.

No IMS, essa capacidade de observação será formalizada nos capítulos de Instrumentation Model, Telemetry Model e Event Model.

Assim, os ativos representam a transição entre a execução física do processo e sua representação digital.

---

### 8. Considerações Finais

O Asset Model estabelece a estrutura funcional dos ativos que compõem o domínio de referência do IMS.

Ao adotar uma abordagem orientada por funções, a especificação garante que todos os elementos físicos da arquitetura possam ser rastreados até as transformações descritas no Process Model.

Essa rastreabilidade constitui um dos principais mecanismos de consistência entre Engenharia de Processos, Engenharia de Ativos e Engenharia de Dados Industrial.

---

### 9. Relação com os Próximos Capítulos

A modelagem dos ativos estabelece a base para os modelos responsáveis por representar sua observação e monitoramento.

Capítulo - Derivação do Asset Model

IPEM-06 – Instrumentation Model -	Define como cada ativo será observado.

IPEM-07 – Telemetry Model -	Representa as variáveis produzidas pelos ativos.

IPEM-08 – Event Model -	Modela os eventos relacionados ao comportamento dos ativos.

IPEM-09 – KPI Model -	Define indicadores derivados do desempenho dos ativos e do processo.
