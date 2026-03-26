"""Sistema de follow-up automático de clientes."""

from datetime import datetime, date, timedelta
from ..config import carregar_clientes, carregar_transacoes


def clientes_sem_compra(dias=30):
    """Identifica clientes ativos que não compraram nos últimos N dias."""
    clientes = carregar_clientes()
    transacoes = carregar_transacoes()
    hoje = date.today()
    limite = hoje - timedelta(days=dias)

    # Mapear última compra por cliente
    ultima_compra = {}
    for t in transacoes.get("transacoes", []):
        if t["tipo"] == "receita" and t.get("cliente_id"):
            data_t = datetime.strptime(t["data"], "%Y-%m-%d").date()
            cid = t["cliente_id"]
            if cid not in ultima_compra or data_t > ultima_compra[cid]:
                ultima_compra[cid] = data_t

    # Filtrar clientes sem compra recente
    resultado = []
    for c in clientes.get("clientes", []):
        if c.get("status") != "ativo":
            continue
        cid = c["id"]
        ult = ultima_compra.get(cid)
        if ult is None:
            resultado.append({
                **c,
                "ultima_compra": "Nunca",
                "dias_sem_compra": None,
                "prioridade": "alta"
            })
        elif ult < limite:
            dias_sem = (hoje - ult).days
            resultado.append({
                **c,
                "ultima_compra": ult.strftime("%d/%m/%Y"),
                "dias_sem_compra": dias_sem,
                "prioridade": "alta" if dias_sem > 60 else "media"
            })

    return sorted(resultado, key=lambda x: x.get("dias_sem_compra") or 9999, reverse=True)


def gerar_lista_followup(dias=30):
    """Gera lista de follow-up com ações sugeridas."""
    clientes = clientes_sem_compra(dias)

    lista = []
    for c in clientes:
        dias_sem = c.get("dias_sem_compra")
        if dias_sem is None:
            acao = "Primeiro contato - apresentar catálogo e promoções"
        elif dias_sem > 90:
            acao = "Reativação urgente - oferecer desconto especial"
        elif dias_sem > 60:
            acao = "Follow-up prioritário - verificar satisfação e novas necessidades"
        else:
            acao = "Follow-up regular - informar novidades e promoções"

        lista.append({
            "cliente": c["nome"],
            "telefone": c.get("telefone", ""),
            "email": c.get("email", ""),
            "ultima_compra": c["ultima_compra"],
            "dias_sem_compra": dias_sem,
            "prioridade": c["prioridade"],
            "acao_sugerida": acao
        })

    return lista


def gerar_relatorio_followup(dias=30):
    """Gera relatório textual de follow-up."""
    lista = gerar_lista_followup(dias)
    if not lista:
        return "Nenhum cliente necessita de follow-up no momento."

    linhas = [
        "=" * 70,
        f"LISTA DE FOLLOW-UP - Clientes sem compra há mais de {dias} dias",
        "=" * 70,
        f"Total de clientes para contatar: {len(lista)}",
        "-" * 70,
    ]

    for i, item in enumerate(lista, 1):
        linhas.extend([
            f"\n{i}. {item['cliente']} [{item['prioridade'].upper()}]",
            f"   Telefone: {item['telefone'] or 'N/A'}",
            f"   E-mail: {item['email'] or 'N/A'}",
            f"   Última compra: {item['ultima_compra']}",
            f"   Ação: {item['acao_sugerida']}",
        ])

    linhas.append("\n" + "=" * 70)
    return "\n".join(linhas)
