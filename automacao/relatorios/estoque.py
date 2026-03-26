"""Relatório de estoque (baseado nos produtos do catálogo)."""

from datetime import date
from decimal import Decimal
from ..utils.formatadores import formatar_moeda


def resumo_estoque(produtos=None):
    """
    Gera resumo de estoque.

    Args:
        produtos: Lista de produtos (se None, usa dados de exemplo)
    """
    if produtos is None:
        produtos = []

    total_itens = len(produtos)
    valor_total = Decimal("0")
    sem_estoque = 0
    estoque_baixo = 0

    for p in produtos:
        preco = Decimal(str(p.get("preco", 0)))
        qtd = p.get("quantidade", 0)
        valor_total += preco * qtd
        if qtd == 0:
            sem_estoque += 1
        elif qtd <= 5:
            estoque_baixo += 1

    return {
        "total_produtos": total_itens,
        "valor_total_estoque": float(valor_total),
        "produtos_sem_estoque": sem_estoque,
        "produtos_estoque_baixo": estoque_baixo,
        "data_consulta": date.today().strftime("%d/%m/%Y")
    }


def gerar_relatorio_estoque(produtos=None):
    """Gera relatório textual de estoque."""
    resumo = resumo_estoque(produtos)

    linhas = [
        "=" * 60,
        "RELATÓRIO DE ESTOQUE",
        "=" * 60,
        f"Data: {resumo['data_consulta']}",
        "-" * 60,
        f"Total de produtos: {resumo['total_produtos']}",
        f"Valor total em estoque: {formatar_moeda(resumo['valor_total_estoque'])}",
        f"Produtos sem estoque: {resumo['produtos_sem_estoque']}",
        f"Produtos com estoque baixo: {resumo['produtos_estoque_baixo']}",
        "=" * 60,
    ]

    if resumo["produtos_sem_estoque"] > 0 or resumo["produtos_estoque_baixo"] > 0:
        linhas.append("\nALERTA: Há produtos que necessitam de reposição!")

    return "\n".join(linhas)
