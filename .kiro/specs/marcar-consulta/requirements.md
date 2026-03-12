# Requirements Document

## Introduction

Este documento especifica os requisitos para o fluxo de Marcar Consulta em um sistema de agendamento médico com interface conversacional baseada em LangGraph. O sistema utiliza uma arquitetura modular com múltiplos grafos independentes, onde cada subfluxo possui seu próprio grafo LangGraph e SYSTEM_MESSAGE específico. O fluxo de marcar consulta é executado em um grafo isolado que recebe apenas os dados do paciente (sem histórico de conversas anteriores) e retorna dados estruturados para orquestração Python.

## Glossary

- **Sistema_Agendamento**: O sistema completo de agendamento de consultas médicas
- **Grafo_Marcar_Consulta**: Grafo LangGraph específico (configure_graph_marcar_consulta) responsável pelo fluxo de agendamento
- **Orquestrador_Python**: Código Python em main.py que gerencia transições entre grafos
- **Paciente**: Usuário cadastrado no sistema que deseja agendar uma consulta
- **Dados_Paciente**: Estrutura JSON contendo id, nome e CPF do paciente
- **Especialidade**: Área médica específica (ex: Cardiologia, Dermatologia)
- **Procedimento**: Procedimento médico específico que pode ser agendado
- **Médico**: Profissional de saúde com CRM e especialidades cadastradas
- **Slot_Disponível**: Intervalo de tempo de 20 minutos disponível na agenda de um médico
- **Consulta**: Agendamento confirmado entre paciente e médico
- **Disponibilidade_Médico**: Períodos em que um médico está disponível para atendimentos
- **Janela_Agendamento**: Período de 14 dias a partir da data atual para agendamentos
- **SYSTEM_MESSAGE_Marcar_Consulta**: Prompt específico em prompt.py focado apenas no fluxo de agendamento
- **Estado_Mínimo**: State contendo apenas Dados_Paciente, sem histórico de conversas

## Requirements

### Requirement 1: Criar Grafo LangGraph Independente

**User Story:** Como desenvolvedor, quero um grafo LangGraph específico para marcar consulta, para que o fluxo seja isolado e tenha contexto reduzido.

#### Acceptance Criteria

1. THE Sistema_Agendamento SHALL implementar a função configure_graph_marcar_consulta() em src/ia/graph.py
2. THE Grafo_Marcar_Consulta SHALL ser independente dos outros grafos (cadastro e menu)
3. THE Grafo_Marcar_Consulta SHALL receber apenas Dados_Paciente como entrada, sem histórico de conversas anteriores
4. THE Grafo_Marcar_Consulta SHALL utilizar SYSTEM_MESSAGE_Marcar_Consulta específico definido em src/ia/prompt.py
5. THE Grafo_Marcar_Consulta SHALL utilizar bind_tools com as ferramentas de TOOLS_MENU necessárias
6. THE Grafo_Marcar_Consulta SHALL retornar dados estruturados (JSON) ao Orquestrador_Python
7. THE Grafo_Marcar_Consulta SHALL utilizar RunnableConfig com thread_id para isolamento de conversas

### Requirement 2: Definir SYSTEM_MESSAGE Focado

**User Story:** Como desenvolvedor, quero um prompt específico para o fluxo de agendamento, para que o agente tenha instruções claras e contexto reduzido.

#### Acceptance Criteria

1. THE Sistema_Agendamento SHALL criar SYSTEM_MESSAGE_Marcar_Consulta em src/ia/prompt.py
2. THE SYSTEM_MESSAGE_Marcar_Consulta SHALL conter apenas instruções para o fluxo de agendamento
3. THE SYSTEM_MESSAGE_Marcar_Consulta SHALL instruir o agente a solicitar especialidade ou sintoma
4. THE SYSTEM_MESSAGE_Marcar_Consulta SHALL instruir o agente a apresentar opções de especialidades/procedimentos
5. THE SYSTEM_MESSAGE_Marcar_Consulta SHALL instruir o agente a buscar e apresentar disponibilidade de médicos
6. THE SYSTEM_MESSAGE_Marcar_Consulta SHALL instruir o agente a confirmar antes de criar a consulta
7. THE SYSTEM_MESSAGE_Marcar_Consulta SHALL instruir o agente a retornar confirmação estruturada após agendamento
8. THE SYSTEM_MESSAGE_Marcar_Consulta SHALL NOT conter instruções sobre cadastro ou outras funcionalidades

### Requirement 3: Gerenciar Estado Mínimo

**User Story:** Como desenvolvedor, quero que o grafo utilize apenas dados essenciais, para que o contexto seja reduzido e a performance otimizada.

#### Acceptance Criteria

1. THE Grafo_Marcar_Consulta SHALL receber Estado_Mínimo contendo apenas id_paciente, nome e CPF
2. THE Grafo_Marcar_Consulta SHALL NOT receber histórico de conversas anteriores (cadastro ou menu)
3. THE Grafo_Marcar_Consulta SHALL acessar Dados_Paciente através de state["paciente"]
4. THE Grafo_Marcar_Consulta SHALL manter apenas o histórico de mensagens da conversa de agendamento atual
5. WHEN o agendamento é concluído, THE Grafo_Marcar_Consulta SHALL retornar dados estruturados sem manter estado persistente

