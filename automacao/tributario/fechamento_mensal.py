"""
Fechamento tributário mensal unificado.
Detecta o regime da empresa e executa os cálculos apropriados.
"""

from datetime import datetime, date
from decimal import Decimal
from ..config import carregar_config_empresa, carregar_transacoes
from ..utils.formatadores import formatar_moeda, formatar_data
from . import simples_nacional, lucro_presumido, lucro_real, mei


def obter_faturamento_periodo(transacoes, mes, ano):
    """Calcula o faturamento de um mês específico a partir das transações."""
    total = Decimal("0")
    for t in transacoes.get("transacoes", []):
        if t["tipo"] == "receita":
            data_t = datetime.strptime(t["data"], "%Y-%m-%d").date()
            if data_t.month == mes and data_t.year == ano:
                total += Decimal(str(t["valor"]))
    return float(total)


def obter_despesas_periodo(transacoes, mes, ano):
    """Calcula as despesas de um mês específico."""
    total = Decimal("0")
    for t in transacoes.get("transacoes", []):
        if t["tipo"] == "despesa":
            data_t = datetime.strptime(t["data"], "%Y-%m-%d").date()
            if data_t.month == mes and data_t.year == ano:
                total += Decimal(str(t["valor"]))
    return float(total)


def obter_faturamento_12_meses(transacoes, mes_ref, ano_ref):
    """Calcula a RBT12 (Receita Bruta Total dos últimos 12 meses)."""
    total = Decimal("0")
    for i in range(12):
        m = mes_ref - i
        a = ano_ref
        while m <= 0:
            m += 12
            a -= 1
        total += Decimal(str(obter_faturamento_periodo(transacoes, m, a)))
    return float(total)


