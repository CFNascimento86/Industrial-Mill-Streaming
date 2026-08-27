### 1. Contexto

O IMS representa processos, ativos e variáveis industriais ao longo de diferentes etapas do ciclo de vida da informação.

Esses elementos podem possuir diferentes representações técnicas em PLCs, protocolos, sistemas de aquisição, eventos e mecanismos de persistência.

O DM-02 estabelece como **Process, Asset e Variable mantêm identidade industrial estável**, independentemente das tecnologias utilizadas para representá-los.

---

### 2. Princípios de Identidade

O modelo estabelece três princípios fundamentais.

*Identity Before Storage*

A identidade industrial existe antes de qualquer representação física ou tecnológica.

*Identity Is Not Location*

A identidade não deverá depender de sua posição hierárquica, endereço técnico ou localização dentro de determinada tecnologia.

*Meaning Defines Continuity*

> *Se o significado industrial permanece, a identidade deve ser preservada. Se o significado muda, a identidade deve ser reconsiderada.*

Assim:

```text
Industrial Meaning
       │
       ▼
Stable Identity
       │
       ├── OPC UA
       ├── Kafka
       ├── PostgreSQL
       └── ADLS
````

---

### 3. Industrial Identity

Industrial Identity representa a identidade lógica e semanticamente significativa de uma entidade dentro do domínio industrial. Ela deverá permanecer independente de elementos como:

````
PLC Address
OPC UA NodeId
Kafka Topic
Database Key
Storage Path
````
Esses elementos pertencem à representação técnica.
````
INDUSTRIAL IDENTITY        TECHNICAL IDENTITY
───────────────────        ──────────────────
What is it?                Where is it?
What does it mean?         How is it accessed?
Where does it belong?      How is it represented?
````
A separação permite que a infraestrutura evolua sem alterar o significado das entidades industriais.

---

### 4. Process Identity

Process representa uma função industrial semanticamente reconhecível dentro da fronteira modelada.

No contexto do IMS:
````
PROCESS
   │
   ▼
Milling
````
Process não representa diretamente:

* PLC;
* rede industrial;
* banco de dados;
* estrutura de software;
* área de memória.

Sua identidade deriva da função exercida no domínio industrial.

Conceitualmente:
````
Industrial Process
       │
       └── Milling
````
O modelo permanece preparado para que outros processos sejam incorporados futuramente sem alterar a identidade daqueles já existentes.

---

### 5. Asset Identity

Asset representa um elemento físico ou funcional que possui identidade própria dentro do processo.
````
Milling
   │
   └── Mill 01
          │
          ├── Main Drive
          ├── Hydraulic System
          └── Roller Assembly
````
A identidade do Asset não deverá depender:
````
Asset Identity
      ≠
PLC Structure
OPC UA Structure
Network Topology
Database Structure
````
A organização adotada, representa a visão lógica necessária para compreensão e contextualização dos dados.

---

### 6. Asset Hierarchy

Assets poderão possuir relações hierárquicas entre si.
````
ASSET
  │
  └── contains
         │
         ▼
       ASSET
````
Exemplo:
````
Mill 01
│
├── Main Drive
│      ├── Motor
│      └── Gearbox
│
├── Hydraulic System
│
└── Roller Assembly
````
Essa abordagem evita criar diferentes entidades exclusivamente para representar níveis como equipamento, subsistema ou componente.

> Hierarchy provides semantic organization; it does not define identity.

Alterações na organização lógica não deverão, por si só, criar novas identidades industriais.

---

### 7. Variable Identity

Variable representa uma propriedade industrial observável associada a um Process ou Asset.

Exemplo:
````
Hydraulic System
       │
       └── Hydraulic Pressure
                    │
                    ▼
                 VARIABLE
````
Variable não representa a tag ou endereço utilizado para obter seu valor.
````
VARIABLE

Hydraulic Pressure
        │
        │ observed through
        ▼
OPC UA Node
ns=3;s=DB_Mill01.Pressure.PV
````
Portanto:

> Variable ≠ Tag

> Variable ≠ OPC UA Node

> Variable ≠ PLC Address

Esses elementos representam referências técnicas para uma propriedade industrial que possui identidade própria.

---

### 8. Stable Identity and Semantic Path

Identidade e localização semântica representam conceitos distintos.
````
Stable Identity
      │
      └── identifies the entity

Semantic Path
      │
      └── locates the entity in the model
````
Por exemplo:
````
Milling
   │
   └── Mill 01
          │
          └── Hydraulic System
                  │
                  └── Hydraulic Pressure
````
poderá fornecer um caminho semântico como:
````
milling/mill-01/hydraulic-system/hydraulic-pressure
````
Esse caminho é útil para navegação e interpretação, mas não deverá constituir sozinho a identidade definitiva da entidade. Portanto, uma reorganização hierárquica poderá alterar o caminho sem significar que a entidade industrial deixou de ser a mesma.

---

### 9. Identity Continuity

O IMS utilizará o significado industrial como principal critério de continuidade de identidade.

Mudança técnica
````
Hydraulic Pressure
        │
        ▼
OPC UA Node A
````
posteriormente:
````
Hydraulic Pressure
        │
        ▼
OPC UA Node B
````
Se a propriedade observada continuar sendo a mesma:
````
Industrial Identity → SAME
Technical Identity  → CHANGED
````
*Mudança de significado*

Se inicialmente a variável representar:
````
Pressure Before Control Valve
````
e posteriormente:
````
Pressure After Control Valve
````
ainda que ambas sejam denominadas Hydraulic Pressure, o significado industrial mudou.

Nesse caso:
````
Industrial Meaning → CHANGED
        │
        ▼
Identity must be reconsidered
````

---

### 10. Industrial and Technical Identity

O modelo estabelece uma fronteira explícita entre domínio industrial e domínio técnico.
````
          INDUSTRIAL DOMAIN

               PROCESS
                  │
                  ▼
                ASSET
                  │
             ┌────┴────┐
             │         │
             ▼         ▼
           ASSET    VARIABLE
                       │
                       │ observed through
                       ▼
────────────────────────────────
          TECHNICAL DOMAIN
                       │
                     SOURCE
````
Source, definido no DM-01 como entidade técnica, representa o mecanismo pelo qual determinada informação é obtida. 
Uma Variable poderá conceitualmente possuir diferentes Sources ao longo de seu ciclo de vida:
````
                   ┌── OPC UA Source
                   │
Hydraulic Pressure ┼── Historical Source
                   │
                   └── Simulation Source
````
A cardinalidade e materialização dessa relação serão definidas no Logical Data Model.

---

### 11. Modelo de Identidade

O núcleo conceitual do DM-02 pode ser representado como:
````
                  INDUSTRIAL IDENTITY

                       PROCESS
                          │
                          ▼
                        ASSET
                          │
                   ┌──────┴──────┐
                   │             │
                   ▼             ▼
                 ASSET        VARIABLE
                                  │
                                  │
                                  ▼
────────────────────────────────────────────
                    TECHNICAL BOUNDARY
                                  │
                                SOURCE
````
Transversalmente:
````
Stable Identity
      │
      ├── Process
      ├── Asset
      └── Variable

Semantic Hierarchy
      │
      └── organizes identities

Technical Reference
      │
      └── locates representations
````
Assim, identidade, organização semântica e representação técnica permanecem desacopladas.

---

### 12. Boundaries

O DM-02 não define:

* formato físico dos identificadores;
* nomenclatura definitiva dos IDs;
* estrutura definitiva dos semantic paths;
* Primary Keys ou Foreign Keys;
* estrutura ISA-95;
* OPC UA Information Model;
* endereçamento de PLC;
* estrutura de tópicos Kafka.

Essas decisões pertencem aos modelos lógico e físico ou a disciplinas externas ao escopo do IMS.

---

### 13. Related Engineering and Architecture

|Documento|	                    Relação                                         |
|---------|---------------------------------------------------------------------|
| IPEM-03 |	Define a organização do processo industrial                         |
| IPEM-05 |	Define os ativos relevantes e seu significado no processo           |
| ARCH-01 |	Estabelece organização lógica independente da infraestrutura física |
| ARCH-02 |	Define enriquecimento progressivo da informação                     |
| ADR-02  |	Estabelece desacoplamento entre aquisição e domínio informacional   |
| DM-01	  | Define Process, Asset, Variable e Source como entidades conceituais |

---

### 14. Considerações Finais

O DM-02 estabelece que Process, Asset e Variable possuem identidade industrial independente das tecnologias utilizadas para representá-los.
````
Process
   ↓
Asset
   ↓
Variable
   │
   │ Stable Industrial Identity
   │
   ├─────────────┐
   ▼             ▼
Semantic      Technical
Hierarchy     Representation
                  │
                  ▼
                Source
````
Essa separação permite que PLCs, protocolos, endereços, sistemas de aquisição e mecanismos de persistência evoluam sem comprometer a continuidade semântica das informações industriais.

O significado industrial torna-se, portanto, o principal critério para preservação da identidade.
