"""
Cálculos do Simples Nacional (LC 123/2006, atualizada pela LC 155/2016).

Fórmula da alíquota efetiva:
  Alíquota Efetiva = (RBT12 × Alíquota Nominal - Parcela a Deduzir) / RBT12

Onde:
  RBT12 = Receita Bruta Total acumulada nos 12 meses anteriores ao período de apuração
"""

from decimal import Decimal, ROUND_HALF_UP
from .tabelas_aliquotas import SIMPLES_ANEXOS, ATIVIDADE_ANEXO


def obter_anexo(atividade):
    """Retorna o anexo do Simples Nacional para a atividade informada."""
    chave = ATIVIDADE_ANEXO.get(atividade, "anexo_i")
    return SIMPLES_ANEXOS[chave]


def obter_faixa(rbt12, anexo):
    """Identifica a faixa de tributação com base na RBT12."""
    for faixa in anexo["faixas"]:
        if rbt12 <= faixa["ate"]:
            return faixa
    return anexo["faixas"][-1]


def calcular_aliquota_efetiva(rbt12, atividade="comercio"):
    """
    Calcula a alíquota efetiva do Simples Nacional.

    Args:
        rbt12: Receita Bruta Total dos últimos 12 meses
        atividade: Tipo de atividade (comercio, industria, servicos, etc.)

    Returns:
        dict com aliquota_efetiva, faixa, anexo e detalhes
    """
    if rbt12 <= 0:
        return {
            "aliquota_efetiva": Decimal("0"),
            "faixa": 0,
            "anexo": atividade,
            "detalhes": "Sem faturamento no período"
        }

    if rbt12 > 4800000:
        return {
            "aliquota_efetiva": None,
            "faixa": 0,
            "anexo": atividade,
            "detalhes": "EXCEDEU LIMITE DO SIMPLES NACIONAL (R$ 4.800.000,00). Empresa deve migrar para outro regime."
        }

    anexo = obter_anexo(atividade)
    faixa = obter_faixa(rbt12, anexo)

    rbt12_dec = Decimal(str(rbt12))
    aliquota = Decimal(str(faixa["aliquota"]))
    deduzir = Decimal(str(faixa["deduzir"]))

    aliquota_efetiva = (rbt12_dec * aliquota - deduzir) / rbt12_dec
    aliquota_efetiva = aliquota_efetiva.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)

    return {
        "aliquota_efetiva": float(aliquota_efetiva),
        "aliquota_nominal": faixa["aliquota"],
        "parcela_deduzir": faixa["deduzir"],
        "faixa": faixa["faixa"],
        "anexo": anexo["descricao"],
        "rbt12": rbt12,
        "detalhes": f"Anexo: {anexo['descricao']} | Faixa {faixa['faixa']} | Alíquota Nominal: {faixa['aliquota']*100:.1f}%"
    }


def calcular_das(receita_mensal, rbt12, atividade="comercio"):
    """
    Calcula o valor do DAS (Documento de Arrecadação do Simples Nacional).

    Args:
        receita_mensal: Receita bruta do mês de apuração
        rbt12: Receita Bruta Total dos últimos 12 meses
        atividade: Tipo de atividade

    Returns:
        dict com valor_das, aliquota_efetiva e detalhes
    """
    resultado = calcular_aliquota_efetiva(rbt12, atividade)

    if resultado["aliquota_efetiva"] is None:
        return {
            "valor_das": None,
            "aliquota_efetiva": None,
            "receita_mensal": receita_mensal,
            "detalhes": resultado["detalhes"]
        }

    receita_dec = Decimal(str(receita_mensal))
    aliq_efetiva = Decimal(str(resultado["aliquota_efetiva"]))
    valor_das = (receita_dec * aliq_efetiva).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return {
        "valor_das": float(valor_das),
        "aliquota_efetiva": resultado["aliquota_efetiva"],
        "aliquota_efetiva_percentual": f"{resultado['aliquota_efetiva']*100:.4f}%",
        "receita_mensal": receita_mensal,
        "rbt12": rbt12,
        "faixa": resultado["faixa"],
        "anexo": resultado["anexo"],
        "detalhes": resultado["detalhes"]
    }


def simular_simples_anual(faturamento_mensal_lista, atividade="comercio"):
    """
    Simula o Simples Nacional para 12 meses.

    Args:
        faturamento_mensal_lista: Lista com 12 valores de faturamento mensal
        atividade: Tipo de atividade

    Returns:
        dict com resumo anual e detalhamento mensal
    """
    if len(faturamento_mensal_lista) != 12:
        raise ValueError("Deve fornecer exatamente 12 meses de faturamento")

    resultado_mensal = []
    total_das = Decimal("0")
    total_faturamento = Decimal("0")

    for mes_idx, faturamento in enumerate(faturamento_mensal_lista):
        # RBT12 = soma dos 12 meses anteriores (para simplicidade, usando o acumulado até o mês)
        if mes_idx == 0:
            rbt12 = sum(faturamento_mensal_lista)  # estimativa inicial
        else:
            rbt12 = sum(faturamento_mensal_lista[:mes_idx]) + sum(faturamento_mensal_lista[mes_idx:])

        das = calcular_das(faturamento, rbt12, atividade)
        resultado_mensal.append({
            "mes": mes_idx + 1,
            "faturamento": faturamento,
            **das
        })

        if das["valor_das"] is not None:
            total_das += Decimal(str(das["valor_das"]))
        total_faturamento += Decimal(str(faturamento))

    return {
        "total_faturamento": float(total_faturamento),
        "total_das": float(total_das),
        "carga_tributaria_media": float(total_das / total_faturamento * 100) if total_faturamento > 0 else 0,
        "atividade": atividade,
        "meses": resultado_mensal
    }
