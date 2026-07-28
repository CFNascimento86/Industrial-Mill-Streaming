### 1. Introdução

O Event Model estabelece a representação digital dos acontecimentos relevantes observados durante a execução do processo industrial.

No contexto do Industrial Mill Streaming (IMS), um evento não representa apenas uma alteração em uma variável de processo. Ele representa uma mudança de estado cuja relevância já foi estabelecida pela engenharia da planta ou pelas regras de negócio da arquitetura de dados.

Dessa forma, o Event Model transforma observações contínuas provenientes da telemetria em acontecimentos contextualizados, preparados para consumo por aplicações analíticas, indicadores operacionais e sistemas corporativos.

---

### 2. Engineering Question

Como representar digitalmente acontecimentos relevantes do processo industrial preservando seu significado operacional?

Essa pergunta estabelece claramente o propósito deste documento.

---

### 3. Princípio de Modelagem
*Engineering Knowledge Preservation*

O IMS adota o princípio **Engineering Knowledge Preservation**, segundo o qual toda representação de eventos deve preservar a semântica operacional previamente estabelecida pelas disciplinas responsáveis pelo processo industrial.

Consequentemente, o IMS não redefine critérios de alarmes, estratégias de controle, filosofias operacionais ou regras de segurança.

Seu papel consiste em representar digitalmente esse conhecimento de forma consistente, rastreável e reutilizável.

---

### 4. Conceito de Evento

No IMS, um evento representa uma alteração relevante no estado operacional do processo industrial.

Essa alteração pode ter origem em:

- regras operacionais da planta;
- sistemas de controle;
- gestão de alarmes;
- lógica de produção;
- interpretação das telemetrias;
- monitoramento da própria plataforma de dados.

Assim, um evento constitui uma entidade semântica da arquitetura de dados, e não apenas uma notificação técnica.

---

### 5. Origem dos Eventos

Os eventos representados pelo IMS podem possuir diferentes origens.

*5.1 - Eventos Operacionais*

Relacionados à operação normal da planta.

Exemplos:

- Início da Moagem
- Parada Programada
- Início da Batelada
- Final da Batelada
- Mudança de Receita

*5.2 - Eventos derivados da Gestão de Alarmes*

Representam alarmes definidos pela Engenharia de Controle e Automação.

Esses eventos devem preservar integralmente a semântica estabelecida pela filosofia de alarmes da planta.

Exemplos:

- Alta Temperatura
- Baixa Pressão
- Sobrecorrente
- Vibração Excessiva

O IMS não redefine:

- prioridades;
- severidades;
- deadbands;
- shelving;
- tempos de supressão;
- racionalização de alarmes.

Esses elementos permanecem sob responsabilidade da Gestão de Alarmes da planta.

*5.3 - Eventos de Processo*

Relacionados ao comportamento físico do processo.

Exemplos:

- Perda de Alimentação
- Instabilidade de Processo
- Excesso de Carga
- Falha de Extração

*5.4 - Eventos da Plataforma de Dados*

Representam situações próprias da arquitetura IMS.

Exemplos:

- Falha de Comunicação
- Perda de Pacotes
- Timestamp Inválido
- Latência Excessiva
- Falha de Pipeline
- Dados Duplicados
- Lacunas Temporais

Esses eventos pertencem exclusivamente ao domínio da Engenharia de Dados Industrial.

---

### 6. Estrutura Conceitual do Evento

Todo evento deve preservar seu contexto operacional.

| Elemento           | Descrição                                    |
| ------------------ | -------------------------------------------- |
| Origem             | Processo, ativo ou plataforma responsável    |
| Categoria          | Operacional, Processo, Alarme ou Plataforma  |
| Condição de Origem | Situação que originou o evento               |
| Severidade         | Conforme definição da engenharia responsável |
| Timestamp          | Momento da ocorrência                        |
| Contexto           | Processo, ativo e telemetrias associadas     |

Essa estrutura garante rastreabilidade e consistência semântica.

---

### 7. Relação entre Telemetria e Eventos

A telemetria representa observações.

Os eventos representam interpretações dessas observações ou de regras operacionais previamente estabelecidas.
````
    Telemetria
        │
        ▼
Contexto Operacional
        │
        ▼
 Regras Existentes
        │
        ▼
      Evento
````
Essa sequência preserva a separação entre aquisição de dados e interpretação operacional.

---

### 8. Governança dos Eventos

O IMS estabelece que todos os eventos derivados da operação industrial devem manter coerência com os modelos e práticas já existentes na planta.

Sempre que aplicável, devem ser preservados:

- identificação do evento;
- descrição operacional;
- classificação;
- prioridade;
- severidade;
- significado operacional.

Essa diretriz evita conflitos entre os sistemas analíticos e a operação industrial.

---

### 9. Papel do Event Model na Arquitetura IMS

O Event Model representa a camada responsável por transformar informações em acontecimentos relevantes.
````
Processo Industrial
        │
        ▼
      Ativos
        │
        ▼
  Instrumentação
        │
        ▼
    Telemetria
        │
        ▼
   Event Model
        │
        ▼
       KPIs
        │
        ▼
    Analytics
````
Nesse ponto da arquitetura, a informação deixa de representar apenas o estado do processo e passa a representar fatos relevantes para operação, manutenção e gestão.

---

### 10. Limites Arquiteturais

O Event Model é responsável por:

- representar eventos industriais;
- preservar sua semântica operacional;
- integrar acontecimentos relevantes à arquitetura de dados;
- preparar informações para indicadores e análises.

Não é responsabilidade deste documento:

- definir estratégias de controle;
- criar filosofias de alarmes;
- racionalizar alarmes;
- configurar PLCs;
- parametrizar sistemas supervisórios;
- estabelecer permissivos operacionais.

Essas responsabilidades permanecem sob domínio das disciplinas responsáveis pela automação e operação da planta.

---

### 11. Considerações Finais

O Event Model estabelece a camada responsável por representar digitalmente acontecimentos relevantes do processo.

Ao preservar o conhecimento operacional existente e integrá-lo à arquitetura de dados, o IMS garante que análises, indicadores e aplicações digitais utilizem exatamente o mesmo significado adotado pela operação industrial.

Essa abordagem reforça o papel do IMS como uma arquitetura de Engenharia de Dados Industrial comprometida com a consistência entre o mundo físico, o conhecimento operacional e sua representação digital.

---

### 12. Relação com o Próximo Capítulo

| Capítulo                | Derivação do Event Model                                                                         |
| ----------------------- | ------------------------------------------------------------------------------------------------ |
| **IPEM-09 – KPI Model** | Consolida telemetrias e eventos em indicadores de desempenho para operação, manutenção e gestão. |
