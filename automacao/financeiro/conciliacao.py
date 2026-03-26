"""Conciliação bancária simplificada."""

from datetime import datetime, date
from decimal import Decimal
from ..config import carregar_transacoes
from ..utils.formatadores import formatar_moeda


def conciliar_periodo(mes, ano):
    """
    Realiza conciliação bancária do período.
    Compara transações registradas com seus status de pagamento.
    """
    dados = carregar_transacoes()

    pagas = []
    pendentes = []
    atrasadas = []
    hoje = date.today()

    for t in dados.get("transacoes", []):
        data_t = datetime.strptime(t["data"], "%Y-%m-%d").date()
        if data_t.month != mes or data_t.year != ano:
            continue

        if t.get("status") == "pago":
            pagas.append(t)
        else:
            venc = datetime.strptime(t.get("data_vencimento", "9999-12-31"), "%Y-%m-%d").date()
            if venc < hoje:
                atrasadas.append(t)
            else:
                pendentes.append(t)

    total_pagas = sum(Decimal(str(t["valor"])) for t in pagas)
    total_pendentes = sum(Decimal(str(t["valor"])) for t in pendentes)
    total_atrasadas = sum(Decimal(str(t["valor"])) for t in atrasadas)

    receitas_pagas = sum(Decimal(str(t["valor"])) for t in pagas if t["tipo"] == "receita")
    despesas_pagas = sum(Decimal(str(t["valor"])) for t in pagas if t["tipo"] == "despesa")

    return {
        "periodo": f"{mes:02d}/{ano}",
        "transacoes_conciliadas": len(pagas),
        "transacoes_pendentes": len(pendentes),
        "transacoes_atrasadas": len(atrasadas),
        "total_conciliado": float(total_pagas),
        "total_pendente": float(total_pendentes),
        "total_atrasado": float(total_atrasadas),
        "receitas_conciliadas": float(receitas_pagas),
        "despesas_conciliadas": float(despesas_pagas),
        "saldo_conciliado": float(receitas_pagas - despesas_pagas),
        "detalhes_pagas": pagas,
        "detalhes_pendentes": pendentes,
        "detalhes_atrasadas": atrasadas
    }


def gerar_relatorio_conciliacao(resultado):
    """Gera relatório textual da conciliação."""
    linhas = [
        "=" * 60,
        "CONCILIAÇÃO BANCÁRIA",
        "=" * 60,
        f"Período: {resultado['periodo']}",
        "-" * 60,
        f"Transações conciliadas: {resultado['transacoes_conciliadas']}",
        f"Transações pendentes:   {resultado['transacoes_pendentes']}",
        f"Transações atrasadas:   {resultado['transacoes_atrasadas']}",
        "-" * 60,
        f"Receitas conciliadas: {formatar_moeda(resultado['receitas_conciliadas'])}",
        f"Despesas conciliadas: {formatar_moeda(resultado['despesas_conciliadas'])}",
        f"Saldo conciliado:     {formatar_moeda(resultado['saldo_conciliado'])}",
        "-" * 60,
        f"Total pendente:  {formatar_moeda(resultado['total_pendente'])}",
        f"Total atrasado:  {formatar_moeda(resultado['total_atrasado'])}",
        "=" * 60,
    ]

    if resultado["detalhes_atrasadas"]:
        linhas.append("\nTRANSAÇÕES ATRASADAS:")
        for t in resultado["detalhes_atrasadas"]:
            linhas.append(f"  [{t['tipo'].upper()}] {t['descricao']} - {formatar_moeda(t['valor'])} (venc: {t['data_vencimento']})")

    return "\n".join(linhas)
