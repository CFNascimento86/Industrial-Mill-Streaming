### 1. Contexto

O DM-02 estabelece a identidade relativamente estável de **Process, Asset e Variable** dentro do domínio industrial. Entretanto, a informação industrial também possui uma dimensão temporal.

Valores são observados, estados mudam, condições surgem e acontecimentos são identificados ao longo do tempo. O DM-03 estabelece como **Telemetry e Event representam essas ocorrências temporais**, preservando identidade, cronologia e rastreabilidade independentemente da tecnologia utilizada para transportá-las ou processá-las.

---

### 2. Princípios de Modelagem Temporal

O modelo estabelece quatro princípios fundamentais.

-> *Observation Is Not Occurrence*

Telemetry representa uma observação temporal.

Event representa um acontecimento significativo.

-> *Industrial Time Before Processing Time*

A cronologia industrial deverá ser determinada prioritariamente pelo momento em que algo ocorreu no domínio, e não pelo momento em que foi processado pela plataforma.

-> *Arrival Order Is Not Industrial Order*

A sequência de chegada das informações ao IMS não necessariamente representa a sequência real dos acontecimentos industriais.

-> *Reprocessing Is Not Reoccurrence*

O reprocessamento de uma informação não significa que o acontecimento industrial ocorreu novamente.

---

### 3. Telemetry

*Telemetry* representa uma observação temporal de uma Variable.

