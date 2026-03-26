#!/usr/bin/env python3
"""
Sistema de Automação de Escritório com IA
=========================================
Entry point unificado para todas as automações.

Uso:
    python -m automacao.main <comando> [opções]

Comandos disponíveis:
    diario          - Executa rotina diária (alertas, vencimentos, resumo)
    fechamento      - Fechamento tributário mensal
    financeiro      - Resumo financeiro
    clientes        - Gestão de clientes
    relatorio       - Gerar relatórios
    status          - Status geral do sistema
    ajuda           - Mostra esta ajuda
"""

import sys
import json
from datetime import date, datetime
from pathlib import Path

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from automacao.config import carregar_config_empresa, RELATORIOS_DIR
from automacao.financeiro.contas_pagar import contas_vencendo, resumo_contas_a_pagar
from automacao.financeiro.contas_receber import contas_a_vencer, resumo_contas_a_receber
from automacao.financeiro.fluxo_caixa import fluxo_caixa_mensal, previsao_fluxo, gerar_relatorio_fluxo
from automacao.financeiro.conciliacao import conciliar_periodo, gerar_relatorio_conciliacao
from automacao.tributario.fechamento_mensal import fechamento, gerar_relatorio_fechamento
from automacao.tributario.legislacao import resumo_regime, verificar_atualizacoes
from automacao.clientes.cadastro import resumo_clientes
from automacao.clientes.followup import gerar_relatorio_followup
from automacao.clientes.cobranca import gerar_relatorio_cobranca
from automacao.relatorios.vendas import gerar_relatorio_vendas
from automacao.relatorios.faturamento import gerar_relatorio_faturamento
from automacao.relatorios.gerador_pdf import gerar_html, salvar_relatorio_texto
from automacao.relatorios.dashboard import gerar_dashboard
from automacao.utils.formatadores import formatar_moeda


def print_separador(titulo=""):
    """Imprime separador visual."""
    if titulo:
        print(f"\n{'='*70}")
        print(f" {titulo}")
        print(f"{'='*70}")
    else:
        print("-" * 70)


def comando_status():
    """Mostra status geral do sistema."""
    config = carregar_config_empresa()
    hoje = date.today()

    print_separador("STATUS DO SISTEMA DE AUTOMAÇÃO")
    print(f"Data: {hoje.strftime('%d/%m/%Y')}")
    print(f"Empresa: {config.get('nome_fantasia', 'Não configurada')}")
    print(f"CNPJ: {config.get('cnpj', 'Não configurado')}")
    print(f"Regime: {config.get('regime_tributario', 'Não definido').replace('_', ' ').title()}")

    # Resumo financeiro
    print_separador("FINANCEIRO")
    pagar = resumo_contas_a_pagar()
    receber = resumo_contas_a_receber()
    print(f"Contas a pagar pendentes: {pagar['qtd_pendentes']} ({formatar_moeda(pagar['total_pendente'])})")
    print(f"Contas a pagar vencidas:  {pagar['qtd_vencidas']} ({formatar_moeda(pagar['total_vencido'])})")
    print(f"Contas a receber pendentes: {receber['qtd_pendentes']} ({formatar_moeda(receber['total_pendente'])})")
    print(f"Contas a receber atrasadas: {receber['qtd_atrasadas']} ({formatar_moeda(receber['total_atrasado'])})")

    # Resumo clientes
    print_separador("CLIENTES")
    cli = resumo_clientes()
    print(f"Total de clientes: {cli['total']} (Ativos: {cli['ativos']}, Inativos: {cli['inativos']})")
    print(f"Pessoa Física: {cli['pessoa_fisica']} | Pessoa Jurídica: {cli['pessoa_juridica']}")

    print_separador()
    print("Sistema operacional. Use 'python -m automacao.main ajuda' para ver comandos.")


