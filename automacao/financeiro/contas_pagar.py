"""Gestão de contas a pagar."""

from datetime import datetime, date, timedelta
from decimal import Decimal
from ..config import carregar_transacoes, salvar_transacoes
from ..utils.formatadores import formatar_moeda, formatar_data


def listar_contas_a_pagar(status="pendente"):
    """Lista contas a pagar filtradas por status."""
    dados = carregar_transacoes()
    contas = [
        t for t in dados.get("transacoes", [])
        if t["tipo"] == "despesa" and t.get("status", "pendente") == status
    ]
    return sorted(contas, key=lambda x: x.get("data_vencimento", "9999-12-31"))


def adicionar_conta(descricao, valor, data_vencimento, categoria="geral", observacoes=""):
    """Adiciona nova conta a pagar."""
    dados = carregar_transacoes()
    novo_id = dados.get("proximo_id", 1)

    nova_conta = {
        "id": novo_id,
        "tipo": "despesa",
        "descricao": descricao,
        "valor": float(valor),
        "data": date.today().strftime("%Y-%m-%d"),
        "data_vencimento": data_vencimento,
        "data_pagamento": None,
        "status": "pendente",
        "categoria": categoria,
        "cliente_id": None,
        "observacoes": observacoes
    }

    dados["transacoes"].append(nova_conta)
    dados["proximo_id"] = novo_id + 1
    salvar_transacoes(dados)
    return nova_conta


def registrar_pagamento(conta_id, data_pagamento=None):
    """Registra o pagamento de uma conta."""
    if data_pagamento is None:
        data_pagamento = date.today().strftime("%Y-%m-%d")

    dados = carregar_transacoes()
    for t in dados["transacoes"]:
        if t["id"] == conta_id and t["tipo"] == "despesa":
            t["status"] = "pago"
            t["data_pagamento"] = data_pagamento
            salvar_transacoes(dados)
            return t
    return None


def contas_vencendo(dias=7):
    """Retorna contas que vencem nos próximos N dias."""
    hoje = date.today()
    limite = hoje + timedelta(days=dias)
    pendentes = listar_contas_a_pagar("pendente")

    vencendo = []
    for conta in pendentes:
        venc = datetime.strptime(conta["data_vencimento"], "%Y-%m-%d").date()
        if venc <= limite:
            dias_restantes = (venc - hoje).days
            conta["dias_restantes"] = dias_restantes
            conta["vencida"] = dias_restantes < 0
            vencendo.append(conta)

    return vencendo


def resumo_contas_a_pagar():
    """Gera resumo das contas a pagar."""
    pendentes = listar_contas_a_pagar("pendente")
    pagas = listar_contas_a_pagar("pago")

    total_pendente = sum(Decimal(str(c["valor"])) for c in pendentes)
    total_pago = sum(Decimal(str(c["valor"])) for c in pagas)
    vencidas = [c for c in pendentes if datetime.strptime(c["data_vencimento"], "%Y-%m-%d").date() < date.today()]
    total_vencido = sum(Decimal(str(c["valor"])) for c in vencidas)

    return {
        "total_pendente": float(total_pendente),
        "total_pago": float(total_pago),
        "total_vencido": float(total_vencido),
        "qtd_pendentes": len(pendentes),
        "qtd_pagas": len(pagas),
        "qtd_vencidas": len(vencidas),
        "contas_pendentes": pendentes,
        "contas_vencidas": vencidas
    }
