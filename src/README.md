Entidades:
Paciente (Cliente)
Clinica Medica (IA)
Funções (Menu):
1 - "Marcar Consulta ou Procedimento Médico" @tool - marcar_consulta_procedimento(dia: DateTime, id_usuario: int, id_especialidade: int, id_procedimento: int) -> {id_agenda: int; data: DateTime, id_especialidade: int; id_procedimento: int}
2 - "Desmarcar Consulta ou Procedimento Médico" @tool - desmarcar_consulta_procedimento(dia: DateTime, id_agenda)-> {sucesso:bool}
3 - "Confirmar Dia da Consulta ou Procedimento Médico" - @tool -> confirmar_consulta_procedimento(id_agenda: int) -> {sucesso:bool}
4 - "Consultar Consulta ou Procedimento Médico" @tool - consular_consulta_procedimento(dia: DateTime, id_usuario: int, id_especialidade: int, id_procedimento: int) -> {id_agenda: int; data: DateTime, id_especialidade: int; id_procedimento: int}
tools:
marcar_consulta_procedimento(dia: DateTime, id_usuario: int, id_especialidade: int, id_procedimento: int) -> {id_agenda: int; data: DateTime, id_especialidade: int; id_procedimento: int}
desmarcar_consulta_procedimento(dia: DateTime, id_agenda)-> {sucesso:bool}
confirmar_consulta_procedimento(id_agenda: int) -> {sucesso:bool}
consular_consulta_procedimento(dia: DateTime, id_usuario: int, id_especialidade: int, id_procedimento: int) -> {id_agenda: int; data: DateTime, id_especialidade: int; id_procedimento: int}
cadastrar_alterar_cliente(cpf: string, nome: string, sexo: str,
consultar_cliente
Fluxo explicado:
Grafico sereia para representar um sistema em que o paciente começa um chat com a Clinica, pode "Marcar Consulta ou Procedimento Médico", "Desmarcar Consulta ou Procedimento Médico", "Confirmar Dia da Consulta ou Procedimento Médico", "Consultar Consulta ou Procedimento Médico" para ser atendido deverá estar na base de dados como Paciente para ver isso deve chamar a função "Procurar Cliente", caso não ache o caminho é "Cadastrar Alterar Cliente" depois de cadastrado ou recuperado de "Consultar Cliente" deverá apresentar o menu de opções
