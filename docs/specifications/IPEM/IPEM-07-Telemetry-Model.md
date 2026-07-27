### 1. Introdução

O Telemetry Model estabelece a forma como as informações provenientes da instrumentação industrial passam a ser representadas digitalmente dentro da arquitetura do Industrial Mill Streaming (IMS).

No contexto do IMS, telemetria não representa protocolos de comunicação, tecnologias de transporte ou mecanismos de armazenamento. Seu objetivo é definir uma representação lógica, consistente e contextualizada das informações produzidas pela planta industrial.

Este modelo constitui a primeira camada efetivamente pertencente à Engenharia de Dados Industrial, transformando observações do processo em entidades digitais preparadas para processamento analítico, geração de eventos e cálculo de indicadores.

---

### 2. Escopo

O Telemetry Model é responsável por:

- definir a representação lógica das informações industriais;
- estabelecer a estrutura das observações digitais;
- padronizar atributos fundamentais das telemetrias;
- preservar o contexto operacional das informações;
- preparar os dados para consumo pelos modelos subsequentes.

Não fazem parte do escopo deste documento:

- protocolos industriais (OPC-UA, Modbus, S7 Protocol, MQTT etc.);
- mecanismos de mensageria (Kafka, RabbitMQ etc.);
- bancos de dados;
- Data Lakes;
- APIs;
- pipelines de ingestão;
- tecnologias de armazenamento.

Esses elementos serão especificados na documentação de Arquitetura e nas Architecture Decision Records (ADR), preservando a independência entre Engenharia e Implementação.

---

### 3. Conceito de Telemetria

No IMS, uma telemetria representa uma observação digital de um comportamento do processo industrial em um determinado instante.

Cada registro de telemetria constitui uma evidência contextualizada do estado operacional de um ativo, preservando sua origem, significado e momento de ocorrência.

Dessa forma, a telemetria deixa de ser apenas um valor numérico e passa a representar uma unidade semântica da arquitetura de dados.

---

### 4. Estrutura Conceitual da Telemetria

Toda telemetria deve possuir um conjunto mínimo de atributos capazes de preservar seu significado dentro da arquitetura.

| Elemento  | Descrição                              |
| --------- | -------------------------------------- |
| Origem    | Ativo responsável pela informação      |
| Processo  | Etapa operacional associada            |
| Variável  | Informação observada                   |
| Valor     | Valor observado                        |
| Unidade   | Unidade de engenharia                  |
| Timestamp | Instante da observação                 |
| Qualidade | Estado de confiabilidade da informação |

Esses elementos permitem que qualquer observação seja compreendida independentemente da tecnologia utilizada para sua aquisição.

---

### 5. Relação entre Instrumentação e Telemetria

A instrumentação disponibiliza informações que são convertidas em entidades digitais pela arquitetura do IMS.

| Instrumentação | Informação Disponibilizada | Telemetria Representada |
| -------------- | -------------------------- | ----------------------- |
| RTD            | Temperatura                | Temperatura do Motor    |
| PT             | Pressão                    | Pressão Hidráulica      |
| Encoder        | Velocidade Angular         | Rotação dos Rolos       |
| Acelerômetro   | Vibração                   | Vibração dos Mancais    |
| TC             | Corrente Elétrica          | Corrente do Motor       |

Nesse modelo, a instrumentação deixa de ser o elemento central. O protagonismo passa a ser da informação representada.

---

### 6. Organização das Telemetrias

Para facilitar sua utilização pelos modelos analíticos, as telemetrias são organizadas segundo sua natureza.

| Categoria   | Exemplos                                  |
| ----------- | ----------------------------------------- |
| Processo    | Pressão, Vazão, Temperatura, Nível        |
| Mecânica    | Torque, Vibração, Rotação                 |
| Elétrica    | Corrente, Tensão, Potência                |
| Operacional | Estado, Disponibilidade, Modo de Operação |

Essa organização estabelece uma taxonomia consistente para toda a arquitetura de dados.

---

### 7. Papel da Telemetria na Arquitetura IMS

A telemetria constitui a camada responsável por representar digitalmente o comportamento operacional da planta.
````
Processo Industrial
        │
        ▼
Ativos Industriais
        │
        ▼
Instrumentação Existente
        │
        ▼
   Telemetria
        │
        ▼
     Eventos
        │
        ▼
       KPIs
````
A partir desse ponto, o IMS deixa de operar sobre elementos físicos e passa a operar exclusivamente sobre dados contextualizados.

---

### 8. Telemetria como Fundamento dos Eventos

Os eventos industriais não são produzidos diretamente pela instrumentação.
Eles resultam da interpretação das telemetrias.

| Telemetria           | Condição         | Evento              |
| -------------------- | ---------------- | ------------------- |
| Temperatura do Motor | > 90 °C          | Alta Temperatura    |
| Vibração do Mancal   | Acima do limite  | Vibração Excessiva  |
| Pressão Hidráulica   | Abaixo do mínimo | Baixa Pressão       |
| Corrente do Motor    | Sobrecorrente    | Sobrecarga Elétrica |

Essa separação preserva uma distinção importante:
- Telemetria descreve o comportamento observado.
- Evento interpreta esse comportamento segundo regras de negócio ou operacionais.

---

### 9. Considerações Finais

O Telemetry Model representa o ponto em que o processo industrial passa a existir como uma estrutura organizada de dados.

Ao estabelecer uma representação lógica independente de protocolos, plataformas e tecnologias específicas, o IMS garante que sua arquitetura permaneça estável diante da evolução tecnológica.

Essa abordagem reforça o princípio de que a Engenharia de Dados Industrial deve ser orientada pela informação e pelo contexto operacional, e não pelas ferramentas utilizadas para transportá-la ou armazená-la.

---

### 10. Relação com os Próximos Capítulos

O Telemetry Model fornece a base para todos os modelos analíticos da arquitetura IMS.

| Capítulo                  | Derivação do Telemetry Model                                                                       |
| ------------------------- | -------------------------------------------------------------------------------------------------- |
| **IPEM-08 – Event Model** | Interpreta alterações relevantes nas telemetrias e identifica eventos operacionais e de negócio.   |
| **IPEM-09 – KPI Model**   | Consolida telemetrias em indicadores que suportam análise operacional, gestão e tomada de decisão. |
