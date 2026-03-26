"""Relatório de vendas."""

from datetime import datetime, date
from decimal import Decimal
from collections import defaultdict
from ..config import carregar_transacoes, carregar_clientes
from ..utils.formatadores import formatar_moeda


def vendas_periodo(mes=None, ano=None):
    """Gera relatório de vendas de um período."""
    if mes is None:
        mes = date.today().month
    if ano is None:
        ano = date.today().year

    dados = carregar_transacoes()
    clientes = carregar_clientes()
    mapa_clientes = {c["id"]: c["nome"] for c in clientes.get("clientes", [])}

    vendas = []
    total = Decimal("0")
    por_categoria = defaultdict(lambda: Decimal("0"))
    por_cliente = defaultdict(lambda: Decimal("0"))

    for t in dados.get("transacoes", []):
        if t["tipo"] != "receita":
            continue
        data_t = datetime.strptime(t["data"], "%Y-%m-%d").date()
        if data_t.month != mes or data_t.year != ano:
            continue

        valor = Decimal(str(t["valor"]))
        total += valor
        por_categoria[t.get("categoria", "outros")] += valor

        cid = t.get("cliente_id")
        nome_cliente = mapa_clientes.get(cid, "Não identificado") if cid else "Não identificado"
        por_cliente[nome_cliente] += valor

        vendas.append({
            "data": t["data"],
            "descricao": t["descricao"],
            "valor": float(valor),
            "categoria": t.get("categoria", "outros"),
            "cliente": nome_cliente,
            "status": t.get("status", "pendente")
        })

    return {
        "periodo": f"{mes:02d}/{ano}",
        "total_vendas": float(total),
        "qtd_vendas": len(vendas),
        "ticket_medio": float(total / len(vendas)) if vendas else 0,
        "por_categoria": {k: float(v) for k, v in sorted(por_categoria.items(), key=lambda x: x[1], reverse=True)},
        "por_cliente": {k: float(v) for k, v in sorted(por_cliente.items(), key=lambda x: x[1], reverse=True)},
        "vendas": sorted(vendas, key=lambda x: x["data"])
    }


def gerar_relatorio_vendas(mes=None, ano=None):
    """Gera relatório textual de vendas."""
    dados = vendas_periodo(mes, ano)

    linhas = [
        "=" * 60,
        f"RELATÓRIO DE VENDAS - {dados['periodo']}",
        "=" * 60,
        f"Total de vendas: {formatar_moeda(dados['total_vendas'])}",
        f"Quantidade: {dados['qtd_vendas']}",
        f"Ticket médio: {formatar_moeda(dados['ticket_medio'])}",
        "-" * 60,
        "POR CATEGORIA:",
    ]

    for cat, valor in dados["por_categoria"].items():
        pct = (valor / dados["total_vendas"] * 100) if dados["total_vendas"] > 0 else 0
        linhas.append(f"  {cat}: {formatar_moeda(valor)} ({pct:.1f}%)")

    linhas.extend(["-" * 60, "POR CLIENTE:"])
    for cli, valor in dados["por_cliente"].items():
        linhas.append(f"  {cli}: {formatar_moeda(valor)}")

    linhas.extend(["-" * 60, "DETALHAMENTO:"])
    for v in dados["vendas"]:
        status = "OK" if v["status"] == "pago" else "PENDENTE"
        linhas.append(f"  {v['data']} | {v['descricao']} | {formatar_moeda(v['valor'])} [{status}]")

    linhas.append("=" * 60)
    return "\n".join(linhas)
