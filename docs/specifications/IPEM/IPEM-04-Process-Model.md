### 1. Introdução

Este capítulo descreve o comportamento operacional do domínio de referência adotado pelo Industrial Mill Streaming (IMS).

Enquanto os capítulos anteriores definiram o contexto e a organização do domínio, o Process Model estabelece como ocorre a transformação física que origina os dados utilizados pela arquitetura.

Neste documento, o processo industrial passa a ser considerado a principal referência para a modelagem dos ativos, da instrumentação, da telemetria, dos eventos e dos indicadores de desempenho especificados nos capítulos seguintes.

---

### 2. Objetivo do Processo

A operação de moagem tem como finalidade promover a extração do caldo da cana-de-açúcar por meio da compressão controlada da matéria-prima entre conjuntos de rolos, produzindo caldo e bagaço como principais produtos do processo.

Sob a perspectiva do IMS, essa transformação representa não apenas uma operação física, mas também a origem dos dados que descrevem o comportamento operacional da Moenda.

---

### 3. Princípio de Modelagem

O IMS adota o princípio Process First Modeling, segundo o qual toda a arquitetura de dados deve ser derivada do comportamento do processo industrial.

*Consequentemente:*

- os ativos existem para executar etapas do processo;
- a instrumentação existe para observar o processo;
- a telemetria representa o estado do processo;
- os eventos descrevem alterações no processo;
- os indicadores avaliam o desempenho do processo.

Essa abordagem assegura que toda a modelagem permaneça alinhada ao comportamento operacional real do domínio.

----

### 4. Fluxo Conceitual do Processo

O comportamento operacional da Moenda pode ser representado pelo seguinte fluxo conceitual:
````
Recepção da Matéria-Prima
            │
            ▼
Alimentação da Moenda
            │
            ▼
Compressão da Cana
            │
            ▼
Extração do Caldo
            │
            ▼
Separação Física
      ┌──────────────┐
      ▼              ▼
   Caldo         Bagaço
````
Este fluxo representa exclusivamente a transformação física realizada pela Moenda, sem considerar ainda equipamentos específicos ou tecnologias de automação.

---

### 5. Entradas e Saídas do Processo

O processo recebe como principais *entradas*:

- cana-de-açúcar;
- água de embebição;
- energia mecânica;
- energia elétrica.
  
Como resultado *(saídas)* da operação são produzidos:

- caldo;
- bagaço;
- informações operacionais.

A inclusão das informações operacionais como saída do processo reflete a visão do IMS de que os dados industriais constituem um produto inerente à operação e não um subproduto da automação.

---

### 6. Estados Operacionais

Durante seu ciclo de vida operacional, a Moenda pode assumir diferentes estados.

Os principais estados considerados pelo IMS são:
````
Parada

↓

Partida

↓

Operação Normal

↓

Operação com Restrição

↓

Sobrecarga

↓

Parada Programada

↓

Parada de Emergência
````
Esses estados servirão como base para a modelagem dos eventos operacionais descritos no Event Model.

---

### 7. Variáveis de Processo

A operação da Moenda é caracterizada por grandezas físicas que descrevem continuamente seu comportamento.

Entre as principais variáveis de engenharia destacam-se:

- taxa de alimentação;
- pressão hidráulica;
- velocidade dos rolos;
- torque;
- corrente elétrica;
- potência;
- temperatura dos mancais;
- vibração;
- consumo de água de embebição.

Neste estágio da especificação, essas variáveis são apresentadas apenas como grandezas de processo.

A associação com sensores, instrumentos e controladores será realizada posteriormente no Instrumentation Model e no Telemetry Model.

---

### 8. Transformação Física × Transformação Digital

A operação da Moenda produz simultaneamente dois resultados complementares.

O primeiro corresponde à transformação física da matéria-prima.

O segundo corresponde à geração contínua de informações capazes de representar digitalmente o comportamento do processo.

Essa relação pode ser representada da seguinte forma:
````
Processo Industrial

        │

        ├──────────────► Transformação Física
        │                     │
        │                     ├── Caldo
        │                     └── Bagaço
        │
        └──────────────► Transformação Digital
                              │
                              ├── Telemetria
                              ├── Eventos
                              ├── KPIs
                              └── Informações para Gestão
````
Essa representação sintetiza a proposta central do IMS, onde toda transformação física relevante do processo industrial deve possuir uma representação digital coerente, rastreável e capaz de apoiar decisões operacionais e gerenciais.

---

### 9. Considerações Finais

O Process Model estabelece a referência conceitual para toda a modelagem subsequente do IMS.

Ao adotar o processo industrial como fonte primária da arquitetura, a especificação assegura que todos os modelos derivados preservem coerência com a operação real da Moenda, fortalecendo a integração entre Engenharia de Processos e Engenharia de Dados Industrial.

---

### 10. Relação com os Próximos Capítulos

O comportamento operacional descrito neste documento fundamenta diretamente os modelos subsequentes:

Capítulo - Derivação do Processo

IPEM-05 – Asset Model	Identifica os ativos responsáveis por executar cada etapa do processo.

IPEM-06 – Instrumentation Model	Define como cada etapa do processo será observada.

IPEM-07 – Telemetry Model	Representa as variáveis produzidas pelo processo.

IPEM-08 – Event Model	Modela os acontecimentos relevantes durante a execução do processo.

IPEM-09 – KPI Model	Define como o desempenho do processo será medido.