def obter_faturamento_trimestre(transacoes, mes_ref, ano_ref):
    """Retorna faturamentos dos 3 meses do trimestre ao qual o mês pertence."""
    trimestre = ((mes_ref - 1) // 3) * 3 + 1
    faturamentos = []
    for m in range(trimestre, trimestre + 3):
        a = ano_ref
        if m > 12:
            m -= 12
            a += 1
        faturamentos.append(obter_faturamento_periodo(transacoes, m, a))
    return faturamentos


def obter_faturamento_acumulado_ano(transacoes, mes_ref, ano_ref):
    """Calcula o faturamento acumulado no ano até o mês informado."""
    total = Decimal("0")
    for m in range(1, mes_ref + 1):
        total += Decimal(str(obter_faturamento_periodo(transacoes, m, ano_ref)))
    return float(total)


def fechamento(mes=None, ano=None, regime=None):
    """
    Executa o fechamento tributário mensal.

    Args:
        mes: Mês de referência (default: mês anterior)
        ano: Ano de referência (default: ano atual)
        regime: Regime tributário (default: carregado da config da empresa)

    Returns:
        dict com resultado completo do fechamento
    """
    hoje = date.today()
    if mes is None:
        mes = hoje.month - 1 if hoje.month > 1 else 12
    if ano is None:
        ano = hoje.year if hoje.month > 1 else hoje.year - 1

    config = carregar_config_empresa()
    if regime is None:
        regime = config.get("regime_tributario", "simples_nacional")

    atividade = config.get("atividade_principal", "comercio")
    transacoes = carregar_transacoes()

    faturamento_mes = obter_faturamento_periodo(transacoes, mes, ano)
    despesas_mes = obter_despesas_periodo(transacoes, mes, ano)

    resultado_base = {
        "periodo": f"{mes:02d}/{ano}",
        "mes": mes,
        "ano": ano,
        "regime": regime,
        "atividade": atividade,
        "empresa": config.get("nome_fantasia", config.get("razao_social", "")),
        "cnpj": config.get("cnpj", ""),
        "faturamento_mes": faturamento_mes,
        "despesas_mes": despesas_mes,
        "data_processamento": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

    if regime == "simples_nacional":
        rbt12 = obter_faturamento_12_meses(transacoes, mes, ano)
        calculo = simples_nacional.calcular_das(faturamento_mes, rbt12, atividade)
        resultado_base.update({
            "rbt12": rbt12,
            "calculo": calculo,
            "impostos_a_pagar": calculo.get("valor_das", 0),
        })

    elif regime == "lucro_presumido":
        # PIS/COFINS mensal
        pis_cofins = lucro_presumido.calcular_pis_cofins(faturamento_mes)
        resultado_base["pis_cofins"] = pis_cofins
        resultado_base["impostos_mensais"] = {
            "pis": pis_cofins["pis"],
            "cofins": pis_cofins["cofins"],
            "total_mensal": pis_cofins["pis"] + pis_cofins["cofins"]
        }

        # IRPJ/CSLL trimestral (só calcula no último mês do trimestre)
        if mes % 3 == 0:
            fats_trimestre = obter_faturamento_trimestre(transacoes, mes, ano)
            irpj = lucro_presumido.calcular_irpj_trimestral(sum(fats_trimestre), atividade)
            csll = lucro_presumido.calcular_csll_trimestral(sum(fats_trimestre), atividade)
            resultado_base["trimestral"] = {
                "irpj": irpj,
                "csll": csll,
                "faturamentos_trimestre": fats_trimestre
            }
            resultado_base["impostos_a_pagar"] = (
                pis_cofins["pis"] + pis_cofins["cofins"] +
                irpj["irpj_total"] + csll["csll"]
            )
        else:
            resultado_base["impostos_a_pagar"] = pis_cofins["pis"] + pis_cofins["cofins"]
            resultado_base["nota"] = f"IRPJ e CSLL serão calculados no fechamento do trimestre (mês {((mes-1)//3+1)*3})"

    elif regime == "lucro_real":
        calculo = lucro_real.fechamento_mensal(
            receita_bruta=faturamento_mes,
            despesas_dedutiveis=despesas_mes
        )
        resultado_base.update({
            "calculo": calculo,
            "impostos_a_pagar": calculo["total_impostos"],
        })

    elif regime == "mei":
        fat_acumulado = obter_faturamento_acumulado_ano(transacoes, mes, ano)
        calculo = mei.fechamento_mensal_mei(
            faturamento_mes=faturamento_mes,
            faturamento_acumulado_ano=fat_acumulado,
            categoria=atividade,
            mes_atual=mes,
            ano=ano
        )
        resultado_base.update({
            "calculo": calculo,
            "impostos_a_pagar": calculo["valor_a_pagar"],
            "faturamento_acumulado_ano": fat_acumulado,
        })

    else:
        resultado_base["erro"] = f"Regime tributário '{regime}' não reconhecido. Use: simples_nacional, lucro_presumido, lucro_real ou mei."

    return resultado_base


def gerar_relatorio_fechamento(resultado):
    """Gera relatório em texto do fechamento tributário."""
    linhas = [
        "=" * 70,
        "FECHAMENTO TRIBUTÁRIO MENSAL",
        "=" * 70,
        f"Empresa: {resultado.get('empresa', 'N/A')}",
        f"CNPJ: {resultado.get('cnpj', 'N/A')}",
        f"Período: {resultado.get('periodo', 'N/A')}",
        f"Regime: {resultado.get('regime', 'N/A').upper().replace('_', ' ')}",
        f"Atividade: {resultado.get('atividade', 'N/A')}",
        f"Data do processamento: {resultado.get('data_processamento', 'N/A')}",
        "-" * 70,
        f"Faturamento do mês: {formatar_moeda(resultado.get('faturamento_mes', 0))}",
        f"Despesas do mês: {formatar_moeda(resultado.get('despesas_mes', 0))}",
    ]

    regime = resultado.get("regime", "")

    if regime == "simples_nacional":
        linhas.extend([
            f"RBT12: {formatar_moeda(resultado.get('rbt12', 0))}",
            "-" * 70,
            "CÁLCULO DO DAS:",
        ])
        calculo = resultado.get("calculo", {})
        if calculo.get("valor_das") is not None:
            linhas.extend([
                f"  Alíquota efetiva: {calculo.get('aliquota_efetiva_percentual', 'N/A')}",
                f"  Faixa: {calculo.get('faixa', 'N/A')}",
                f"  Anexo: {calculo.get('anexo', 'N/A')}",
                f"  Valor do DAS: {formatar_moeda(calculo.get('valor_das', 0))}",
            ])
        else:
            linhas.append(f"  {calculo.get('detalhes', 'Sem dados')}")

    elif regime == "lucro_presumido":
        linhas.append("-" * 70)
        linhas.append("IMPOSTOS MENSAIS (PIS/COFINS):")
        imp = resultado.get("impostos_mensais", {})
        linhas.extend([
            f"  PIS: {formatar_moeda(imp.get('pis', 0))}",
            f"  COFINS: {formatar_moeda(imp.get('cofins', 0))}",
        ])
        if "trimestral" in resultado:
            tri = resultado["trimestral"]
            linhas.extend([
                "-" * 70,
                "IMPOSTOS TRIMESTRAIS (IRPJ/CSLL):",
                f"  IRPJ: {formatar_moeda(tri['irpj']['irpj_total'])}",
                f"    (Normal: {formatar_moeda(tri['irpj']['irpj_normal'])} + Adicional: {formatar_moeda(tri['irpj']['irpj_adicional'])})",
                f"  CSLL: {formatar_moeda(tri['csll']['csll'])}",
            ])
        elif "nota" in resultado:
            linhas.append(f"  Nota: {resultado['nota']}")

    elif regime == "lucro_real":
        calculo = resultado.get("calculo", {})
        linhas.extend([
            f"Lucro contábil: {formatar_moeda(calculo.get('lucro_contabil', 0))}",
            f"Lucro real: {formatar_moeda(calculo.get('lucro_real', 0))}",
            "-" * 70,
            "IMPOSTOS:",
        ])
        pc = calculo.get("pis_cofins", {})
        linhas.extend([
            f"  PIS a pagar: {formatar_moeda(pc.get('pis_a_pagar', 0))}",
            f"  COFINS a pagar: {formatar_moeda(pc.get('cofins_a_pagar', 0))}",
        ])
        irpj = calculo.get("irpj", {})
        linhas.extend([
            f"  IRPJ: {formatar_moeda(irpj.get('irpj_total', 0))}",
        ])
        csll_val = calculo.get("csll", {})
        linhas.append(f"  CSLL: {formatar_moeda(csll_val.get('csll', 0))}")

    elif regime == "mei":
        calculo = resultado.get("calculo", {})
        das = calculo.get("das_mei", {})
        linhas.extend([
            "-" * 70,
            "DAS-MEI:",
            f"  INSS: {formatar_moeda(das.get('inss', 0))}",
            f"  ICMS: {formatar_moeda(das.get('icms', 0))}",
            f"  ISS: {formatar_moeda(das.get('iss', 0))}",
        ])
        limite = calculo.get("limite_faturamento", {})
        linhas.extend([
            "-" * 70,
            f"Faturamento acumulado no ano: {formatar_moeda(resultado.get('faturamento_acumulado_ano', 0))}",
            f"Limite anual: {formatar_moeda(limite.get('limite_anual', 81000))}",
            f"Utilizado: {limite.get('percentual_utilizado', 'N/A')}",
            f"Status: {limite.get('status', 'N/A')}",
        ])
        if limite.get("alerta"):
            linhas.append(f"  >> {limite['alerta']}")

    linhas.extend([
        "=" * 70,
        f"TOTAL DE IMPOSTOS A PAGAR: {formatar_moeda(resultado.get('impostos_a_pagar', 0))}",
        "=" * 70,
    ])

    return "\n".join(linhas)
