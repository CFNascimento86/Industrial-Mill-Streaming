### 1. Introdução

O Instrumentation Model estabelece a relação entre os ativos industriais descritos no IPEM-05 – Asset Model e as informações produzidas pela instrumentação existente na planta industrial.

No contexto do Industrial Mill Streaming (IMS), este documento não tem como objetivo especificar sensores, transmissores, malhas de controle ou estratégias de automação. Essas atividades pertencem ao domínio da Engenharia de Controle e Automação.

O propósito do IMS inicia-se a partir da existência dessa infraestrutura, tratando a instrumentação como a origem das informações que permitirão construir uma representação digital consistente do processo industrial.

Assim, este modelo estabelece quais informações provenientes da instrumentação são relevantes para representar o comportamento dos ativos e preparar sua utilização pela arquitetura de dados industrial.

---

### 2. Escopo do Modelo

O Instrumentation Model limita-se à representação lógica da instrumentação existente.

Portanto, estão fora do escopo deste documento:

- especificação de sensores;
- dimensionamento de instrumentos;
- seleção de tecnologias de medição;
- projeto de malhas de controle;
- arquitetura de automação;
- estratégias de controle PID;
- instalação e calibração de instrumentos.

O IMS assume que essas definições já fazem parte da infraestrutura operacional da planta.

Seu interesse concentra-se exclusivamente nas informações produzidas por essa infraestrutura.

---

### 3. Objetivo da Instrumentação no IMS

Sob a perspectiva da Engenharia de Dados Industrial, a instrumentação representa o primeiro ponto de contato entre o processo físico e sua representação digital.

Cada instrumento disponibiliza informações que permitem observar aspectos específicos do comportamento dos ativos industriais.

Essas informações constituem a matéria-prima para os modelos de telemetria, eventos e indicadores definidos nos capítulos posteriores.

---

### 4. Relação entre Ativos e Instrumentação

Cada ativo pode ser observado por diferentes instrumentos, dependendo dos comportamentos relevantes para o processo operacional.

Essa associação estabelece a origem das futuras variáveis industriais.

| Ativo              | Comportamento Observado | Instrumentação Existente       |
| ------------------ | ----------------------- | ------------------------------ |
| Motor Elétrico     | Temperatura             | RTD                            |
| Motor Elétrico     | Corrente elétrica       | Transformador de Corrente (TC) |
| Motor Elétrico     | Velocidade de rotação   | Encoder                        |
| Mancais            | Vibração                | Acelerômetro                   |
| Sistema Hidráulico | Pressão hidráulica      | Transmissor de Pressão (PT)    |
| Mesa Alimentadora  | Velocidade              | Encoder                        |
| Rolos              | Rotação                 | Sensor de Velocidade           |

Observe que o foco do modelo não está no instrumento em si, mas na informação que ele torna disponível.

---

### 5. Organização da Instrumentação

A instrumentação pode ser organizada segundo a natureza das informações disponibilizadas.

| Categoria   | Exemplos de Instrumentação | Informação Produzida |
| ----------- | -------------------------- | -------------------- |
| Temperatura | RTD, Termopar              | Temperatura          |
| Pressão     | PT                         | Pressão              |
| Vazão       | FT                         | Vazão                |
| Nível       | LT                         | Nível                |
| Rotação     | Encoder                    | Velocidade Angular   |
| Vibração    | Acelerômetro               | Vibração             |
| Corrente    | TC                         | Corrente Elétrica    |

Essa organização facilita a padronização da representação digital adotada pelo IMS.

---

### 6. Instrumentação como Fonte de Informação

No IMS, a instrumentação é compreendida como a infraestrutura responsável por disponibilizar informações sobre o comportamento operacional dos ativos.

Sua função não é apenas medir grandezas físicas, mas fornecer evidências que permitam representar digitalmente o estado do processo industrial.

Sob essa perspectiva, cada instrumento constitui uma fonte primária de informação para a arquitetura de dados.

Essa abordagem desloca o foco do dispositivo físico para a informação produzida, alinhando o Instrumentation Model aos objetivos da Engenharia de Dados Industrial.

---

### 7. Papel do Instrumentation Model na Arquitetura IMS

Dentro da arquitetura do IMS, este modelo estabelece a transição entre o mundo operacional e a arquitetura de dados.
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
Informações Disponibilizadas
        │
        ▼
Telemetry Model
````
Essa estrutura evidencia que a instrumentação não constitui o objetivo final do IMS, mas a origem das informações necessárias para a construção dos modelos digitais subsequentes.

---

### 8. Limites Arquiteturais

Para preservar a consistência da especificação, o Instrumentation Model adota os seguintes limites:

É responsabilidade deste documento:

- identificar a instrumentação relevante ao domínio;
- relacionar ativos e informações produzidas;
- estabelecer a origem das futuras variáveis industriais;
- preparar a modelagem da telemetria.

Não é responsabilidade deste documento:

- definir sensores;
- justificar tecnologias de medição;
- especificar protocolos industriais;
- modelar PLCs;
- definir sistemas supervisórios;
- estabelecer estratégias de controle.

Esses elementos pertencem às disciplinas responsáveis pela automação industrial.

---

### 9. Considerações Finais

O Instrumentation Model estabelece a primeira camada de representação digital do processo industrial.

Ao reconhecer a instrumentação como fonte das informações que descrevem o comportamento dos ativos, o IMS cria uma base consistente para a construção da arquitetura de dados industrial.

Essa abordagem preserva a independência entre Engenharia de Controle e Engenharia de Dados, permitindo que cada disciplina atue dentro de seu respectivo domínio de competência.

---

### 10. Relação com os Próximos Capítulos

O Instrumentation Model fornece a base necessária para a definição das estruturas responsáveis pelo tratamento dos dados industriais.

| Capítulo                      | Relação com o IPEM-06                                                                       |
| ----------------------------- | ------------------------------------------------------------------------------------------- |
| **IPEM-07 – Telemetry Model** | Estrutura as informações produzidas pela instrumentação em variáveis digitais padronizadas. |
| **IPEM-08 – Event Model**     | Identifica alterações relevantes observadas nas informações provenientes da instrumentação. |
| **IPEM-09 – KPI Model**       | Consolida informações da telemetria em indicadores operacionais e gerenciais.               |
