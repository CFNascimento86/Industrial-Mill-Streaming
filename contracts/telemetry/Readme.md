## Telemetry Contracts

Este diretório contém os contratos de dados utilizados para representar
observações de telemetria industrial no IMS.

### TelemetryObservation

`TelemetryObservation` representa uma única observação industrial adquirida
e contextualizada na fronteira de aquisição.

O contrato é independente do protocolo de origem.

Informações específicas de transporte ou aquisição, como endereço Modbus,
offset de PLC, NodeId OPC UA ou parâmetros de conectividade, não fazem parte
do contrato.

### Princípios

- Identity Is Not Location
- Observation Is Not Meaning
- Observation Is Not Occurrence
- Industrial Time Before Processing Time
- The contract belongs to the information, not to the producer.

### Versionamento

A evolução e compatibilidade dos schemas serão governadas pelo Schema
Registry.

O nome do arquivo contém a versão inicial apenas para organização do
repositório durante o desenvolvimento.
