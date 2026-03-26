"""Gestão de contas a receber."""

from datetime import datetime, date, timedelta
from decimal import Decimal
from ..config import carregar_transacoes, salvar_transacoes
from ..utils.formatadores import formatar_moeda, formatar_data


def listar_contas_a_receber(status="pendente"):
    """Lista contas a receber filtradas por status."""
    dados = carregar_transacoes()
    contas = [
        t for t in dados.get("transacoes", [])
        if t["tipo"] == "receita" and t.get("status", "pendente") == status
    ]
    return sorted(contas, key=lambda x: x.get("data_vencimento", "9999-12-31"))


def adicionar_conta(descricao, valor, data_vencimento, cliente_id=None, categoria="vendas", observacoes=""):
    """Adiciona nova conta a receber."""
    dados = carregar_transacoes()
    novo_id = dados.get("proximo_id", 1)

    nova_conta = {
        "id": novo_id,
        "tipo": "receita",
        "descricao": descricao,
        "valor": float(valor),
        "data": date.today().strftime("%Y-%m-%d"),
        "data_vencimento": data_vencimento,
        "data_pagamento": None,
        "status": "pendente",
        "categoria": categoria,
        "cliente_id": cliente_id,
        "observacoes": observacoes
    }

    dados["transacoes"].append(nova_conta)
    dados["proximo_id"] = novo_id + 1
    salvar_transacoes(dados)
    return nova_conta


def registrar_recebimento(conta_id, data_recebimento=None):
    """Registra o recebimento de uma conta."""
    if data_recebimento is None:
        data_recebimento = date.today().strftime("%Y-%m-%d")

    dados = carregar_transacoes()
    for t in dados["transacoes"]:
        if t["id"] == conta_id and t["tipo"] == "receita":
            t["status"] = "pago"
            t["data_pagamento"] = data_recebimento
            salvar_transacoes(dados)
            return t
    return None


def contas_a_vencer(dias=7):
    """Retorna contas a receber que vencem nos próximos N dias."""
    hoje = date.today()
    limite = hoje + timedelta(days=dias)
    pendentes = listar_contas_a_receber("pendente")

    vencendo = []
    for conta in pendentes:
        venc = datetime.strptime(conta["data_vencimento"], "%Y-%m-%d").date()
        if venc <= limite:
            dias_restantes = (venc - hoje).days
            conta["dias_restantes"] = dias_restantes
            conta["atrasada"] = dias_restantes < 0
            vencendo.append(conta)

    return vencendo


def resumo_contas_a_receber():
    """Gera resumo das contas a receber."""
    pendentes = listar_contas_a_receber("pendente")
    recebidas = listar_contas_a_receber("pago")

    total_pendente = sum(Decimal(str(c["valor"])) for c in pendentes)
    total_recebido = sum(Decimal(str(c["valor"])) for c in recebidas)
    atrasadas = [c for c in pendentes if datetime.strptime(c["data_vencimento"], "%Y-%m-%d").date() < date.today()]
    total_atrasado = sum(Decimal(str(c["valor"])) for c in atrasadas)

    return {
        "total_pendente": float(total_pendente),
        "total_recebido": float(total_recebido),
        "total_atrasado": float(total_atrasado),
        "qtd_pendentes": len(pendentes),
        "qtd_recebidas": len(recebidas),
        "qtd_atrasadas": len(atrasadas),
        "contas_pendentes": pendentes,
        "contas_atrasadas": atrasadas
    }
