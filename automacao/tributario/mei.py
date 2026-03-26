"""
Cálculos do MEI - Microempreendedor Individual.

O MEI paga um valor fixo mensal (DAS-MEI) composto por:
- INSS: 5% do salário mínimo vigente
- ICMS: R$ 1,00 (se atividade de comércio ou indústria)
- ISS: R$ 5,00 (se atividade de serviço)

Limite de faturamento anual: R$ 81.000,00
"""

from decimal import Decimal, ROUND_HALF_UP
from .tabelas_aliquotas import MEI


def obter_salario_minimo(ano=2026):
    """Retorna o salário mínimo do ano informado."""
    chave = f"salario_minimo_{ano}"
    return MEI["inss"].get(chave, MEI["inss"]["salario_minimo_2026"])


def calcular_das_mei(categoria="comercio", ano=2026):
    """
    Calcula o DAS-MEI mensal fixo.

    Args:
        categoria: comercio, industria, servicos, comercio_e_servicos
        ano: Ano para pegar o salário mínimo correto

    Returns:
        dict com detalhamento do DAS-MEI
    """
    salario_minimo = Decimal(str(obter_salario_minimo(ano)))
    percentual_inss = Decimal(str(MEI["inss"]["percentual_salario_minimo"]))

    inss = (salario_minimo * percentual_inss).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    componentes = MEI["categorias"].get(categoria, MEI["categorias"]["comercio"])

    icms = Decimal(str(MEI["icms"]["valor"])) if "icms" in componentes else Decimal("0")
    iss = Decimal(str(MEI["iss"]["valor"])) if "iss" in componentes else Decimal("0")

    total = inss + icms + iss

    return {
        "das_mei_total": float(total),
        "inss": float(inss),
        "icms": float(icms),
        "iss": float(iss),
        "salario_minimo": float(salario_minimo),
        "categoria": categoria,
        "ano": ano,
        "detalhes": {
            "inss": f"5% de R$ {salario_minimo} = R$ {inss}",
            "icms": f"R$ {icms}" if icms > 0 else "Não aplicável",
            "iss": f"R$ {iss}" if iss > 0 else "Não aplicável"
        }
    }


def verificar_limite_faturamento(faturamento_acumulado, mes_atual=12):
    """
    Verifica se o MEI está dentro do limite de faturamento anual.

    Args:
        faturamento_acumulado: Faturamento acumulado no ano
        mes_atual: Mês atual (para cálculo proporcional se início no meio do ano)

    Returns:
        dict com status e alertas
    """
    limite = Decimal(str(MEI["limite_faturamento_anual"]))
    fat = Decimal(str(faturamento_acumulado))

    # Média mensal permitida
    media_mensal_limite = limite / 12
    media_mensal_atual = fat / mes_atual if mes_atual > 0 else Decimal("0")

    # Projeção anual
    projecao_anual = media_mensal_atual * 12

    excedeu = fat > limite
    excedeu_20 = fat > limite * Decimal("1.20")

    if excedeu_20:
        status = "EXCEDEU_20_PORCENTO"
        alerta = "ATENÇÃO: Faturamento excedeu 20% do limite! Desenquadramento RETROATIVO ao início do ano. Deve migrar para ME/EPP."
    elif excedeu:
        status = "EXCEDEU"
        alerta = "ATENÇÃO: Faturamento excedeu o limite! Deve recolher DAS complementar sobre o excedente e será desenquadrado a partir do ano seguinte."
    elif projecao_anual > limite * Decimal("0.80"):
        status = "ALERTA"
        alerta = f"ALERTA: Projeção anual de R$ {projecao_anual:.2f} está próxima do limite. Monitore o faturamento."
    else:
        status = "OK"
        alerta = "Faturamento dentro do limite."

    return {
        "faturamento_acumulado": float(fat),
        "limite_anual": float(limite),
        "percentual_utilizado": f"{float(fat / limite * 100):.1f}%",
        "media_mensal_atual": float(media_mensal_atual),
        "projecao_anual": float(projecao_anual),
        "status": status,
        "alerta": alerta,
        "meses_informados": mes_atual
    }


def fechamento_mensal_mei(faturamento_mes, faturamento_acumulado_ano, categoria="comercio",
                          mes_atual=1, ano=2026):
    """
    Realiza o fechamento mensal do MEI.

    Args:
        faturamento_mes: Faturamento do mês
        faturamento_acumulado_ano: Faturamento acumulado no ano
        categoria: Tipo de atividade
        mes_atual: Número do mês (1-12)
        ano: Ano fiscal
    """
    das = calcular_das_mei(categoria, ano)
    limite = verificar_limite_faturamento(faturamento_acumulado_ano, mes_atual)

    return {
        "mes": mes_atual,
        "ano": ano,
        "faturamento_mes": faturamento_mes,
        "das_mei": das,
        "limite_faturamento": limite,
        "valor_a_pagar": das["das_mei_total"],
        "resumo": f"DAS-MEI: R$ {das['das_mei_total']:.2f} | Faturamento: R$ {faturamento_mes:.2f} | {limite['status']}"
    }