def comando_diario():
    """Executa rotina diária de automação."""
    hoje = date.today()
    config = carregar_config_empresa()
    dias_alerta = config.get("configuracoes", {}).get("alerta_vencimento_dias", 7)

    print_separador(f"ROTINA DIÁRIA - {hoje.strftime('%d/%m/%Y')}")

    # 1. Contas a pagar vencendo
    print_separador("CONTAS A PAGAR - PRÓXIMOS VENCIMENTOS")
    vencendo = contas_vencendo(dias_alerta)
    if vencendo:
        for c in vencendo:
            status = "VENCIDA!" if c.get("vencida") else f"vence em {c['dias_restantes']} dias"
            print(f"  [{status}] {c['descricao']} - {formatar_moeda(c['valor'])} (venc: {c['data_vencimento']})")
    else:
        print("  Nenhuma conta a pagar nos próximos dias.")

    # 2. Contas a receber
    print_separador("CONTAS A RECEBER - PRÓXIMOS VENCIMENTOS")
    a_receber = contas_a_vencer(dias_alerta)
    if a_receber:
        for c in a_receber:
            status = "ATRASADA!" if c.get("atrasada") else f"vence em {c['dias_restantes']} dias"
            print(f"  [{status}] {c['descricao']} - {formatar_moeda(c['valor'])} (venc: {c['data_vencimento']})")
    else:
        print("  Nenhuma conta a receber nos próximos dias.")

    # 3. Previsão de fluxo
    print_separador("PREVISÃO DE FLUXO DE CAIXA (30 dias)")
    prev = previsao_fluxo(30)
    print(f"  Receitas previstas: {formatar_moeda(prev['total_receitas_previstas'])}")
    print(f"  Despesas previstas: {formatar_moeda(prev['total_despesas_previstas'])}")
    print(f"  Saldo previsto:     {formatar_moeda(prev['saldo_previsto'])}")

    # 4. Cobranças
    print_separador("COBRANÇAS")
    print(gerar_relatorio_cobranca())

    # 5. Follow-up
    print_separador("FOLLOW-UP DE CLIENTES")
    print(gerar_relatorio_followup(30))

    print_separador()
    print(f"Rotina diária concluída em {datetime.now().strftime('%H:%M:%S')}")

    # Salvar relatório
    conteudo = f"Rotina diária executada em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    nome = f"diario_{hoje.strftime('%Y%m%d')}"
    salvar_relatorio_texto("Rotina Diária", conteudo, nome)


def comando_fechamento(mes=None, ano=None, regime=None):
    """Executa fechamento tributário mensal."""
    resultado = fechamento(mes, ano, regime)
    relatorio = gerar_relatorio_fechamento(resultado)
    print(relatorio)

    # Salvar relatório
    periodo = resultado.get("periodo", "").replace("/", "_")
    nome = f"fechamento_{periodo}"
    caminho_txt = salvar_relatorio_texto("Fechamento Tributário", relatorio, nome)
    caminho_html = gerar_html("Fechamento Tributário Mensal", relatorio, nome)
    print(f"\nRelatórios salvos em:")
    print(f"  TXT: {caminho_txt}")
    print(f"  HTML: {caminho_html}")

    return resultado


def comando_financeiro(tipo="resumo"):
    """Mostra resumo financeiro."""
    hoje = date.today()

    if tipo == "resumo":
        print_separador("RESUMO FINANCEIRO")

        pagar = resumo_contas_a_pagar()
        print(f"\nCONTAS A PAGAR:")
        print(f"  Pendentes: {pagar['qtd_pendentes']} - {formatar_moeda(pagar['total_pendente'])}")
        print(f"  Vencidas:  {pagar['qtd_vencidas']} - {formatar_moeda(pagar['total_vencido'])}")
        print(f"  Pagas:     {pagar['qtd_pagas']} - {formatar_moeda(pagar['total_pago'])}")

        receber = resumo_contas_a_receber()
        print(f"\nCONTAS A RECEBER:")
        print(f"  Pendentes:  {receber['qtd_pendentes']} - {formatar_moeda(receber['total_pendente'])}")
        print(f"  Atrasadas:  {receber['qtd_atrasadas']} - {formatar_moeda(receber['total_atrasado'])}")
        print(f"  Recebidas:  {receber['qtd_recebidas']} - {formatar_moeda(receber['total_recebido'])}")

    elif tipo == "fluxo":
        fluxo = fluxo_caixa_mensal(hoje.month, hoje.year)
        print(gerar_relatorio_fluxo(fluxo))

    elif tipo == "conciliacao":
        resultado = conciliar_periodo(hoje.month, hoje.year)
        print(gerar_relatorio_conciliacao(resultado))

    elif tipo == "previsao":
        prev = previsao_fluxo(30)
        print_separador("PREVISÃO DE FLUXO - 30 DIAS")
        for dia in prev["previsao"]:
            print(f"  {dia['data']} | Rec: {formatar_moeda(dia['receitas'])} | Desp: {formatar_moeda(dia['despesas'])} | Saldo: {formatar_moeda(dia['saldo_acumulado'])}")
        print_separador()
        print(f"Saldo previsto: {formatar_moeda(prev['saldo_previsto'])}")


