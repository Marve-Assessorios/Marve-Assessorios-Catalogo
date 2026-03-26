"""
Tabelas de alíquotas tributárias brasileiras.
Baseado na legislação vigente (LC 123/2006, LC 155/2016, Lei 9.718/98, Lei 9.430/96).

IMPORTANTE: Estas tabelas devem ser revisadas periodicamente pela IA para garantir
conformidade com a legislação vigente. Última atualização: Março/2026.
"""

# =============================================================================
# SIMPLES NACIONAL - Anexos I a V (LC 123/2006, atualizada pela LC 155/2016)
# =============================================================================

# Cada faixa: (limite_inferior, limite_superior, aliquota_nominal, parcela_deduzir)
# Valores em R$ para Receita Bruta acumulada nos últimos 12 meses (RBT12)

SIMPLES_ANEXO_I = {
    "descricao": "Comércio",
    "faixas": [
        {"faixa": 1, "ate": 180000.00, "aliquota": 0.04, "deduzir": 0},
        {"faixa": 2, "ate": 360000.00, "aliquota": 0.073, "deduzir": 5940.00},
        {"faixa": 3, "ate": 720000.00, "aliquota": 0.095, "deduzir": 13860.00},
        {"faixa": 4, "ate": 1800000.00, "aliquota": 0.107, "deduzir": 22500.00},
        {"faixa": 5, "ate": 3600000.00, "aliquota": 0.143, "deduzir": 87300.00},
        {"faixa": 6, "ate": 4800000.00, "aliquota": 0.19, "deduzir": 378000.00},
    ]
}

SIMPLES_ANEXO_II = {
    "descricao": "Indústria",
    "faixas": [
        {"faixa": 1, "ate": 180000.00, "aliquota": 0.045, "deduzir": 0},
        {"faixa": 2, "ate": 360000.00, "aliquota": 0.078, "deduzir": 5940.00},
        {"faixa": 3, "ate": 720000.00, "aliquota": 0.10, "deduzir": 13860.00},
        {"faixa": 4, "ate": 1800000.00, "aliquota": 0.112, "deduzir": 22500.00},
        {"faixa": 5, "ate": 3600000.00, "aliquota": 0.147, "deduzir": 85500.00},
        {"faixa": 6, "ate": 4800000.00, "aliquota": 0.30, "deduzir": 720000.00},
    ]
}

SIMPLES_ANEXO_III = {
    "descricao": "Serviços (receitas de locação de bens móveis, agências de viagem, escritórios contábeis, etc.)",
    "faixas": [
        {"faixa": 1, "ate": 180000.00, "aliquota": 0.06, "deduzir": 0},
        {"faixa": 2, "ate": 360000.00, "aliquota": 0.112, "deduzir": 9360.00},
        {"faixa": 3, "ate": 720000.00, "aliquota": 0.135, "deduzir": 17640.00},
        {"faixa": 4, "ate": 1800000.00, "aliquota": 0.16, "deduzir": 35640.00},
        {"faixa": 5, "ate": 3600000.00, "aliquota": 0.21, "deduzir": 125640.00},
        {"faixa": 6, "ate": 4800000.00, "aliquota": 0.33, "deduzir": 648000.00},
    ]
}

SIMPLES_ANEXO_IV = {
    "descricao": "Serviços (construção, vigilância, limpeza, advocacia, etc.)",
    "faixas": [
        {"faixa": 1, "ate": 180000.00, "aliquota": 0.045, "deduzir": 0},
        {"faixa": 2, "ate": 360000.00, "aliquota": 0.09, "deduzir": 8100.00},
        {"faixa": 3, "ate": 720000.00, "aliquota": 0.102, "deduzir": 12420.00},
        {"faixa": 4, "ate": 1800000.00, "aliquota": 0.14, "deduzir": 39780.00},
        {"faixa": 5, "ate": 3600000.00, "aliquota": 0.22, "deduzir": 183780.00},
        {"faixa": 6, "ate": 4800000.00, "aliquota": 0.33, "deduzir": 828000.00},
    ]
}

SIMPLES_ANEXO_V = {
    "descricao": "Serviços (engenharia, medicina, odontologia, psicologia, etc.)",
    "faixas": [
        {"faixa": 1, "ate": 180000.00, "aliquota": 0.155, "deduzir": 0},
        {"faixa": 2, "ate": 360000.00, "aliquota": 0.18, "deduzir": 4500.00},
        {"faixa": 3, "ate": 720000.00, "aliquota": 0.195, "deduzir": 9900.00},
        {"faixa": 4, "ate": 1800000.00, "aliquota": 0.205, "deduzir": 17100.00},
        {"faixa": 5, "ate": 3600000.00, "aliquota": 0.23, "deduzir": 62100.00},
        {"faixa": 6, "ate": 4800000.00, "aliquota": 0.305, "deduzir": 540000.00},
    ]
}

