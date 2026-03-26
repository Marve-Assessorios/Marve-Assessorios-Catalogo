"""
Base de conhecimento sobre legislação tributária brasileira.
Este módulo serve como referência para a IA interpretar e aplicar a legislação.

IMPORTANTE: A IA deve consultar fontes oficiais (Receita Federal, Planalto.gov.br)
para verificar atualizações na legislação. Este módulo contém um resumo para referência rápida.
"""

LEGISLACAO = {
    "simples_nacional": {
        "base_legal": "Lei Complementar 123/2006, atualizada pela LC 155/2016",
        "orgao": "Receita Federal do Brasil (RFB)",
        "periodicidade": "Mensal (DAS)",
        "limite_faturamento": "R$ 4.800.000,00/ano",
        "sublimite_icms_iss": "R$ 3.600.000,00/ano (para ICMS e ISS em estados que adotam sublimite)",
        "regras_principais": [
            "Recolhimento unificado via DAS (Documento de Arrecadação do Simples)",
            "Alíquota progressiva baseada na RBT12 (Receita Bruta dos últimos 12 meses)",
            "5 Anexos com faixas de tributação diferenciadas por atividade",
            "Fator R (folha de pagamento/receita bruta): se >= 28%, serviços do Anexo V migram para Anexo III",
            "Sublimite estadual de R$ 3,6M para ICMS/ISS em alguns estados",
            "Empresa excluída se ultrapassar R$ 4,8M no ano-calendário"
        ],
        "obrigacoes_acessorias": [
            "DASN-SIMEI (declaração anual, para MEI)",
            "DEFIS - Declaração de Informações Socioeconômicas e Fiscais",
            "PGDAS-D - Programa Gerador do DAS (cálculo e emissão mensal)"
        ],
        "prazos": {
            "pagamento_das": "Dia 20 do mês subsequente",
            "defis": "Até 31 de março do ano seguinte",
            "opcao_simples": "Até o último dia útil de janeiro"
        }
    },

    "lucro_presumido": {
        "base_legal": "Lei 9.718/98, Lei 9.430/96, RIR/2018 (Decreto 9.580/2018)",
        "orgao": "Receita Federal do Brasil (RFB)",
        "periodicidade": "PIS/COFINS mensal, IRPJ/CSLL trimestral",
        "limite_faturamento": "R$ 78.000.000,00/ano",
        "regras_principais": [
            "PIS (0,65%) e COFINS (3%) cumulativos sobre faturamento mensal",
            "IRPJ: 15% sobre base presumida + adicional 10% sobre excedente de R$ 60k/trimestre",
            "CSLL: 9% sobre base presumida",
            "Base de presunção do IRPJ varia conforme atividade (8% comércio, 32% serviços)",
            "Base de presunção da CSLL: 12% comércio, 32% serviços",
            "Trimestres: Jan-Mar, Abr-Jun, Jul-Set, Out-Dez",
            "Opção irretratável para todo o ano-calendário"
        ],
        "prazos": {
            "pis_cofins": "Dia 25 do mês subsequente",
            "irpj_csll": "Último dia útil do mês subsequente ao trimestre",
            "dctf": "15º dia útil do 2º mês subsequente"
        }
    },

    "lucro_real": {
        "base_legal": "Lei 9.430/96, Lei 10.637/2002, Lei 10.833/2003, RIR/2018",
        "orgao": "Receita Federal do Brasil (RFB)",
        "periodicidade": "Mensal (estimativa) ou Trimestral (definitivo)",
        "obrigatorio_para": [
            "Receita bruta superior a R$ 78 milhões/ano",
            "Instituições financeiras",
            "Empresas com lucros no exterior",
            "Empresas que usufruem de benefícios fiscais"
        ],
        "regras_principais": [
            "PIS (1,65%) e COFINS (7,6%) não-cumulativos com direito a créditos",
            "IRPJ: 15% sobre lucro real + adicional 10% sobre excedente R$ 20k/mês",
            "CSLL: 9% sobre base de cálculo ajustada",
            "Lucro Real = Lucro Contábil ± Ajustes do LALUR",
            "LALUR: Livro de Apuração do Lucro Real (adições e exclusões)",
            "Compensação de prejuízos fiscais: limite de 30% do lucro do período",
            "Pode optar por apuração trimestral (definitiva) ou anual (estimativas mensais)"
        ],
        "prazos": {
            "pis_cofins": "Dia 25 do mês subsequente",
            "irpj_csll_trimestral": "Último dia útil do mês subsequente ao trimestre",
            "irpj_csll_estimativa": "Último dia útil do mês subsequente",
            "ecf": "Último dia útil de julho do ano seguinte",
            "ecd": "Último dia útil de maio do ano seguinte"
        }
    },

    "mei": {
        "base_legal": "Lei Complementar 123/2006 (arts. 18-A a 18-E)",
        "orgao": "Receita Federal do Brasil (RFB) / Portal do Empreendedor",
        "periodicidade": "Mensal (DAS-MEI fixo)",
        "limite_faturamento": "R$ 81.000,00/ano",
        "regras_principais": [
            "Valor fixo mensal: INSS (5% do salário mínimo) + ICMS (R$1) e/ou ISS (R$5)",
            "Máximo 1 empregado com salário mínimo ou piso da categoria",
            "Não pode ser sócio ou titular de outra empresa",
            "Atividades permitidas conforme lista da Resolução CGSN",
            "Se exceder até 20% do limite: recolhe diferença + multa, desenquadra no ano seguinte",
            "Se exceder mais de 20%: desenquadramento retroativo ao início do ano",
            "Emite NFA-e (Nota Fiscal Avulsa Eletrônica) ou NFS-e pelo Portal Nacional"
        ],
        "obrigacoes_acessorias": [
            "DASN-SIMEI até 31 de maio do ano seguinte",
            "Relatório Mensal de Receitas Brutas"
        ],
        "prazos": {
            "pagamento_das": "Dia 20 do mês subsequente",
            "dasn_simei": "Até 31 de maio do ano seguinte"
        }
    },

    "obrigacoes_gerais": {
        "sped": {
            "descricao": "Sistema Público de Escrituração Digital",
            "componentes": [
                "ECD - Escrituração Contábil Digital",
                "ECF - Escrituração Contábil Fiscal",
                "EFD-Contribuições (PIS/COFINS)",
                "EFD-ICMS/IPI",
                "EFD-Reinf (Retenções e outras informações fiscais)",
                "e-Social (obrigações trabalhistas)"
            ]
        },
        "notas_fiscais": {
            "nfe": "Nota Fiscal Eletrônica (mercadorias)",
            "nfse": "Nota Fiscal de Serviços Eletrônica",
            "nfce": "Nota Fiscal ao Consumidor Eletrônica"
        }
    },

    "atualizacoes_recentes": [
        {
            "data": "2024",
            "descricao": "Reforma Tributária (EC 132/2023): Transição para IBS e CBS no consumo. Implementação gradual de 2026 a 2033.",
            "impacto": "Substituição gradual de PIS, COFINS, IPI, ICMS e ISS por IBS e CBS. Alíquota de referência estimada em 26,5%."
        },
        {
            "data": "2025",
            "descricao": "Novo salário mínimo: R$ 1.518,00. Início da fase de testes do IBS/CBS.",
            "impacto": "Atualiza cálculos do MEI (INSS) e tabela do IRRF."
        }
    ],

    "fontes_oficiais": [
        "https://www.gov.br/receitafederal - Receita Federal",
        "https://www.planalto.gov.br - Legislação Federal",
        "http://www8.receita.fazenda.gov.br/SimplesNacional - Portal do Simples Nacional",
        "https://www.gov.br/empresas-e-negocios/pt-br/empreendedor - Portal do Empreendedor (MEI)"
    ]
}


