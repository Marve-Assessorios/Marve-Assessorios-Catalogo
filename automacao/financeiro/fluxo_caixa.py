"""Controle de fluxo de caixa."""

from datetime import datetime, date, timedelta
from decimal import Decimal
from collections import defaultdict
from ..config import carregar_transacoes
from ..utils.formatadores import formatar_moeda


def fluxo_caixa_periodo(data_inicio, data_fim):
    """
    Gera fluxo de caixa para um período.

    Args:
        data_inicio: Data início (str "YYYY-MM-DD" ou date)
        data_fim: Data fim (str "YYYY-MM-DD" ou date)
    """
    if isinstance(data_inicio, str):
        data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
    if isinstance(data_fim, str):
        data_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()

    dados = carregar_transacoes()
    receitas = Decimal("0")
    despesas = Decimal("0")
    movimentacoes = []

    for t in dados.get("transacoes", []):
        data_t = datetime.strptime(t["data"], "%Y-%m-%d").date()
        if data_inicio <= data_t <= data_fim:
            valor = Decimal(str(t["valor"]))
            if t["tipo"] == "receita":
                receitas += valor
            else:
                despesas += valor
            movimentacoes.append(t)

    saldo = receitas - despesas

    return {
        "periodo": f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}",
        "total_receitas": float(receitas),
        "total_despesas": float(despesas),
        "saldo": float(saldo),
        "saldo_positivo": saldo >= 0,
        "qtd_movimentacoes": len(movimentacoes),
        "movimentacoes": sorted(movimentacoes, key=lambda x: x["data"])
    }


def fluxo_caixa_mensal(mes, ano):
    """Gera fluxo de caixa de um mês específico."""
    from calendar import monthrange
    ultimo_dia = monthrange(ano, mes)[1]
    data_inicio = date(ano, mes, 1)
    data_fim = date(ano, mes, ultimo_dia)
    return fluxo_caixa_periodo(data_inicio, data_fim)


def fluxo_caixa_diario(data_ref=None):
    """Gera fluxo de caixa do dia."""
    if data_ref is None:
        data_ref = date.today()
    if isinstance(data_ref, str):
        data_ref = datetime.strptime(data_ref, "%Y-%m-%d").date()
    return fluxo_caixa_periodo(data_ref, data_ref)


def previsao_fluxo(dias=30):
    """
    Gera previsão de fluxo de caixa para os próximos N dias
    baseado nas contas pendentes (a pagar e a receber).
    """
    hoje = date.today()
    limite = hoje + timedelta(days=dias)
    dados = carregar_transacoes()

    previsao_diaria = defaultdict(lambda: {"receitas": Decimal("0"), "despesas": Decimal("0")})

    for t in dados.get("transacoes", []):
        if t.get("status") != "pendente":
            continue
        vencimento = t.get("data_vencimento")
        if not vencimento:
            continue
        data_venc = datetime.strptime(vencimento, "%Y-%m-%d").date()
        if hoje <= data_venc <= limite:
            valor = Decimal(str(t["valor"]))
            if t["tipo"] == "receita":
                previsao_diaria[vencimento]["receitas"] += valor
            else:
                previsao_diaria[vencimento]["despesas"] += valor

    previsao = []
    saldo_acumulado = Decimal("0")
    for data_str in sorted(previsao_diaria.keys()):
        dia = previsao_diaria[data_str]
        saldo_dia = dia["receitas"] - dia["despesas"]
        saldo_acumulado += saldo_dia
        previsao.append({
            "data": data_str,
            "receitas": float(dia["receitas"]),
            "despesas": float(dia["despesas"]),
            "saldo_dia": float(saldo_dia),
            "saldo_acumulado": float(saldo_acumulado)
        })

    return {
        "periodo": f"Próximos {dias} dias",
        "previsao": previsao,
        "total_receitas_previstas": float(sum(Decimal(str(d["receitas"])) for d in previsao)),
        "total_despesas_previstas": float(sum(Decimal(str(d["despesas"])) for d in previsao)),
        "saldo_previsto": float(saldo_acumulado)
    }


def gerar_relatorio_fluxo(fluxo):
    """Gera relatório em texto do fluxo de caixa."""
    linhas = [
        "=" * 60,
        "FLUXO DE CAIXA",
        "=" * 60,
        f"Período: {fluxo.get('periodo', 'N/A')}",
        "-" * 60,
        f"Total Receitas:  {formatar_moeda(fluxo.get('total_receitas', 0))}",
        f"Total Despesas:  {formatar_moeda(fluxo.get('total_despesas', 0))}",
        f"Saldo:           {formatar_moeda(fluxo.get('saldo', 0))}",
        "-" * 60,
        f"Movimentações: {fluxo.get('qtd_movimentacoes', 0)}",
        "=" * 60,
    ]
    return "\n".join(linhas)
