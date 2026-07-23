### 1. Introdução

O Industrial Mill Streaming utiliza como domínio de referência a operação de moagem da Área de Extração de uma usina sucroenergética.

A operação de moagem reúne características típicas de sistemas industriais modernos, como elevado nível de instrumentação, aquisição contínua de dados, eventos operacionais, criticidade do processo e integração entre ambientes de Tecnologia Operacional (OT) e Tecnologia da Informação (IT).

Essas características tornam o processo um ambiente adequado para demonstrar conceitos de Engenharia de Dados Industrial por meio de uma arquitetura orientada a eventos e baseada em tecnologias abertas.

 ---
 
### 2. Contexto Industrial

O setor sucroenergético caracteriza-se por processos industriais integrados, nos quais a disponibilidade e a qualidade dos dados operacionais influenciam diretamente a eficiência da produção.

Ao longo da cadeia produtiva, diferentes áreas operacionais geram informações que podem ser utilizadas para monitoramento, rastreabilidade, otimização de processos e suporte à tomada de decisão.

Entre essas áreas, a Extração representa um dos primeiros e mais relevantes pontos de geração de dados industriais, constituindo a base informacional para diversas etapas subsequentes da produção.

---

### 3. Domínio de Referência

O IMS adota como domínio de referência o Sistema de Moagem, responsável pela extração do caldo da cana-de-açúcar. Porque reúne em um único processo, praticamente todos os desafios que uma arquitetura de Engenharia de Dados Industrial precisa enfrentar.

A escolha desse sistema fundamenta-se em critérios técnicos.

*A operação apresenta:*

- aquisição contínua de dados;
- alta densidade de instrumentação;
- integração OT/IT;
- eventos operacionais;
- necessidade de disponibilidade;
- geração de KPIs;
- decisões quase em tempo real.

Sob a perspectiva da Engenharia de Dados Industrial, essas características fazem da moagem um domínio representativo para estudos de aquisição, modelagem e processamento de dados industriais.

---

### 4. Hierarquia do Domínio

O IMS organiza seu domínio industrial segundo a seguinte estrutura conceitual:
````
Setor Sucroenergético
        │
        ▼
Área de Extração
        │
        ▼
Sistema de Moagem
        │
        ▼
      Moenda
        │
        ▼
Ativos Industriais
        │
        ▼
Instrumentação
        │
        ▼
Telemetria
        │
        ▼
     Eventos
````
Essa organização estabelece a relação entre o contexto industrial e os elementos que serão modelados ao longo da especificação, servindo como referência para todos os capítulos subsequentes do IPEM.

---

### 5. Geração de Dados Industriais

Durante sua operação, o Sistema de Moagem produz continuamente informações provenientes de sensores, instrumentos de campo, controladores programáveis e sistemas supervisórios.

Esses dados representam o estado operacional do processo e constituem a principal fonte de informação utilizada pela arquitetura do IMS.

*Entre as principais categorias de informação destacam-se:*

- variáveis de processo;
- estados operacionais;
- alarmes;
- eventos;
- indicadores de desempenho;
- informações de rastreabilidade.

Esses elementos serão detalhados nos capítulos específicos de Telemetry Model, Event Model e KPI Model.

---

### 6. Delimitação do Escopo

Para manter consistência arquitetural e foco na modelagem do domínio, o Industrial Mill Streaming limita seu escopo ao Sistema de Moagem da Área de Extração.

*Não fazem parte desta especificação:*

- tratamento de caldo;
- evaporação;
- cozimento;
- centrifugação;
- fermentação;
- destilação;
- cogeração;
- demais processos industriais da planta.

Essa delimitação permite aprofundar a modelagem do domínio escolhido sem ampliar desnecessariamente a complexidade da solução.

---

### 7. Considerações Finais

O Sistema de Moagem representa um domínio industrial suficientemente rico para demonstrar conceitos fundamentais de Engenharia de Dados Industrial, incluindo aquisição de dados, integração OT/IT, processamento de eventos e disponibilização de informações para aplicações analíticas.

Ao concentrar a especificação nesse domínio, o IMS estabelece uma base consistente para evolução incremental da arquitetura, preservando a possibilidade de expansão futura para outros processos industriais.

---

### 8. Relação com os Próximos Capítulos

O contexto apresentado neste capítulo fundamenta os documentos subsequentes da especificação.

*Nos próximos capítulos serão detalhados:*

IPEM-03 – Plant Model: organização física e funcional da Área de Extração.

IPEM-04 – Process Model: fluxo operacional do Sistema de Moagem.

IPEM-05 – Asset Model: identificação e classificação dos ativos industriais.

IPEM-06 – Instrumentation Model: modelagem da instrumentação associada aos ativos.

IPEM-07 – Telemetry Model: representação das variáveis de processo.

IPEM-08 – Event Model: modelagem dos eventos industriais.

IPEM-09 – KPI Model: definição dos indicadores operacionais.
