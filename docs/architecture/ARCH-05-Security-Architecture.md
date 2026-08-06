### 1. Introdução

O **Security Architecture** estabelece os princípios responsáveis por garantir a confiança, a integridade e a governança das informações produzidas pelo Industrial Mill Streaming (IMS).

No contexto do IMS, segurança não representa a proteção da infraestrutura industrial ou dos sistemas responsáveis pelo controle do processo.

Seu propósito consiste em assegurar que os dados produzidos, transformados e disponibilizados pela arquitetura permaneçam íntegros, rastreáveis e confiáveis durante todo o seu ciclo de vida.

Este documento estabelece princípios arquiteturais relacionados à proteção da plataforma de dados.

Aspectos referentes à proteção de infraestruturas críticas, redes industriais e sistemas de controle pertencem às disciplinas especializadas de OT Cybersecurity e encontram-se fora do escopo desta especificação.

---

### 2. Architectural Question

> **Como garantir que as informações produzidas e disponibilizadas pelo IMS permaneçam confiáveis durante todo o seu ciclo de vida?**

Essa pergunta orienta toda a arquitetura de segurança do IMS.

---

### 3. Princípio Arquitetural

*Trusted Information by Design*

> **Toda informação produzida pela arquitetura IMS deve preservar identidade, origem, integridade e rastreabilidade ao longo de todo o seu ciclo de vida.**

A confiança na informação deve ser consequência da arquitetura e não apenas da aplicação de mecanismos tecnológicos.

---

### 4. Escopo Arquitetural

A arquitetura de segurança do IMS concentra-se na proteção da plataforma de dados e das informações por ela produzidas.

Inclui conceitualmente:

* identidade das informações;
* rastreabilidade;
* proveniência;
* integridade;
* auditoria;
* governança;
* controle de acesso aos dados;
* proteção dos contratos de integração;
* preservação dos metadados.

O documento não contempla aspectos relacionados à proteção física ou operacional da infraestrutura industrial.

---

### 5. Fronteira entre OT Cybersecurity e IMS

O IMS estabelece uma separação clara entre a segurança da plataforma de dados e a proteção da infraestrutura industrial.

```text id="2yik1o"
OT Cybersecurity
        │
        ├── Redes Industriais
        ├── PLCs
        ├── Firewalls
        ├── Infraestrutura Crítica
        ├── IEC 62443
        ├── NIST
        └── Segurança Operacional
        │
────────────────────────────────────
        │
Industrial Mill Streaming
        │
        ├── Governança
        ├── Proveniência
        ├── Integridade
        ├── Auditoria
        ├── Linhagem
        ├── Metadados
        ├── Controle de Acesso
        └── Rastreabilidade
```

Essa separação garante que cada disciplina preserve suas responsabilidades e competências específicas.

---

### 6. Objetivos Arquiteturais

A arquitetura de segurança do IMS deve assegurar:

* autenticidade das informações;
* integridade dos dados;
* rastreabilidade completa;
* auditoria das transformações;
* controle de acesso às informações;
* preservação da origem;
* confiança nos contratos de integração;
* governança dos metadados.

Esses objetivos devem acompanhar toda a jornada da informação dentro da arquitetura.

---

### 7. Confiança na Informação

A confiança em uma informação não é determinada apenas pelo seu conteúdo.

Ela depende da capacidade da arquitetura responder perguntas como:

* Qual a origem desta informação?
* Quando ela foi adquirida?
* Quais transformações foram aplicadas?
* Qual componente realizou cada transformação?
* Quem consumiu essa informação?
* Qual versão do contrato foi utilizada?

Responder essas perguntas fortalece a transparência e a confiabilidade da plataforma.

---

### 8. Diretrizes Arquiteturais

A arquitetura IMS deve garantir que:

* toda informação possua origem identificável;
* transformações permaneçam auditáveis;
* metadados acompanhem os dados;
* contratos de integração sejam preservados;
* consumidores utilizem apenas informações autorizadas;
* mecanismos de proteção não comprometam a continuidade operacional;
* responsabilidades permaneçam claramente segregadas.

---

### 9. Relação com os Próximos Documentos

O ARCH-05 estabelece **como a plataforma preserva a confiança nas informações**.

O documento seguinte definirá **como essas informações serão disponibilizadas aos consumidores da arquitetura.**

| Documento                            | Responsabilidade                                                              |
| ------------------------------------ | ----------------------------------------------------------------------------- |
| **ARCH-06 — Analytics Architecture** | Disponibilização da informação para investigação e tomada de decisão          |
| **ADR**                              | Decisões tecnológicas relacionadas à implementação dos mecanismos de proteção |

---

### 10. Considerações Finais

A arquitetura de segurança do IMS estabelece que a confiança na informação deve ser construída desde sua aquisição até sua disponibilização para consumo analítico.

Ao preservar identidade, origem, integridade, rastreabilidade e governança, a arquitetura garante que decisões operacionais sejam tomadas sobre informações cuja procedência e histórico possam ser verificados.

Essa abordagem reforça que, no contexto do IMS, segurança não significa apenas restringir acessos.

Significa assegurar que a informação permaneça confiável durante todo o seu ciclo de vida, sem interferir nas responsabilidades próprias da Engenharia de Controle e Automação ou das disciplinas de OT Cybersecurity.

```text id="kxt0qz"
      Origem
        │
        ▼
    Integridade
        │
        ▼
  Rastreabilidade
        │
        ▼
     Governança
        │
        ▼
    Confiança
        │
        ▼
     Decisão
```