def consultar_legislacao(regime):
    """Retorna informações da legislação para o regime informado."""
    return LEGISLACAO.get(regime, {"erro": f"Regime '{regime}' não encontrado"})


def listar_prazos(regime):
    """Lista os prazos de entrega/pagamento para o regime."""
    leg = LEGISLACAO.get(regime, {})
    return leg.get("prazos", {})


def verificar_atualizacoes():
    """Retorna lista de atualizações recentes na legislação."""
    return LEGISLACAO.get("atualizacoes_recentes", [])


def resumo_regime(regime):
    """Gera um resumo textual sobre o regime tributário."""
    leg = LEGISLACAO.get(regime)
    if not leg:
        return f"Regime '{regime}' não encontrado."

    linhas = [
        f"REGIME: {regime.upper().replace('_', ' ')}",
        f"Base Legal: {leg.get('base_legal', 'N/A')}",
        f"Periodicidade: {leg.get('periodicidade', 'N/A')}",
        "",
        "Regras Principais:",
    ]
    for regra in leg.get("regras_principais", []):
        linhas.append(f"  - {regra}")

    linhas.append("\nPrazos:")
    for chave, prazo in leg.get("prazos", {}).items():
        linhas.append(f"  - {chave.replace('_', ' ').title()}: {prazo}")

    return "\n".join(linhas)