### Requirement 4: Buscar Especialidades e Procedimentos

**User Story:** Como paciente, quero buscar especialidades médicas disponíveis, para que eu possa escolher a área médica adequada para minha consulta.

#### Acceptance Criteria

1. WHEN o Paciente fornece um termo de busca, THE Grafo_Marcar_Consulta SHALL chamar a tool consultar_especialidade_procedimento
2. THE Sistema_Agendamento SHALL retornar todas as Especialidades cujo nome contenha o termo (case-insensitive)
3. THE Sistema_Agendamento SHALL retornar todos os Procedimentos cujo nome contenha o termo (case-insensitive)
4. THE Sistema_Agendamento SHALL retornar cada resultado com identificador único, nome e tipo (1 para Especialidade, 2 para Procedimento)
5. WHEN nenhuma Especialidade ou Procedimento corresponde ao termo, THE Sistema_Agendamento SHALL retornar uma lista vazia
6. THE Grafo_Marcar_Consulta SHALL apresentar os resultados de forma clara ao Paciente

### Requirement 5: Consultar Disponibilidade de Médicos

**User Story:** Como paciente, quero visualizar os horários disponíveis para uma especialidade, para que eu possa escolher um médico e horário convenientes.

#### Acceptance Criteria

1. WHEN o Paciente seleciona uma Especialidade, THE Grafo_Marcar_Consulta SHALL chamar a tool consultar_agenda_disponibilidade
2. THE Sistema_Agendamento SHALL buscar todos os Médicos que atendem aquela Especialidade
3. WHEN o Paciente seleciona um Procedimento, THE Sistema_Agendamento SHALL buscar todos os Médicos que realizam aquele Procedimento
4. THE Sistema_Agendamento SHALL retornar apenas Slots_Disponíveis dentro da Janela_Agendamento (14 dias)
5. THE Sistema_Agendamento SHALL gerar Slots_Disponíveis em intervalos de 20 minutos
6. WHEN um Médico tem Disponibilidade_Médico com status LIVRE, THE Sistema_Agendamento SHALL gerar Slots_Disponíveis para aquele período
7. THE Sistema_Agendamento SHALL considerar apenas dias da semana que correspondem ao dia_semana da Disponibilidade_Médico
8. THE Sistema_Agendamento SHALL respeitar os horários de início e fim definidos na Disponibilidade_Médico
9. THE Sistema_Agendamento SHALL agrupar os resultados por Médico, mostrando nome e lista de datas disponíveis
10. THE Sistema_Agendamento SHALL ordenar os Slots_Disponíveis por data e depois por id do Médico
11. THE Grafo_Marcar_Consulta SHALL apresentar os horários disponíveis agrupados por médico de forma clara

### Requirement 6: Marcar Consulta

**User Story:** Como paciente, quero confirmar o agendamento de uma consulta, para que eu possa garantir meu atendimento médico.

#### Acceptance Criteria

1. WHEN o Paciente seleciona um Médico, data/horário e Especialidade, THE Grafo_Marcar_Consulta SHALL chamar a tool marcar_consulta_procedimento
2. THE Sistema_Agendamento SHALL criar um registro de Consulta no banco de dados
3. THE Sistema_Agendamento SHALL armazenar o id do Paciente, id do Médico, id da Especialidade e data/horário da consulta
4. THE Sistema_Agendamento SHALL registrar a data de criação da Consulta como o timestamp atual
5. THE Sistema_Agendamento SHALL definir id_funcionario como 1 (sistema automático)
6. WHEN a Consulta é criada com sucesso, THE Sistema_Agendamento SHALL retornar os dados da consulta agendada
7. THE Grafo_Marcar_Consulta SHALL confirmar o agendamento ao Paciente com todos os detalhes (médico, especialidade, data e horário)

### Requirement 7: Validação de Dados do Agendamento

**User Story:** Como sistema, quero validar os dados antes de criar uma consulta, para que eu possa garantir a integridade dos agendamentos.

#### Acceptance Criteria

1. WHEN o Paciente tenta agendar uma consulta, THE Sistema_Agendamento SHALL verificar que o id_paciente existe no banco de dados
2. WHEN o Paciente tenta agendar uma consulta, THE Sistema_Agendamento SHALL verificar que o id_medico existe no banco de dados
3. WHEN o Paciente tenta agendar uma consulta, THE Sistema_Agendamento SHALL verificar que o id_tipo_especialidade existe no banco de dados
4. WHEN o Paciente tenta agendar uma consulta, THE Sistema_Agendamento SHALL verificar que a data/horário está dentro da Janela_Agendamento
5. IF alguma validação falha, THEN THE Sistema_Agendamento SHALL retornar uma mensagem de erro descritiva
6. THE Grafo_Marcar_Consulta SHALL comunicar erros de validação ao Paciente de forma clara

### Requirement 8: Fluxo Conversacional de Agendamento

**User Story:** Como paciente, quero ser guiado através do processo de agendamento, para que eu possa marcar minha consulta de forma intuitiva.

