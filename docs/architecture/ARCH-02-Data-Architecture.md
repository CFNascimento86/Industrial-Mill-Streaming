### 1. Introdução

O **Data Architecture** estabelece como os dados evoluem ao longo da arquitetura do Industrial Mill Streaming (IMS).

Seu objetivo é definir a progressão lógica da informação desde sua aquisição até sua disponibilização para consumo analítico, preservando contexto, rastreabilidade e significado industrial.

Este documento não define tecnologias, bancos de dados ou estruturas físicas de armazenamento.

Seu propósito é estabelecer o modelo conceitual de evolução da informação.

---

### 2. Architectural Question

> **Como os dados evoluem desde sua aquisição até se tornarem informações capazes de apoiar investigação e tomada de decisão?**

Essa pergunta orienta toda a arquitetura de dados do IMS.

---

### 3. Princípio Arquitetural

*Progressive Information Enrichment*

> **Ao percorrer a arquitetura IMS, os dados devem receber progressivamente contexto, significado e rastreabilidade, evoluindo de registros técnicos para informações capazes de apoiar investigação e tomada de decisão.**

O IMS não tem como objetivo apenas transportar ou armazenar dados.

Seu papel é enriquecer continuamente a informação sem perder sua origem.

---

### 4. Evolução da Informação

A arquitetura organiza os dados segundo uma sequência lógica de enriquecimento.

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
Informação Industrial
        │
        ▼
Conhecimento Analítico
```

Cada estágio acrescenta novos elementos sem alterar a identidade da informação original.

---

### 5. Estágios da Informação

#### *5.1 - Dado Técnico*

Representa a informação exatamente como disponibilizada pela infraestrutura industrial.

Exemplos:

* valores de variáveis;
* estados de equipamentos;
* códigos operacionais;
* timestamps de origem.

Nesse estágio predominam as características técnicas da fonte.


#### *5.2 - Dado Adquirido*

Representa a informação após sua captura pela arquitetura.

São preservados:

* origem;
* instante de aquisição;
* integridade do valor;
* rastreabilidade inicial.

O dado continua refletindo fielmente sua origem técnica.


#### *5.3 - Dado Contextualizado*

Representa o momento em que a informação passa a possuir significado industrial.

Nesse estágio os dados são associados aos modelos definidos no IPEM:

* domínio;
* processo;
* ativo;
* instrumentação;
* telemetria.

O foco deixa de ser "onde o dado foi obtido" e passa a ser "o que esse dado representa".


#### *5.4 - Informação Industrial*

Corresponde à integração entre telemetrias, eventos e contexto operacional.

Nesse estágio tornam-se possíveis:

* correlações;
* análises temporais;
* interpretação operacional;
* identificação de comportamentos relevantes.


#### *5.5 - Conhecimento Analítico*

Representa a consolidação da informação em indicadores e conjuntos preparados para consumo.

Inclui:

* KPIs;
* análises operacionais;
* suporte à investigação;
* apoio à decisão.

O objetivo não é apenas informar o desempenho, mas explicar as condições que o produziram.

---

### 6. Fluxo Conceitual da Informação

```text
Infraestrutura Industrial
        │
        ▼
    Aquisição
        │
        ▼
Enriquecimento Progressivo
        │
        ▼
Contextualização
        │
        ▼
     Eventos
        │
        ▼
      KPIs
        │
        ▼
   Investigação
        │
        ▼
     Decisão
```

O fluxo representa a evolução lógica da informação, independentemente da tecnologia utilizada para implementá-lo.

---

### 7. Diretrizes Arquiteturais

A arquitetura de dados do IMS deve garantir que:

* a origem da informação seja preservada;
* o contexto seja enriquecido progressivamente;
* as transformações permaneçam rastreáveis;
* o significado industrial nunca seja perdido;
* consumidores utilizem informações contextualizadas e não estruturas técnicas das fontes.

Essas diretrizes asseguram consistência entre engenharia, arquitetura e consumo analítico.

---

### 8. Relação com os Próximos Documentos

O ARCH-02 estabelece **como a informação evolui**.

Os documentos seguintes detalharão **como essa evolução será materializada**.

| Documento                                 | Responsabilidade                                             |
| ----------------------------------------- | ------------------------------------------------------------ |
| **ARCH-03 — Integration Architecture**    | Comunicação entre fontes, componentes e consumidores         |
| **ARCH-04 — Infrastructure Architecture** | Distribuição das capacidades entre Edge, On-Premises e Cloud |
| **ARCH-05 — Security Architecture**       | Proteção, identidade, acesso e auditoria                     |
| **ARCH-06 — Analytics Architecture**      | Disponibilização da informação para investigação e decisão   |

---

### 9. Considerações Finais

O Data Architecture estabelece que o valor da informação não está em sua aquisição, mas em sua evolução ao longo da arquitetura.

À medida que percorrem o IMS, os dados recebem contexto, significado e rastreabilidade, tornando-se progressivamente mais úteis para compreender o comportamento do processo industrial.

Essa abordagem garante que a plataforma não apenas mova dados entre sistemas, mas transforme registros técnicos em conhecimento capaz de apoiar investigação, decisão e melhoria contínua.

```text
   Dado Técnico
        │
        ▼
Informação Contextualizada
        │
        ▼
   Conhecimento
        │
        ▼
   Investigação
        │
        ▼
     Decisão
```
