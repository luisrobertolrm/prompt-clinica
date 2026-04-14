# Especificação: Dashboard e Agenda Médica

## 1. Visão Geral
A tela de **Dashboard (Agenda)** atuará como a página inicial interativa (Home) quando o profissional médico efetuar o login. O foco central é exibir rapidamente a linha do tempo das consultas marcadas para o **dia vigente (Hoje)**, garantindo a autonomia necessária para que o médico navegue livremente pelo calendário para avaliar projeções de compromissos futuros ou consultar históricos rápidos passados.

## 2. Layout da Navbar e Controles Temporais
Para garantir uma UI rica, o topo da Dashboard (inserida dentro do `Workspace` expandido) deve possuir:

- **Cabeçalho Principal:** Título destacado informando a "Data Selecionada". Caso seja o dia atual, haverá a tag visual `Hoje` estilizada (ex: em verde).
- **Controle de Navegação (Paginador de Dias):**
  - Botão de voltar `<` (Dia anterior).
  - Ícone/Botão indicando a "Data atual", que servirá como um gatilho (*trigger*) para abrir um pequeno componente visual **Calendário (*Datepicker*)**. Isso permite ao médico "pular" para uma data distante (ex: daqui a duas semanas) sem engessamento de cliques sequenciais.
  - Botão evolver `>` (Próximo dia).
  - Botão ágil de atalho `Ir para Hoje`.
- **Estatísticas Rápidas do Dia (Topo/Lateral):** Componentes minimalistas que mostram rapidamente o status do plantão: `Total Agendado`, `Finalizados`, `Aguardando` e `Faltas`.

## 3. Listagem de Rotina (Cards Modernos)
A área central será dividida em formato de fila (*Timeline*), abrangendo janelas de tempo:

- **Slot Ocupado (Paciente Agendado):**
  - **Identificação Estética:** Nome do Paciente, ID abreviado, Convênio / Particular.
  - **Foto/Avatar:** Ícone redondo indicativo do paciente.
  - **Etiqueta de Status Variável:**
    - `Agendado` (Cinza/Neutro)
    - `Em Espera - Triagem` (Amarelo)
    - `Em Atendimento` (Azul animado)
    - `Encerrado` (Verde)
  - **Ação Principal de Foco:** Botão destacado **"Iniciar Prontuário"** ao lado de cada consulta a realizar. Ao ser pressionado, deve redirecionar instantaneamente para a tela de `Registro de Consulta (.pep)` passando informações como Nome e ID contextual daquele paciente e horário.

- **Slot Livre (Tempo Disponível):**
  - Indicadores discretos pontilhados mostrando horários vagos ou cancelados no decorrer do dia (ex: *11:00 - Agenda Livre*). Pode conter uma funcionalidade extra de "Bloquear Horário" exclusiva para uso do profissional médico.

## 4. Regras de Permissões
* **Usuário "Médico":** O painel é travado por padrão para visualizar somentes clientes/horas de si mesmo, para evitar perda de foco e erro humano. 
* **Usuário "Funcionário" (ex: Recepção):** Verá na interface superior um seletor em formato *Dropdown* (`Filtro de Médicos`), para administrar as pautas globais da clínica no mesmo formato do calendário rotativo.

## 5. Fluxo de Dados com a API (Integração)
* Espera-se que, ao trocar o dia pelos botões `<` ou `>`, o frontend Angular dipare uma requisição leve com o query param adequado para a API Python: `GET /api/consultas?data=2026-04-14&medico_id=123`.
* A reatividade nativa do Angular renderizará a lista baseada no Observable retornado.
