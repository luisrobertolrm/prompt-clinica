# Clínica Médica - Ferramentas

## Entidades

- Paciente (Cliente)
- Clínica Médica (IA)

## Menu rápido

1. Marcar Consulta ou Procedimento Médico
2. Desmarcar Consulta ou Procedimento Médico
3. Confirmar Dia da Consulta ou Procedimento Médico
4. Consultar Consulta ou Procedimento Médico

## Tools

| Nome                                 | Parâmetros                                                                                          | Retorno                                                                         | Descrição                                   |
| ------------------------------------ | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------- |
| marcar_consulta_procedimento         | dia: DateTime; id_especialidade: int; id_procedimento: int                                          | {id_agenda: int; data: DateTime; id_especialidade: int; id_procedimento: int}   | Marca um procedimento para o paciente.      |
| desmarcar_consulta_procedimento      | dia: DateTime; id_agenda: int                                                                       | {sucesso: bool}                                                                 | Cancela uma agenda existente.               |
| confirmar_consulta_procedimento      | id_agenda: int                                                                                      | {sucesso: bool}                                                                 | Confirma uma agenda pelo id.                |
| consular_consulta_procedimento       | dia: DateTime \| None; id_usuario: int; id_especialidade: int \| None; id_procedimento: int \| None | [{id_agenda: int; data: DateTime; id_especialidade: int; id_procedimento: int}] | Lista agendas disponíveis conforme filtros. |
| cadastrar_alterar_cliente            | cpf: string; nome: string; sexo: str                                                                | {cpf: string; nome: string; rg: string; id_usuario: int}                        | Cadastra ou altera dados de cliente.        |
| consultar_cliente                    | cpf: string                                                                                         | {cpf: string; nome: string; rg: string; id_usuario: int} \| None                | Busca cliente pelo CPF.                     |
| consultar_especialidade_procedimento | especialidade: string                                                                               | [{id_especialidade: int; nome: string}]                                         | Lista especialidades/procedimentos.         |

## Fluxo resumido

- Paciente inicia chat e informa CPF.
- Se não existir, segue para cadastro/alteração; caso exista, apresenta menu.
- Escolhe ação: marcar, desmarcar, confirmar ou consultar consultas/procedimentos.
- Após cada ação, pode encerrar ou voltar ao menu.

## Diagramas

- Ver fluxo detalhado em fluxo.mermaid.
