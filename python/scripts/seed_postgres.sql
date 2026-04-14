-- Seed inicial para testes locais (PostgreSQL)
-- Execute com: psql -d <database> -f scripts/seed_postgres.sql

BEGIN;

-- Limpa tabelas na ordem reversa para evitar FK
TRUNCATE disponibilidade_medico, medico_procedimento, procedimento, tipo_procedimento,
         medico_especialidade, consulta, tipo_especialidade,
         medico, paciente, telefone, documento, pessoa
         RESTART IDENTITY CASCADE;

-- Pessoas (médicos e um paciente genérico)
INSERT INTO pessoa (nome, data_nascimento, sexo, cpf, email) VALUES
    ('Dra. Ana Santos', '1980-03-12', 'F', '12345678901', 'ana.santos@exemplo.com'),
    ('Dr. Bruno Costa', '1975-07-22', 'M', '23456789012', 'bruno.costa@exemplo.com'),
    ('Paciente Teste', '1990-05-01', 'M', '34567890123', 'paciente@exemplo.com');

-- Médicos (id manual, mas id_pessoa vindo do insert anterior)
INSERT INTO medico (id, crm, uf_crm, data_criacao, id_pessoa)
VALUES
    (1, '12345', 'SP', NOW(), (SELECT id FROM pessoa WHERE cpf = '12345678901')),
    (2, '67890', 'RJ', NOW(), (SELECT id FROM pessoa WHERE cpf = '23456789012'));

-- Paciente usa o id_pessoa (não é identity)
INSERT INTO paciente (id_pessoa, ativo)
VALUES ((SELECT id FROM pessoa WHERE cpf = '34567890123'), TRUE);

-- Tipos de especialidade (ids gerados pelo IDENTITY)
INSERT INTO tipo_especialidade (descricao, duracao_consulta_padrao, embedding) VALUES
    ('Cardiologia', 40, NULL),
    ('Dermatologia', 30, NULL);

-- Especialidades por médico
INSERT INTO medico_especialidade (id_medico, id_tipo_especialidade, duracao_consulta, data_criacao, data_inativacao)
VALUES
    (1, (SELECT id FROM tipo_especialidade WHERE descricao = 'Cardiologia'), 40, NOW(), NULL),
    (2, (SELECT id FROM tipo_especialidade WHERE descricao = 'Dermatologia'), 30, NOW(), NULL);

-- Tipos de procedimento (ids gerados pelo IDENTITY)
INSERT INTO tipo_procedimento (descricao, embedding) VALUES
    ('Eletrocardiograma', NULL),
    ('Biopsia de Pele', NULL);

-- Procedimentos atendidos por médico
INSERT INTO medico_procedimento (id_medico, id_tipo_procedimento, data) VALUES
    (1, (SELECT id FROM tipo_procedimento WHERE descricao = 'Eletrocardiograma'), '2024-01-10'),
    (2, (SELECT id FROM tipo_procedimento WHERE descricao = 'Biopsia de Pele'), '2024-01-11');

-- Disponibilidade de médicos (status: 0=LIVRE, 1=OCUPADO, 2=BLOQUEADO)
INSERT INTO disponibilidade_medico (id_medico, data_inicio, data_fim, hora_inicio, hora_fim, dia_semana, status) VALUES
    (1, '2024-02-01', '2024-02-28', '08:00:00', '12:00:00', 1, 0),
    (1, '2024-02-01', '2024-02-28', '13:00:00', '17:00:00', 3, 1),
    (2, '2024-02-01', '2024-02-28', '09:00:00', '15:00:00', 2, 0);

COMMIT;
