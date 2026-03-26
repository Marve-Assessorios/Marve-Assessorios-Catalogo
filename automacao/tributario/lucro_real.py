"""
Cálculos do Lucro Real (Lei 9.430/96, Lei 10.637/2002, Lei 10.833/2003).

Regime não-cumulativo para PIS e COFINS.
IRPJ e CSLL calculados sobre o lucro líquido ajustado.

- PIS: 1,65% (não-cumulativo, com créditos)
- COFINS: 7,6% (não-cumulativo, com créditos)
- IRPJ: 15% sobre lucro real + adicional 10% sobre excedente R$20k/mês
- CSLL: 9% sobre lucro real (base ajustada)
"""

from decimal import Decimal, ROUND_HALF_UP
from .tabelas_aliquotas import LUCRO_REAL


def calcular_pis_cofins(receita_bruta, creditos_pis=0, creditos_cofins=0):
    """
    Calcula PIS e COFINS no regime não-cumulativo (Lucro Real).

    Args:
        receita_bruta: Receita bruta mensal
        creditos_pis: Créditos de PIS a compensar (insumos, etc.)
        creditos_cofins: Créditos de COFINS a compensar
    """
    receita = Decimal(str(receita_bruta))

    pis_bruto = (receita * Decimal(str(LUCRO_REAL["pis"]["aliquota"]))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    cofins_bruto = (receita * Decimal(str(LUCRO_REAL["cofins"]["aliquota"]))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    pis_credito = Decimal(str(creditos_pis)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    cofins_credito = Decimal(str(creditos_cofins)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    pis_liquido = max(Decimal("0"), pis_bruto - pis_credito)
    cofins_liquido = max(Decimal("0"), cofins_bruto - cofins_credito)

    return {
        "pis_bruto": float(pis_bruto),
        "pis_creditos": float(pis_credito),
        "pis_a_pagar": float(pis_liquido),
        "cofins_bruto": float(cofins_bruto),
        "cofins_creditos": float(cofins_credito),
        "cofins_a_pagar": float(cofins_liquido),
        "pis_aliquota": "1,65%",
        "cofins_aliquota": "7,60%",
        "receita_bruta": receita_bruta
    }


def calcular_irpj(lucro_real_periodo, num_meses=1):
    """
    Calcula IRPJ sobre o lucro real.

    Args:
        lucro_real_periodo: Lucro líquido ajustado do período
        num_meses: Número de meses do período (1 para mensal, 3 para trimestral)
    """
    lucro = Decimal(str(lucro_real_periodo))

    if lucro <= 0:
        return {
            "irpj_normal": 0,
            "irpj_adicional": 0,
            "irpj_total": 0,
            "base_calculo": float(lucro),
            "prejuizo": True,
            "detalhes": "Prejuízo no período - sem IRPJ a pagar. Prejuízo pode ser compensado em períodos futuros (limite: 30% do lucro)."
        }

    aliquota = Decimal(str(LUCRO_REAL["irpj"]["aliquota"]))
    irpj_normal = (lucro * aliquota).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Adicional: 10% sobre lucro que exceder R$20.000/mês
    limite_mensal = Decimal(str(LUCRO_REAL["irpj"]["adicional_limite_mensal"]))
    limite_periodo = limite_mensal * num_meses
    adicional = Decimal("0")
    if lucro > limite_periodo:
        excedente = lucro - limite_periodo
        adicional = (excedente * Decimal("0.10")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    irpj_total = irpj_normal + adicional

    return {
        "irpj_normal": float(irpj_normal),
        "irpj_adicional": float(adicional),
        "irpj_total": float(irpj_total),
        "base_calculo": float(lucro),
        "limite_adicional": float(limite_periodo),
        "tem_adicional": lucro > limite_periodo,
        "prejuizo": False
    }


def calcular_csll(lucro_real_periodo):
    """Calcula CSLL sobre o lucro real."""
    lucro = Decimal(str(lucro_real_periodo))

    if lucro <= 0:
        return {
            "csll": 0,
            "base_calculo": float(lucro),
            "prejuizo": True,
            "detalhes": "Prejuízo no período - sem CSLL a pagar."
        }

    aliquota = Decimal(str(LUCRO_REAL["csll"]["aliquota"]))
    csll = (lucro * aliquota).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return {
        "csll": float(csll),
        "base_calculo": float(lucro),
        "aliquota": "9%",
        "prejuizo": False
    }


def fechamento_mensal(receita_bruta, despesas_dedutiveis, creditos_pis=0, creditos_cofins=0,
                      adicoes_lalur=0, exclusoes_lalur=0, compensacao_prejuizo=0):
    """
    Realiza o fechamento tributário mensal completo no Lucro Real.

    Args:
        receita_bruta: Receita bruta do mês
        despesas_dedutiveis: Total de despesas dedutíveis
        creditos_pis: Créditos de PIS a compensar
        creditos_cofins: Créditos de COFINS a compensar
        adicoes_lalur: Adições ao LALUR (despesas não dedutíveis, etc.)
        exclusoes_lalur: Exclusões do LALUR (receitas não tributáveis, etc.)
        compensacao_prejuizo: Compensação de prejuízos acumulados (máx 30% do lucro)
    """
    receita = Decimal(str(receita_bruta))
    despesas = Decimal(str(despesas_dedutiveis))

    # Lucro contábil
    lucro_contabil = receita - despesas

    # Ajustes do LALUR (Livro de Apuração do Lucro Real)
    lucro_real = lucro_contabil + Decimal(str(adicoes_lalur)) - Decimal(str(exclusoes_lalur))

    # Compensação de prejuízos (máximo 30% do lucro)
    comp_prejuizo = Decimal(str(compensacao_prejuizo))
    if lucro_real > 0 and comp_prejuizo > 0:
        limite_compensacao = lucro_real * Decimal("0.30")
        comp_prejuizo = min(comp_prejuizo, limite_compensacao)
        lucro_real -= comp_prejuizo

    # Cálculos
    pis_cofins = calcular_pis_cofins(receita_bruta, creditos_pis, creditos_cofins)
    irpj = calcular_irpj(float(lucro_real), num_meses=1)
    csll = calcular_csll(float(lucro_real))

    total_impostos = (
        Decimal(str(pis_cofins["pis_a_pagar"])) +
        Decimal(str(pis_cofins["cofins_a_pagar"])) +
        Decimal(str(irpj["irpj_total"])) +
        Decimal(str(csll["csll"]))
    )

    return {
        "receita_bruta": receita_bruta,
        "despesas_dedutiveis": despesas_dedutiveis,
        "lucro_contabil": float(lucro_contabil),
        "adicoes_lalur": adicoes_lalur,
        "exclusoes_lalur": exclusoes_lalur,
        "compensacao_prejuizo": float(comp_prejuizo),
        "lucro_real": float(lucro_real),
        "pis_cofins": pis_cofins,
        "irpj": irpj,
        "csll": csll,
        "total_impostos": float(total_impostos),
        "carga_tributaria_percentual": f"{float(total_impostos / receita * 100):.2f}%" if receita > 0 else "0%"
    }