SIMPLES_ANEXOS = {
    "anexo_i": SIMPLES_ANEXO_I,
    "anexo_ii": SIMPLES_ANEXO_II,
    "anexo_iii": SIMPLES_ANEXO_III,
    "anexo_iv": SIMPLES_ANEXO_IV,
    "anexo_v": SIMPLES_ANEXO_V,
}

# Mapeamento atividade -> anexo
ATIVIDADE_ANEXO = {
    "comercio": "anexo_i",
    "industria": "anexo_ii",
    "servicos_anexo_iii": "anexo_iii",
    "servicos_anexo_iv": "anexo_iv",
    "servicos_anexo_v": "anexo_v",
    "servicos": "anexo_iii",  # default para serviços
}

# =============================================================================
# LUCRO PRESUMIDO - Alíquotas e Bases de Presunção
# =============================================================================

LUCRO_PRESUMIDO = {
    "pis": {"aliquota": 0.0065, "descricao": "PIS - 0,65% sobre faturamento (cumulativo)"},
    "cofins": {"aliquota": 0.03, "descricao": "COFINS - 3% sobre faturamento (cumulativo)"},
    "irpj": {
        "aliquota": 0.15,
        "adicional_aliquota": 0.10,
        "adicional_limite_trimestral": 60000.00,
        "descricao": "IRPJ - 15% sobre base presumida + 10% adicional sobre excedente R$60k/trimestre"
    },
    "csll": {
        "aliquota": 0.09,
        "descricao": "CSLL - 9% sobre base presumida"
    },
    "bases_presuncao": {
        "comercio": {"irpj": 0.08, "csll": 0.12},
        "industria": {"irpj": 0.08, "csll": 0.12},
        "servicos": {"irpj": 0.32, "csll": 0.32},
        "transporte_cargas": {"irpj": 0.08, "csll": 0.12},
        "transporte_passageiros": {"irpj": 0.16, "csll": 0.12},
        "servicos_hospitalares": {"irpj": 0.08, "csll": 0.12},
        "revenda_combustiveis": {"irpj": 0.016, "csll": 0.12},
    }
}

# =============================================================================
# LUCRO REAL - Alíquotas
# =============================================================================

LUCRO_REAL = {
    "pis": {"aliquota": 0.0165, "descricao": "PIS - 1,65% (não-cumulativo)"},
    "cofins": {"aliquota": 0.076, "descricao": "COFINS - 7,6% (não-cumulativo)"},
    "irpj": {
        "aliquota": 0.15,
        "adicional_aliquota": 0.10,
        "adicional_limite_mensal": 20000.00,
        "descricao": "IRPJ - 15% sobre lucro real + 10% adicional sobre excedente R$20k/mês"
    },
    "csll": {
        "aliquota": 0.09,
        "descricao": "CSLL - 9% sobre lucro real"
    }
}

# =============================================================================
# MEI - Valores fixos mensais do DAS-MEI
# =============================================================================

MEI = {
    "inss": {
        "percentual_salario_minimo": 0.05,
        "salario_minimo_2024": 1412.00,
        "salario_minimo_2025": 1518.00,
        "salario_minimo_2026": 1518.00,  # Atualizar quando divulgado
        "descricao": "INSS - 5% do salário mínimo"
    },
    "icms": {
        "valor": 1.00,
        "descricao": "ICMS - R$ 1,00 (comércio e indústria)"
    },
    "iss": {
        "valor": 5.00,
        "descricao": "ISS - R$ 5,00 (serviços)"
    },
    "limite_faturamento_anual": 81000.00,
    "categorias": {
        "comercio": ["inss", "icms"],
        "industria": ["inss", "icms"],
        "servicos": ["inss", "iss"],
        "comercio_e_servicos": ["inss", "icms", "iss"],
    }
}

# =============================================================================
# TABELA IRRF - Imposto de Renda Retido na Fonte (para referência)
# =============================================================================

IRRF_2024_2025 = {
    "faixas": [
        {"ate": 2259.20, "aliquota": 0, "deduzir": 0},
        {"ate": 2826.65, "aliquota": 0.075, "deduzir": 169.44},
        {"ate": 3751.05, "aliquota": 0.15, "deduzir": 381.44},
        {"ate": 4664.68, "aliquota": 0.225, "deduzir": 662.77},
        {"ate": float("inf"), "aliquota": 0.275, "deduzir": 896.00},
    ],
    "deducao_por_dependente": 189.59,
    "descricao": "Tabela IRRF vigente (atualizar conforme legislação)"
}
