"""
Cálculos do Lucro Presumido (Lei 9.718/98, Lei 9.430/96).

Apuração trimestral:
- PIS: 0,65% sobre faturamento (cumulativo)
- COFINS: 3% sobre faturamento (cumulativo)
- IRPJ: 15% sobre base presumida + adicional 10% sobre excedente R$60k/trimestre
- CSLL: 9% sobre base presumida

Bases de presunção do IRPJ:
- 8% comércio/indústria
- 32% serviços em geral
- 16% transporte de passageiros
- 1,6% revenda de combustíveis
"""

from decimal import Decimal, ROUND_HALF_UP
from .tabelas_aliquotas import LUCRO_PRESUMIDO


def calcular_pis_cofins(faturamento_mensal):
    """Calcula PIS e COFINS no regime cumulativo (Lucro Presumido)."""
    fat = Decimal(str(faturamento_mensal))
    pis = (fat * Decimal(str(LUCRO_PRESUMIDO["pis"]["aliquota"]))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    cofins = (fat * Decimal(str(LUCRO_PRESUMIDO["cofins"]["aliquota"]))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {
        "pis": float(pis),
        "cofins": float(cofins),
        "pis_aliquota": "0,65%",
        "cofins_aliquota": "3,00%",
        "faturamento": faturamento_mensal
    }


def calcular_irpj_trimestral(faturamento_trimestral, atividade="comercio"):
    """
    Calcula IRPJ trimestral no Lucro Presumido.

    Args:
        faturamento_trimestral: Faturamento total do trimestre
        atividade: Tipo de atividade para definir base de presunção
    """
    fat = Decimal(str(faturamento_trimestral))
    bases = LUCRO_PRESUMIDO["bases_presuncao"].get(atividade, LUCRO_PRESUMIDO["bases_presuncao"]["comercio"])

    base_presuncao = Decimal(str(bases["irpj"]))
    base_calculo = (fat * base_presuncao).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    aliquota = Decimal(str(LUCRO_PRESUMIDO["irpj"]["aliquota"]))
    irpj_normal = (base_calculo * aliquota).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Adicional de 10% sobre o que exceder R$ 60.000 no trimestre
    limite = Decimal(str(LUCRO_PRESUMIDO["irpj"]["adicional_limite_trimestral"]))
    adicional = Decimal("0")
    if base_calculo > limite:
        excedente = base_calculo - limite
        adicional = (excedente * Decimal("0.10")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    irpj_total = irpj_normal + adicional

    return {
        "irpj_normal": float(irpj_normal),
        "irpj_adicional": float(adicional),
        "irpj_total": float(irpj_total),
        "base_calculo": float(base_calculo),
        "base_presuncao_percentual": f"{float(base_presuncao)*100:.0f}%",
        "faturamento_trimestral": faturamento_trimestral,
        "atividade": atividade,
        "tem_adicional": base_calculo > limite
    }


def calcular_csll_trimestral(faturamento_trimestral, atividade="comercio"):
    """Calcula CSLL trimestral no Lucro Presumido."""
    fat = Decimal(str(faturamento_trimestral))
    bases = LUCRO_PRESUMIDO["bases_presuncao"].get(atividade, LUCRO_PRESUMIDO["bases_presuncao"]["comercio"])

    base_presuncao = Decimal(str(bases["csll"]))
    base_calculo = (fat * base_presuncao).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    aliquota = Decimal(str(LUCRO_PRESUMIDO["csll"]["aliquota"]))
    csll = (base_calculo * aliquota).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return {
        "csll": float(csll),
        "base_calculo": float(base_calculo),
        "base_presuncao_percentual": f"{float(base_presuncao)*100:.0f}%",
        "aliquota": "9%",
        "faturamento_trimestral": faturamento_trimestral,
        "atividade": atividade
    }


def fechamento_trimestral(faturamentos_mensais, atividade="comercio"):
    """
    Realiza o fechamento tributário trimestral completo no Lucro Presumido.

    Args:
        faturamentos_mensais: Lista com 3 valores de faturamento (um por mês)
        atividade: Tipo de atividade

    Returns:
        dict com todos os impostos calculados
    """
    if len(faturamentos_mensais) != 3:
        raise ValueError("Deve fornecer exatamente 3 meses de faturamento para o trimestre")

    fat_trimestral = sum(faturamentos_mensais)

    # PIS e COFINS (mensal)
    pis_cofins_mensal = []
    total_pis = Decimal("0")
    total_cofins = Decimal("0")
    for i, fat in enumerate(faturamentos_mensais):
        pc = calcular_pis_cofins(fat)
        pis_cofins_mensal.append({"mes": i + 1, **pc})
        total_pis += Decimal(str(pc["pis"]))
        total_cofins += Decimal(str(pc["cofins"]))

    # IRPJ e CSLL (trimestral)
    irpj = calcular_irpj_trimestral(fat_trimestral, atividade)
    csll = calcular_csll_trimestral(fat_trimestral, atividade)

    total_impostos = total_pis + total_cofins + Decimal(str(irpj["irpj_total"])) + Decimal(str(csll["csll"]))

    return {
        "faturamento_trimestral": fat_trimestral,
        "faturamentos_mensais": faturamentos_mensais,
        "atividade": atividade,
        "pis_cofins_mensal": pis_cofins_mensal,
        "total_pis": float(total_pis),
        "total_cofins": float(total_cofins),
        "irpj": irpj,
        "csll": csll,
        "total_impostos": float(total_impostos),
        "carga_tributaria_percentual": f"{float(total_impostos / Decimal(str(fat_trimestral)) * 100):.2f}%" if fat_trimestral > 0 else "0%"
    }
