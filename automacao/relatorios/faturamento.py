"""Relatório de faturamento mensal/anual."""

from datetime import date
from decimal import Decimal
from ..config import carregar_transacoes
from ..utils.formatadores import formatar_moeda


def faturamento_mensal(ano=None):
    """Gera relatório de faturamento mês a mês."""
    if ano is None:
        ano = date.today().year

    dados = carregar_transacoes()

    meses = {}
    for m in range(1, 13):
        meses[m] = {"receitas": Decimal("0"), "despesas": Decimal("0")}

    for t in dados.get("transacoes", []):
        from datetime import datetime
        data_t = datetime.strptime(t["data"], "%Y-%m-%d").date()
        if data_t.year != ano:
            continue
        valor = Decimal(str(t["valor"]))
        if t["tipo"] == "receita":
            meses[data_t.month]["receitas"] += valor
        else:
            meses[data_t.month]["despesas"] += valor

    resultado = []
    total_receitas = Decimal("0")
    total_despesas = Decimal("0")

    nomes_meses = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                   "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

    for m in range(1, 13):
        receita = meses[m]["receitas"]
        despesa = meses[m]["despesas"]
        lucro = receita - despesa
        total_receitas += receita
        total_despesas += despesa

        resultado.append({
            "mes": m,
            "nome_mes": nomes_meses[m],
            "receitas": float(receita),
            "despesas": float(despesa),
            "lucro_bruto": float(lucro),
            "margem": f"{float(lucro / receita * 100):.1f}%" if receita > 0 else "N/A"
        })

    return {
        "ano": ano,
        "meses": resultado,
        "total_receitas": float(total_receitas),
        "total_despesas": float(total_despesas),
        "lucro_bruto_anual": float(total_receitas - total_despesas),
        "margem_anual": f"{float((total_receitas - total_despesas) / total_receitas * 100):.1f}%" if total_receitas > 0 else "N/A"
    }


def gerar_relatorio_faturamento(ano=None):
    """Gera relatório textual de faturamento."""
    dados = faturamento_mensal(ano)

    linhas = [
        "=" * 70,
        f"RELATÓRIO DE FATURAMENTO - {dados['ano']}",
        "=" * 70,
        f"{'Mês':<6} {'Receitas':>15} {'Despesas':>15} {'Lucro':>15} {'Margem':>8}",
        "-" * 70,
    ]

    for m in dados["meses"]:
        linhas.append(
            f"{m['nome_mes']:<6} {formatar_moeda(m['receitas']):>15} "
            f"{formatar_moeda(m['despesas']):>15} {formatar_moeda(m['lucro_bruto']):>15} "
            f"{m['margem']:>8}"
        )

    linhas.extend([
        "-" * 70,
        f"{'TOTAL':<6} {formatar_moeda(dados['total_receitas']):>15} "
        f"{formatar_moeda(dados['total_despesas']):>15} "
        f"{formatar_moeda(dados['lucro_bruto_anual']):>15} "
        f"{dados['margem_anual']:>8}",
        "=" * 70,
    ])

    return "\n".join(linhas)
