### Industrial Data Generator — Core Tests

Esta suíte valida as propriedades fundamentais do núcleo do **Industrial Data Generator** utilizado pelo IMS.

O objetivo dos testes não é validar uma representação física completa do processo de Moenda, mas garantir que o modelo sintético apresente comportamento **reproduzível, temporalmente coerente e causalmente consistente** antes de sua exposição por meio do Reference S7 Runtime.

---

### Objetivo

Os testes protegem quatro propriedades fundamentais do gerador:

| Propriedade | Garantia |
|---|---|
| **Determinismo** | Mesma configuração, seed e sequência de execução produzem os mesmos resultados |
| **Scenario Transition** | Mudanças de condição operacional ocorrem progressivamente |
| **Causal Correlation** | Variáveis correlacionadas respondem coerentemente às mudanças do processo |
| **Order Invariance** | A ordem declarativa dos sinais não altera a dinâmica simulada |

Essas propriedades constituem a fronteira de validação do núcleo do gerador.

---

### Estrutura

```
tests/
├── README.md
├── conftest.py
├── test_determinism.py
├── test_scenario_transition.py
├── test_causal_correlation.py
└── test_order_invariance.py
````

---

### *test_determinism.py*

Valida a reprodutibilidade da simulação.
````
same configuration
+ same seed
+ same scenario
+ same dt
        ↓
same synthetic sequence
````
Cada sinal utiliza um gerador pseudoaleatório determinístico próprio, derivado da seed global e de seu logical_name.

Isso permite reproduzir execuções e cenários durante desenvolvimento, investigação de falhas e testes de integração.

---

### *test_scenario_transition.py*

Valida a evolução temporal dos modificadores aplicados pelo ScenarioEngine.

Uma mudança de cenário não precisa produzir uma alteração instantânea:
````
normal_operation
        │
        ▼
   transition
        │
        ▼
    high_load
````
Os testes verificam tanto a entrada em uma nova condição operacional quanto o retorno progressivo ao estado nominal por meio de process_recovery.

---

### *test_causal_correlation.py*

Valida relações causais fundamentais definidas no modelo sintético.

Exemplo:
````
cane_flow ↑
     │
     ├──► main_drive_01_torque ↑
     │
     └──► juice_flow ↑
````
Os testes avaliam tendências sustentadas, e não valores instantâneos exatos.

Essa abordagem evita acoplar a validação ao ruído sintético e concentra o teste na propriedade industrial que o modelo pretende representar.

---

### *test_order_invariance.py*

Valida que a ordem dos sinais no process.yaml não interfere no comportamento da simulação.
````
A → B → C → D

e

D → C → B → A

        ↓

mesma evolução do processo
````
Essa propriedade é garantida por duas decisões de implementação:

1. todos os modelos calculam o próximo estado utilizando a mesma fotografia State(t);
2. cada sinal possui seu próprio PRNG determinístico.

Assim:

> Configuration order does not define process semantics.

---

### Ground Truth
Os cenários definidos em scenarios.yaml representam condições conhecidas pelo ambiente de geração.

Essa informação constitui o Engineering Ground Truth do simulador.
````
Industrial Data Generator
        │
        ├── synthetic observations
        │
        └── engineering ground truth
````
O Ground Truth existe para desenvolvimento e validação.

Ele não deve ser publicado pelo gerador como Telemetry, Event ou Operational Context para o IMS.

Isso permite que, futuramente, o Processing Service infira contexto operacional a partir das observações e que seus resultados sejam comparados com a condição originalmente gerada.

---

### Executando os testes
A partir do diretório industrial-data-generator:
````
pytest
````
Para execução detalhada:
````
pytest -v
````
Para executar apenas uma propriedade:
````
pytest tests/test_determinism.py -v
````

---

### Escopo

Esta suíte valida o núcleo comportamental do Industrial Data Generator.

Ela não valida:

- comunicação Siemens S7;
- endereçamento de DBs;
- aquisição pelo IMS;
- contratos Avro;
- publicação no Kafka;
- persistência no PostgreSQL;
- inferência de contexto operacional;
- KPIs.

Essas responsabilidades pertencem a outras fronteiras de teste do IMS.

---

### Critério de conclusão
O core do Industrial Data Generator é considerado válido para o M1 quando as seguintes propriedades estiverem protegidas por testes automatizados:
````
Deterministic
     +
Scenario-aware
     +
Causally coherent
     +
Order-independent
     =
Validated Synthetic Process Core
````
Após essa fronteira, os snapshots produzidos pelo ProcessEngine podem ser materializados no Reference S7 Runtime.

---

### Princípio

> The generator supports the implementation. It is not the industrial architecture.

O Industrial Data Generator existe para tornar a implementação de referência do IMS reproduzível e testável independentemente do acesso à infraestrutura OT real.