#### Acceptance Criteria

1. WHEN o Paciente inicia o fluxo de agendamento, THE Grafo_Marcar_Consulta SHALL solicitar a especialidade ou sintoma desejado
2. WHEN o Paciente fornece a especialidade, THE Grafo_Marcar_Consulta SHALL apresentar as opções encontradas
3. WHEN o Paciente seleciona uma especialidade, THE Grafo_Marcar_Consulta SHALL buscar e apresentar médicos e horários disponíveis
4. WHEN o Paciente seleciona um médico e horário, THE Grafo_Marcar_Consulta SHALL solicitar confirmação antes de criar a Consulta
5. WHEN o Paciente confirma, THE Grafo_Marcar_Consulta SHALL executar a ferramenta marcar_consulta_procedimento
6. WHEN a Consulta é criada, THE Grafo_Marcar_Consulta SHALL apresentar um resumo completo do agendamento
7. THE Grafo_Marcar_Consulta SHALL permitir que o Paciente cancele o processo a qualquer momento

### Requirement 9: Retornar Dados Estruturados para Orquestração

**User Story:** Como desenvolvedor, quero que o grafo retorne dados estruturados, para que o Python possa orquestrar transições entre grafos.

#### Acceptance Criteria

1. WHEN o agendamento é concluído com sucesso, THE Grafo_Marcar_Consulta SHALL retornar JSON com dados da consulta criada
2. THE Grafo_Marcar_Consulta SHALL retornar id_consulta, id_medico, nome_medico, especialidade, data e horário
3. WHEN o Paciente cancela o processo, THE Grafo_Marcar_Consulta SHALL retornar JSON indicando cancelamento
4. WHEN ocorre um erro, THE Grafo_Marcar_Consulta SHALL retornar JSON com mensagem de erro descritiva
5. THE Orquestrador_Python SHALL receber o retorno estruturado e decidir próxima ação (retornar ao menu, finalizar, etc)
6. THE Grafo_Marcar_Consulta SHALL NOT manter estado persistente após retornar dados ao Orquestrador_Python

### Requirement 10: Integração com Arquitetura Existente

**User Story:** Como desenvolvedor, quero que o fluxo de agendamento utilize as ferramentas e padrões existentes, para que o sistema mantenha consistência arquitetural.

#### Acceptance Criteria

1. THE Grafo_Marcar_Consulta SHALL utilizar a ferramenta consultar_especialidade_procedimento de TOOLS_MENU
2. THE Grafo_Marcar_Consulta SHALL utilizar a ferramenta consultar_agenda_disponibilidade de TOOLS_MENU
3. THE Grafo_Marcar_Consulta SHALL utilizar a ferramenta marcar_consulta_procedimento de TOOLS_MENU
4. THE Grafo_Marcar_Consulta SHALL ser invocado pelo Orquestrador_Python em src/main.py
5. THE Grafo_Marcar_Consulta SHALL receber Dados_Paciente do Orquestrador_Python após fase de menu
6. THE Sistema_Agendamento SHALL utilizar o Repository pattern para acesso ao banco de dados
7. THE Sistema_Agendamento SHALL utilizar o context manager get_session() para gerenciar transações
8. THE Grafo_Marcar_Consulta SHALL utilizar RunnableConfig com thread_id único para isolamento

### Requirement 11: Persistência de Dados

**User Story:** Como sistema, quero persistir consultas no banco de dados PostgreSQL, para que os agendamentos sejam mantidos permanentemente.

#### Acceptance Criteria

1. WHEN uma Consulta é criada, THE Sistema_Agendamento SHALL utilizar o Repository pattern para acesso ao banco
2. THE Sistema_Agendamento SHALL utilizar o context manager get_session() para gerenciar transações
3. WHEN a transação é bem-sucedida, THE Sistema_Agendamento SHALL fazer commit automático
4. IF ocorre um erro durante a persistência, THEN THE Sistema_Agendamento SHALL fazer rollback automático
5. THE Sistema_Agendamento SHALL garantir que todos os campos obrigatórios da entidade Consulta sejam preenchidos
6. THE Sistema_Agendamento SHALL utilizar as entidades SQLAlchemy existentes (Paciente, Medico, Consulta, TipoEspecialidade, DisponibilidadeMedico)

### Requirement 12: Tratamento de Conflitos de Horário

**User Story:** Como sistema, quero evitar agendamentos duplicados no mesmo horário, para que não ocorram conflitos de agenda.

#### Acceptance Criteria

1. WHEN o Sistema_Agendamento gera Slots_Disponíveis, THE Sistema_Agendamento SHALL excluir horários já ocupados por Consultas existentes
2. WHEN o Paciente tenta agendar em um horário já ocupado, THE Sistema_Agendamento SHALL retornar uma mensagem de erro
3. THE Grafo_Marcar_Consulta SHALL informar ao Paciente que o horário não está mais disponível
4. THE Grafo_Marcar_Consulta SHALL sugerir horários alternativos próximos ao horário solicitado
5. THE Sistema_Agendamento SHALL verificar conflitos antes de criar a Consulta no banco de dados