def comando_relatorio(tipo="vendas", mes=None, ano=None):
    """Gera relatórios."""
    if mes is None:
        mes = date.today().month
    if ano is None:
        ano = date.today().year

    if tipo == "vendas":
        relatorio = gerar_relatorio_vendas(mes, ano)
    elif tipo == "faturamento":
        relatorio = gerar_relatorio_faturamento(ano)
    elif tipo == "cobranca":
        relatorio = gerar_relatorio_cobranca()
    elif tipo == "followup":
        relatorio = gerar_relatorio_followup()
    else:
        relatorio = f"Tipo de relatório '{tipo}' não reconhecido. Use: vendas, faturamento, cobranca, followup"

    print(relatorio)

    # Salvar
    nome = f"relatorio_{tipo}_{mes:02d}_{ano}"
    caminho = salvar_relatorio_texto(f"Relatório de {tipo.title()}", relatorio, nome)
    caminho_html = gerar_html(f"Relatório de {tipo.title()}", relatorio, nome)
    print(f"\nSalvo em: {caminho}")
    print(f"HTML: {caminho_html}")


def comando_dashboard():
    """Gera dashboard visual em HTML."""
    print("Gerando dashboard...")
    caminho = gerar_dashboard()
    print(f"Dashboard gerado com sucesso!")
    print(f"Abra no navegador: {caminho}")


def comando_ajuda():
    """Mostra ajuda do sistema."""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║         SISTEMA DE AUTOMAÇÃO DE ESCRITÓRIO COM IA                  ║
╚══════════════════════════════════════════════════════════════════════╝

USO: python -m automacao.main <comando> [opções]

COMANDOS:
  status                          Status geral do sistema
  diario                          Executa rotina diária completa
  fechamento [--mes M] [--ano A]  Fechamento tributário mensal
             [--regime REGIME]    (simples_nacional, lucro_presumido,
                                   lucro_real, mei)
  financeiro [--tipo TIPO]        Resumo financeiro
                                  (resumo, fluxo, conciliacao, previsao)
  relatorio [--tipo TIPO]         Gerar relatórios
            [--mes M] [--ano A]   (vendas, faturamento, cobranca, followup)
  dashboard                       Gera dashboard visual HTML com gráficos
  ajuda                           Mostra esta mensagem

EXEMPLOS:
  python -m automacao.main status
  python -m automacao.main diario
  python -m automacao.main fechamento --mes 3 --ano 2026
  python -m automacao.main fechamento --regime mei
  python -m automacao.main financeiro --tipo fluxo
  python -m automacao.main relatorio --tipo vendas --mes 3
  python -m automacao.main relatorio --tipo faturamento --ano 2026

CONFIGURAÇÃO:
  Edite o arquivo dados/config_empresa.json para configurar:
  - Dados da empresa (razão social, CNPJ, etc.)
  - Regime tributário
  - Tipo de atividade
  - Parâmetros de alerta
""")


def parse_args(args):
    """Parse argumentos da linha de comando."""
    resultado = {"comando": None}
    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("--"):
            chave = arg[2:]
            if i + 1 < len(args) and not args[i+1].startswith("--"):
                resultado[chave] = args[i+1]
                i += 2
            else:
                resultado[chave] = True
                i += 1
        elif resultado["comando"] is None:
            resultado["comando"] = arg
            i += 1
        else:
            i += 1
    return resultado


def main():
    """Entry point principal."""
    args = parse_args(sys.argv[1:])
    comando = args.get("comando", "ajuda")

    try:
        if comando == "status":
            comando_status()
        elif comando == "diario":
            comando_diario()
        elif comando == "fechamento":
            mes = int(args["mes"]) if "mes" in args else None
            ano = int(args["ano"]) if "ano" in args else None
            regime = args.get("regime")
            comando_fechamento(mes, ano, regime)
        elif comando == "financeiro":
            tipo = args.get("tipo", "resumo")
            comando_financeiro(tipo)
        elif comando == "relatorio":
            tipo = args.get("tipo", "vendas")
            mes = int(args["mes"]) if "mes" in args else None
            ano = int(args["ano"]) if "ano" in args else None
            comando_relatorio(tipo, mes, ano)
        elif comando == "dashboard":
            comando_dashboard()
        elif comando in ("ajuda", "help", "--help", "-h"):
            comando_ajuda()
        else:
            print(f"Comando '{comando}' não reconhecido. Use 'ajuda' para ver os comandos disponíveis.")
            sys.exit(1)
    except Exception as e:
        print(f"\nERRO: {e}")
        print("Use 'python -m automacao.main ajuda' para ver os comandos disponíveis.")
        sys.exit(1)


if __name__ == "__main__":
    main()
