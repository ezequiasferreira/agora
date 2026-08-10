-- ============================================================
-- ÁGORA
-- Estrutura do banco PostgreSQL do MVP
-- Database esperado: agora
-- Schema: agora
-- ============================================================

CREATE SCHEMA IF NOT EXISTS agora;


-- ============================================================
-- 1. REMUNERAÇÕES
-- ============================================================

CREATE TABLE IF NOT EXISTS agora.remuneracoes (
    id BIGSERIAL PRIMARY KEY,

    ano INTEGER NOT NULL,

    mes INTEGER NOT NULL
        CHECK (mes BETWEEN 1 AND 12),

    nome TEXT NOT NULL,

    cargo TEXT,

    lotacao TEXT,

    remuneracao_paradigma NUMERIC(14,2),

    vantagens_pessoais NUMERIC(14,2),

    subsidio_funcao_cargo_comissao NUMERIC(14,2),

    indenizacoes NUMERIC(14,2),

    vantagens_eventuais NUMERIC(14,2),

    gratificacoes NUMERIC(14,2),

    total_creditos NUMERIC(14,2),

    previdencia_publica NUMERIC(14,2),

    imposto_renda NUMERIC(14,2),

    descontos_diversos NUMERIC(14,2),

    retencao_teto NUMERIC(14,2),

    total_debitos NUMERIC(14,2),

    rendimento_liquido NUMERIC(14,2),

    remuneracao_orgao_origem NUMERIC(14,2),

    diarias NUMERIC(14,2),

    arquivo_origem TEXT,

    data_carga TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS
    idx_remuneracoes_ano_mes
ON agora.remuneracoes (
    ano,
    mes
);


CREATE INDEX IF NOT EXISTS
    idx_remuneracoes_nome
ON agora.remuneracoes (
    nome
);


-- ============================================================
-- 2. SERVIDORES / VÍNCULOS DA TLP
-- ============================================================

CREATE TABLE IF NOT EXISTS agora.servidores_tlp (
    id BIGSERIAL PRIMARY KEY,

    data_referencia DATE NOT NULL,

    grupo_tlp VARCHAR(10) NOT NULL,

    categoria_tlp TEXT NOT NULL,

    numero INTEGER,

    matricula TEXT NOT NULL,

    nome TEXT NOT NULL,

    nome_normalizado TEXT,

    lotacao TEXT,

    origem_requisitado TEXT,

    cargo_efetivo TEXT,

    cargo_comissao TEXT,

    funcao_confianca TEXT,

    efetivo BOOLEAN
        NOT NULL DEFAULT FALSE,

    efetivo_com_cargo_comissao BOOLEAN
        NOT NULL DEFAULT FALSE,

    efetivo_com_funcao_confianca BOOLEAN
        NOT NULL DEFAULT FALSE,

    requisitado BOOLEAN
        NOT NULL DEFAULT FALSE,

    requisitado_com_cargo_comissao BOOLEAN
        NOT NULL DEFAULT FALSE,

    requisitado_com_funcao_confianca BOOLEAN
        NOT NULL DEFAULT FALSE,

    exclusivamente_comissionado BOOLEAN
        NOT NULL DEFAULT FALSE,

    grau_jurisdicao TEXT,

    arquivo_origem TEXT NOT NULL,

    data_carga TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE UNIQUE INDEX IF NOT EXISTS
    uq_servidores_tlp_referencia_matricula
ON agora.servidores_tlp (
    data_referencia,
    matricula
);


CREATE INDEX IF NOT EXISTS
    idx_servidores_tlp_nome_normalizado
ON agora.servidores_tlp (
    nome_normalizado
);


CREATE INDEX IF NOT EXISTS
    idx_servidores_tlp_grupo
ON agora.servidores_tlp (
    grupo_tlp
);


-- ============================================================
-- 3. UNIDADES DA TLP
-- ============================================================

CREATE TABLE IF NOT EXISTS agora.unidades_tlp (
    id BIGSERIAL PRIMARY KEY,

    data_referencia DATE NOT NULL,

    grupo_tlp VARCHAR(10) NOT NULL,

    categoria_tlp TEXT NOT NULL,

    grau TEXT,

    tipo TEXT,

    unidade TEXT NOT NULL,

    uf TEXT,

    municipio_ibge TEXT,

    lotacao_paradigma INTEGER,

    lotacao_real_efetivos INTEGER
        NOT NULL DEFAULT 0,

    lotacao_real_requisitados INTEGER
        NOT NULL DEFAULT 0,

    lotacao_real_sem_vinculo INTEGER
        NOT NULL DEFAULT 0,

    lotacao_real_outros INTEGER
        NOT NULL DEFAULT 0,

    arquivo_origem TEXT NOT NULL,

    data_carga TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS
    idx_unidades_tlp_grupo
ON agora.unidades_tlp (
    grupo_tlp
);


CREATE INDEX IF NOT EXISTS
    idx_unidades_tlp_unidade
ON agora.unidades_tlp (
    unidade
);


-- ============================================================
-- 4. CARGOS E FUNÇÕES POR UNIDADE
-- ============================================================

CREATE TABLE IF NOT EXISTS
    agora.unidades_tlp_cargos_funcoes
(
    id BIGSERIAL PRIMARY KEY,

    unidade_tlp_id BIGINT NOT NULL
        REFERENCES agora.unidades_tlp(id)
        ON DELETE CASCADE,

    categoria TEXT NOT NULL
        CHECK (
            categoria IN (
                'CARGO_COMISSAO',
                'FUNCAO_CONFIANCA'
            )
        ),

    codigo TEXT,

    denominacao TEXT NOT NULL,

    quantidade INTEGER
        NOT NULL DEFAULT 0
);


CREATE INDEX IF NOT EXISTS
    idx_tlp_cargos_funcoes_unidade
ON agora.unidades_tlp_cargos_funcoes (
    unidade_tlp_id
);


-- ============================================================
-- 5. RUBRICAS DA FOLHA
-- ============================================================

CREATE TABLE IF NOT EXISTS agora.rubricas_folha (
    id BIGSERIAL PRIMARY KEY,

    codigo INTEGER NOT NULL UNIQUE,

    denominacao TEXT NOT NULL,

    fundamento_legal TEXT,

    arquivo_origem TEXT NOT NULL,

    data_carga TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS
    idx_rubricas_denominacao
ON agora.rubricas_folha (
    denominacao
);
