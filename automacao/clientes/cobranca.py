"""Sistema de cobranças automáticas."""

from datetime import datetime, date, timedelta
from decimal import Decimal
from ..config import carregar_transacoes, carregar_clientes
from ..utils.formatadores import formatar_moeda, formatar_data


def identificar_inadimplentes():
    """Identifica clientes com pagamentos em atraso."""
    transacoes = carregar_transacoes()
    clientes = carregar_clientes()
    hoje = date.today()

    # Mapear clientes por ID
    mapa_clientes = {c["id"]: c for c in clientes.get("clientes", [])}

    # Agrupar atrasos por cliente
    atrasos_por_cliente = {}
    for t in transacoes.get("transacoes", []):
        if t["tipo"] != "receita" or t.get("status") == "pago":
            continue
        if not t.get("cliente_id") or not t.get("data_vencimento"):
            continue

        vencimento = datetime.strptime(t["data_vencimento"], "%Y-%m-%d").date()
        if vencimento >= hoje:
            continue

        cid = t["cliente_id"]
        dias_atraso = (hoje - vencimento).days

        if cid not in atrasos_por_cliente:
            cliente = mapa_clientes.get(cid, {"nome": f"Cliente #{cid}"})
            atrasos_por_cliente[cid] = {
                "cliente_id": cid,
                "nome": cliente.get("nome", f"Cliente #{cid}"),
                "telefone": cliente.get("telefone", ""),
                "email": cliente.get("email", ""),
                "titulos": [],
                "total_em_atraso": Decimal("0"),
                "maior_atraso_dias": 0
            }

        atrasos_por_cliente[cid]["titulos"].append({
            "id": t["id"],
            "descricao": t["descricao"],
            "valor": t["valor"],
            "vencimento": t["data_vencimento"],
            "dias_atraso": dias_atraso
        })
        atrasos_por_cliente[cid]["total_em_atraso"] += Decimal(str(t["valor"]))
        atrasos_por_cliente[cid]["maior_atraso_dias"] = max(
            atrasos_por_cliente[cid]["maior_atraso_dias"], dias_atraso
        )

    # Converter para lista e definir nível de cobrança
    resultado = []
    for cid, info in atrasos_por_cliente.items():
        info["total_em_atraso"] = float(info["total_em_atraso"])
        dias = info["maior_atraso_dias"]

        if dias <= 7:
            info["nivel_cobranca"] = "lembrete"
            info["acao"] = "Enviar lembrete amigável de pagamento"
        elif dias <= 30:
            info["nivel_cobranca"] = "cobranca_1"
            info["acao"] = "Primeira cobrança formal - contato telefônico"
        elif dias <= 60:
            info["nivel_cobranca"] = "cobranca_2"
            info["acao"] = "Segunda cobrança - notificação por escrito"
        else:
            info["nivel_cobranca"] = "cobranca_3"
            info["acao"] = "Terceira cobrança - avaliar protesto ou negativação"

        resultado.append(info)

    return sorted(resultado, key=lambda x: x["maior_atraso_dias"], reverse=True)


def gerar_relatorio_cobranca():
    """Gera relatório de cobranças."""
    inadimplentes = identificar_inadimplentes()

    if not inadimplentes:
        return "Nenhum cliente inadimplente encontrado."

    total_geral = sum(Decimal(str(c["total_em_atraso"])) for c in inadimplentes)

    linhas = [
        "=" * 70,
        "RELATÓRIO DE COBRANÇAS",
        "=" * 70,
        f"Clientes inadimplentes: {len(inadimplentes)}",
        f"Total em atraso: {formatar_moeda(float(total_geral))}",
        "-" * 70,
    ]

    for i, info in enumerate(inadimplentes, 1):
        linhas.extend([
            f"\n{i}. {info['nome']} [{info['nivel_cobranca'].upper()}]",
            f"   Telefone: {info['telefone'] or 'N/A'}",
            f"   E-mail: {info['email'] or 'N/A'}",
            f"   Total em atraso: {formatar_moeda(info['total_em_atraso'])}",
            f"   Maior atraso: {info['maior_atraso_dias']} dias",
            f"   Ação recomendada: {info['acao']}",
            f"   Títulos:",
        ])
        for titulo in info["titulos"]:
            linhas.append(
                f"     - {titulo['descricao']}: {formatar_moeda(titulo['valor'])} "
                f"(venc: {titulo['vencimento']}, {titulo['dias_atraso']} dias)"
            )

    linhas.append("\n" + "=" * 70)
    return "\n".join(linhas)
