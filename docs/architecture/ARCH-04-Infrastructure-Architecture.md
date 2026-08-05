### 1. Introdução

O **Infrastructure Architecture** estabelece como as capacidades arquiteturais do Industrial Mill Streaming (IMS) são distribuídas entre os diferentes ambientes computacionais.

Seu objetivo é definir a organização lógica da infraestrutura necessária para suportar a arquitetura da plataforma, preservando disponibilidade, continuidade operacional, escalabilidade e integração entre os ambientes industriais e corporativos.

Este documento não define produtos, serviços ou fornecedores específicos.

Seu propósito é estabelecer responsabilidades arquiteturais de infraestrutura.

---

### 2. Architectural Question

> **Como distribuir as capacidades da arquitetura IMS entre diferentes ambientes computacionais preservando disponibilidade, desempenho e continuidade operacional?**

Essa pergunta orienta toda a arquitetura de infraestrutura.

---

### 3. Princípio Arquitetural

*Distributed by Responsibility*

> **As capacidades da arquitetura IMS devem ser distribuídas de acordo com sua responsabilidade operacional, e não pela tecnologia utilizada para implementá-las.**

A infraestrutura não determina a arquitetura.

Ela materializa decisões arquiteturais previamente estabelecidas.

---

### 4. Filosofia de Distribuição

O IMS adota uma arquitetura distribuída baseada na responsabilidade de cada capacidade.

A escolha do ambiente de execução não deve ser motivada pela disponibilidade de uma tecnologia específica, mas pelas necessidades operacionais de cada componente.

Essa abordagem considera aspectos como:

* proximidade com o processo industrial;
* criticidade operacional;
* necessidade de baixa latência;
* disponibilidade;
* escalabilidade;
* capacidade de processamento;
* integração corporativa;
* continuidade da operação.

---

### 5. Ambientes Arquiteturais

A infraestrutura do IMS é organizada em três ambientes lógicos.

```text id="5gkj2d"
Processo Industrial
        │
        ▼
      Edge
        │
        ▼
Ambiente Corporativo
        │
        ▼
      Cloud
```

Cada ambiente possui responsabilidades próprias e complementares.

---

### 6. Edge Domain

O Edge representa a camada mais próxima do processo industrial.

Seu principal objetivo é garantir que a aquisição de dados permaneça disponível independentemente da conectividade com ambientes externos.

Responsabilidades:

* aquisição de dados industriais;
* integração com as fontes;
* validações iniciais;
* buffer temporário;
* sincronização posterior quando necessário;
* proteção da infraestrutura de automação.

O Edge prioriza continuidade operacional e baixa latência.

---

### 7. Corporate Domain

O Ambiente Corporativo concentra capacidades compartilhadas entre diferentes aplicações da organização.

Responsabilidades:

* persistência operacional;
* integração entre sistemas corporativos;
* processamento compartilhado;
* governança local;
* serviços internos;
* disponibilização para aplicações corporativas.

Esse ambiente atua como elo entre o processo industrial e os consumidores internos da organização.

---

### 8. Cloud Domain

O ambiente Cloud concentra capacidades que se beneficiam de elasticidade e grande capacidade computacional.

Responsabilidades:

* processamento distribuído;
* analytics;
* ciência de dados;
* inteligência artificial;
* integração entre unidades industriais;
* armazenamento escalável;
* disponibilização para consumidores remotos.

A utilização da nuvem deve agregar valor sem comprometer a continuidade da operação industrial.

---

### 9. Continuidade Operacional

A arquitetura IMS assume que ambientes externos podem tornar-se temporariamente indisponíveis.

Entretanto, a operação industrial deve permanecer funcional.

```text id="m4cv8e"
Processo Industrial
        │
        ▼
      Edge
        │
        ├────────► Conectividade disponível
        │                 │
        │                 ▼
        │               Cloud
        │
        └────────► Conectividade indisponível
                          │
                          ▼
                 Continuidade da Operação
```

A indisponibilidade da conectividade não deve interromper:

* aquisição de dados;
* monitoramento local;
* execução dos sistemas de automação.

Quando restabelecida a comunicação, a sincronização entre ambientes deve ocorrer de maneira controlada.

---

### 10. Diretrizes Arquiteturais

A infraestrutura IMS deve observar as seguintes diretrizes:

* aproximar do processo apenas capacidades que realmente necessitam baixa latência;
* centralizar apenas responsabilidades que agreguem valor organizacional;
* preservar a independência operacional da planta;
* permitir sincronização assíncrona entre ambientes;
* favorecer escalabilidade sem comprometer estabilidade;
* minimizar impactos de falhas de conectividade;
* distribuir capacidades conforme suas responsabilidades.

---

### 11. Relação com os Próximos Documentos

O ARCH-04 define **onde** as capacidades arquiteturais devem existir.

Os documentos seguintes definirão:

| Documento                            | Responsabilidade                                       |
| ------------------------------------ | ------------------------------------------------------ |
| **ARCH-05 — Security Architecture**  | Como proteger a arquitetura distribuída                |
| **ARCH-06 — Analytics Architecture** | Como disponibilizar informações para consumo analítico |
| **ADR**                              | Quais tecnologias materializarão essa infraestrutura   |

---

### 12. Considerações Finais

O Infrastructure Architecture estabelece que a distribuição das capacidades do IMS deve refletir as necessidades do processo industrial e não as características de uma tecnologia específica.

Ao separar responsabilidades entre Edge, Ambiente Corporativo e Cloud, a arquitetura preserva a continuidade operacional da planta ao mesmo tempo em que cria condições para processamento analítico escalável e integração corporativa.

Essa abordagem permite que a infraestrutura evolua progressivamente sem romper os princípios arquiteturais estabelecidos pelo IMS.

```text id="q3az2k"
Processo Industrial
        │
        ▼
      Edge
        │
        ▼
Ambiente Corporativo
        │
        ▼
      Cloud
        │
        ▼
     Analytics
        │
        ▼
     Decisão
```

A infraestrutura deixa de ser apenas um conjunto de ambientes computacionais e passa a representar uma distribuição consciente de responsabilidades, alinhada aos objetivos da Engenharia de Dados Industrial.
