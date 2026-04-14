# Especificações do Projeto Angular - Clínica Multi Med

## 1. Visão Geral e Estrutura de Áreas
A plataforma clínica "Multi Med" foi arquitetada para ser segmentada em duas grandes áreas para garantir isolamento e performance:
- **Área Externa (Pública):** Páginas acessíveis sem autenticação, vitrine da clínica e informações de contato.
- **Área Interna (Privada):** Acesso restrito com autenticação, contendo o sistema e interfaces segmentadas em três perfis: `Médicos`, `Funcionários` `Pacientes`.

## 2. Autenticação (Tela de Login)
- **Acesso Base:** Formulário tradicional requerendo `Usuário/Email` e `Senha`.
- **Acesso Alternativo (SSO):** Opção de `Continuar com o Google` para facilitar o fluxo de login dos usuários.
- **Roteamento Inteligente:** Com base no token, o login fará o redirecionamento imediato para a página principal baseada no nível de permissão.

## 3. Estrutura do Layout (Workspace e Menu Responsivo)
O sistema deve aproveitar ao máximo o espaço de tela do dispositivo. Componentes fixos e extensíveis dão forma ao layout:

### 3.1 Top Bar (Barra Superior)
- Mantida fixa para reter contexto.
- Lado esquerdo abriga o nome da clínica ("**Multi Med**").
- Lado direito exibe: Avatar/Foto do usuário, Nome completo, Especialidade Médica (visível apenas para perfil médico) e um link simples e direto para "Sair".

### 3.2 Menu de Navegação Flexível
- Pode ser lateral retrátil ou superior.
- Carregado exclusivamente de forma dinâmica via array JSON:
```json
[
  {
    "titulo": "Dashboard",
    "icone": "dashboard",
    "rota": "/painel",
    "visivelMobile": true,
    "perfis": ["medico", "funcionario"]
  },
  {
    "titulo": "Atendimento (Prontuário)",
    "icone": "stethoscope",
    "rota": "/pep",
    "visivelMobile": false,
    "perfis": ["medico"]
  }
]
```
- A chave `visivelMobile` oculta o item de menu automaticamente nos breakpoints de dispositivos menores, adaptando para rotinas complexas que só funcionam em monitores normais.

## 4. Tela de Registro de Consulta Médica (Prontuário/PEP)
Em conformidade com a especificação inteligente (React/Tailwind descrita previamente), a migração em Angular usará os seguintes pilares:
- **Foco em Compliance:** Cabeçalho da consulta trazendo os dados do médico logado (CRM) e identificador único do paciente (LGPD).
- **Transcrição e Textarea:** Integração com microfone e API de reconhecimento de voz. Botão para acionar e interromper a captação do áudio (ícone animado enquanto ativo).
- **Sugestões via IA:** Painel contendo insights (doenças suspeitas, CID sugerido, detecção de sintomas do texto bruto e prescrição de exames). Tudo visivelmente padronizado via cores (Azul, Laranja, Verde).
- **Rodapé e Ações Finais:** Botões para encerramento ("Assinar e Salvar no PEP", com estado *loading* ou desabilitado caso não haja conteúdo principal).