```text
VARIABLE
Hydraulic Pressure
       │
       ├── 10:31:01 → 182.7 bar
       ├── 10:31:02 → 184.1 bar
       ├── 10:31:03 → 185.4 bar
       └── 10:31:04 → 183.9 bar
````
A Variable estabelece aquilo que pode ser observado.

Cada Telemetry representa aquilo que efetivamente foi observado em determinado momento.
````
Variable
   │
   │ observed as
   ▼
Telemetry
````

---

### 4. Telemetry Identity

Cada observação deverá ser individualmente identificável.

A identidade de uma Telemetry não deverá depender exclusivamente da combinação:
````
Variable + Timestamp
````
Essa combinação pode ser insuficiente diante de condições como:

* leituras repetidas;
* retransmissão;
* replay;
* resolução temporal limitada;
* dados fora de ordem;
* diferentes origens técnicas.

Conceitualmente:
````
TELEMETRY
    │
    ├── Identity
    ├── Variable
    ├── Observation
    ├── Time
    └── Quality
````
O formato físico dessa identidade será definido posteriormente.

---

### 5. Event

Event representa uma ocorrência industrial significativamente identificada, produzida ou derivada ao longo do fluxo informacional.

Exemplo:
````
Telemetry

Pressure = 185.4 bar
Pressure = 187.2 bar
Pressure = 189.1 bar
        │
        ▼
  Interpretation
        │
        ▼
      Event

High Hydraulic Pressure Detected
````
Events poderão representar, entre outros:

* State Change
* Operating Transition
* Condition Detected
* Production Event
* Derived Condition
* Engineering Event

Sua interpretação deverá permanecer alinhada às regras de engenharia e ao Event Model definido no IPEM-08.

---

### 6. Telemetry × Event

Telemetry e Event possuem responsabilidades diferentes.
````
TELEMETRY
    │
    ▼
What was observed?


  EVENT
    │
    ▼
What happened?
````
Uma Telemetry poderá contribuir para diferentes Events e um Event poderá resultar da correlação de múltiplas observações.
````
Telemetry A ───┐
Telemetry B ───┼────► Event X
Telemetry C ───┘
````
Conceitualmente:
````
TELEMETRY
     N
     │
     │ contributes to
     │
     N
   EVENT
````
Nem toda Telemetry produz um Event.

Nem todo Event depende de uma única Telemetry.

---

### 7. Industrial Time

Uma informação poderá possuir diferentes momentos relevantes ao longo de seu ciclo de vida.

O IMS distingue conceitualmente:

-> *Occurrence Time*

Representa quando a observação ou acontecimento ocorreu no domínio industrial.

-> *Ingestion Time*

Representa quando a informação entrou na plataforma IMS.

-> *Processing Time*

Representa quando determinada capacidade da plataforma processou a informação.
````
Industrial Domain

Occurrence
10:31:02.125
      │
      ▼
Acquisition
10:31:02.180
      │
      ▼
    Kafka
      │
      ▼
Processing
10:31:02.240
````
Esses tempos representam fatos diferentes e não deverão ser tratados como equivalentes.

---

### 8. Event Time × Processing Time

Para estabelecer a cronologia industrial, o IMS prioriza Event Time, representado pelo momento de ocorrência no domínio.
````
EVENT TIME
    │
    └── when it happened


PROCESSING TIME
    │
    └── when IMS processed it
````
Exemplo:
````
Industrial Occurrence
occurred_at = 10:31:02
        │
        │ network / processing delay
        ▼
IMS Processing
processed_at = 10:31:05
````
O acontecimento continua pertencendo à cronologia industrial de 10:31:02.

> Industrial chronology follows occurrence time, not processing time.

Essa distinção será fundamental para correlação, agregações, histórico, replay e análises posteriores.

---

### 9. Temporal Ordering

Sistemas industriais distribuídos não garantem que informações sejam recebidas na mesma ordem em que ocorreram.

Exemplo:
````
Industrial Order

10:31:02 ─── A
10:31:03 ─── B
10:31:04 ─── C
````
Entretanto:
````
Arrival Order

10:31:03 ─── B
10:31:04 ─── C
10:31:06 ─── A
````
Portanto:
````
Arrival Order
B → C → A

Industrial Order
A → B → C
````
O modelo deverá preservar informação temporal suficiente para reconstruir a cronologia industrial.

> Arrival order does not necessarily represent industrial order.

Conceitos de implementação como watermark, reorder buffer ou tolerância temporal não pertencem ao escopo deste documento.

---

### 10. Event Duration

Nem todo Event representa um instante isolado.

O modelo deverá suportar conceitualmente eventos pontuais e eventos associados a intervalos.
````
Point Event
Motor Started
      ▲
      │
   10:31:02
Interval Event
High Load Condition

10:31:02 ├─────────────────┤ 10:34:48
````
Conceitualmente:
````
EVENT
  │
  ├── Point Event
  │
  └── Interval Event
````
A representação física de início, término ou duração será definida posteriormente.

---

### 11. Telemetry Quality

Uma observação industrial não é completamente representada apenas por seu valor.

O modelo deverá preservar informação sobre a qualidade da observação.
````
TELEMETRY
    │
    ├── Observation
    ├── Time
    └── Quality
````
Conceitualmente, a qualidade poderá representar condições como:
````
GOOD
UNCERTAIN
BAD
UNKNOWN
````
O DM-03 não define códigos específicos de protocolos ou tecnologias.

> Value without quality is an incomplete industrial observation.

A interpretação posterior deverá ser capaz de distinguir um valor válido de uma observação cuja confiabilidade esteja comprometida.

---

### 12. Correlation and Traceability

Telemetry e Event poderão participar de cadeias de informação derivada.
````
Telemetry A
      │
      ▼
Event X
      │
      ▼
Event Y
      │
      ▼
Derived Information
````
Cada ocorrência deverá preservar identidade própria, enquanto relacionamentos deverão permitir rastrear sua origem conceitual.

Assim:
````
Identity
   │
   └── identifies one occurrence

Correlation
   │
   └── relates multiple occurrences
````
O DM-03 não determina ainda um atributo físico como correlation_id.

Estabelece apenas que:

> Temporal entities must support traceable relationships across derived occurrences.

---

### 13. Replay Semantics

A arquitetura do IMS permite que informações previamente registradas sejam processadas novamente.

Entretanto, replay pertence à história de processamento e não cria necessariamente um novo acontecimento industrial.
````
Industrial Event
occurred_at = 10:31:02
        │
        ├── Processing Attempt 1
        │
        └── Processing Attempt 2
````
O acontecimento industrial permanece o mesmo.

O que mudou foi sua trajetória de processamento.
````
Industrial Occurrence
        │
        │ SAME
        ▼
Event Identity

Processing History
        │
        ├── Original Processing
        └── Replay
````
> Reprocessing changes processing history, not industrial occurrence identity.

Essa separação preserva consistência durante recuperação, replay e reprocessamento.

---

### 14. Modelo Temporal

O núcleo conceitual do DM-03 pode ser representado como:
````
                 INDUSTRIAL IDENTITY

                      VARIABLE
                         │
                         │ observed as
                         ▼
                    TELEMETRY
                   ┌─────┼─────┐
                   │     │     │
                   ▼     ▼     ▼
               Identity Time Quality
                         │
                         │ contributes to
                         ▼
                       EVENT
                    ┌─────┴─────┐
                    │           │
                    ▼           ▼
               Point Event  Interval Event
                    │           │
                    └─────┬─────┘
                          ▼
                  Temporal Meaning
````
A dimensão temporal é organizada em duas perspectivas:
````
Industrial Timeline
       │
       └── Occurrence Time


Platform Timeline
       │
       ├── Ingestion Time
       └── Processing Time
````
Essa separação permite preservar simultaneamente a cronologia do processo e a trajetória da informação dentro da plataforma.

---

### 15. Boundaries

O DM-03 não define:

* formato físico de telemetry_id ou event_id;
* tipos de timestamp;
* precisão temporal definitiva;
* timezone de armazenamento;
* atributos Avro;
* estrutura de payload;
* Kafka timestamps;
* particionamento de tópicos.

Essas decisões pertencem aos modelos lógico e físico ou às respectivas decisões de implementação.

---

### 16. Related Engineering and Architecture

|Documento|	                                Relação                                               |
|---------|---------------------------------------------------------------------------------------|
| IPEM-07 |	Define Telemetry como representação contextualizada de observações industriais        |
| IPEM-08 |	Define Event Model e preservação das regras de engenharia                             |                             
| ARCH-02 |	Estabelece Progressive Information Enrichment                                         |
| ADR-04	| Define identidade e contratos dos eventos                                             |
| ADR-05	| Define processamento contínuo Near Real Time                                          |
| ADR-06	| Define delivery semantics, replay, consumer lag e tratamento de falhas                |
| ADR-08	| Estabelece correlação e observabilidade da trajetória dos eventos                     |
| DM-01	  | Define Telemetry e Event como entidades temporais                                     |
| DM-02   |	Estabelece as identidades industriais às quais as ocorrências temporais se relacionam |

---

### 17. Considerações Finais

O DM-03 estabelece a dimensão temporal do modelo industrial do IMS.
````
Variable
   │
   ▼
Telemetry
   │
   ├── Identity
   ├── Quality
   └── Occurrence Time
            │
            ▼
          Event
            │
            ▼
    Temporal Meaning
````
Telemetry representa aquilo que foi observado.

Event representa aquilo que aconteceu ou foi identificado como significativo.

Occurrence Time preserva a cronologia industrial, enquanto Ingestion Time e Processing Time descrevem a trajetória da informação dentro da plataforma.

Essa separação permite que atrasos, informações fora de ordem, replay e reprocessamento ocorram sem comprometer o significado temporal original dos dados.
