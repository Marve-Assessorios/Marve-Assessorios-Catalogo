"""Gerador de dashboard HTML interativo com gráficos."""

import json
from datetime import date, datetime
from ..config import carregar_config_empresa, carregar_transacoes, carregar_clientes, RELATORIOS_DIR
from ..financeiro.contas_pagar import resumo_contas_a_pagar, contas_vencendo
from ..financeiro.contas_receber import resumo_contas_a_receber, contas_a_vencer
from ..financeiro.fluxo_caixa import fluxo_caixa_mensal
from ..relatorios.vendas import vendas_periodo
from ..relatorios.faturamento import faturamento_mensal
from ..clientes.cadastro import resumo_clientes
from ..tributario.fechamento_mensal import fechamento
from ..utils.formatadores import formatar_moeda


def coletar_dados_dashboard():
    """Coleta todos os dados necessários para o dashboard."""
    hoje = date.today()
    config = carregar_config_empresa()

    pagar = resumo_contas_a_pagar()
    receber = resumo_contas_a_receber()
    fluxo = fluxo_caixa_mensal(hoje.month, hoje.year)
    vendas = vendas_periodo(hoje.month, hoje.year)
    fat_anual = faturamento_mensal(hoje.year)
    clientes = resumo_clientes()
    vencendo = contas_vencendo(15)
    a_vencer = contas_a_vencer(15)

    try:
        trib = fechamento()
    except Exception:
        trib = {"regime": config.get("regime_tributario", "N/A"), "impostos_a_pagar": 0}

    transacoes = carregar_transacoes()
    ultimas = sorted(
        transacoes.get("transacoes", []),
        key=lambda x: x.get("data", ""),
        reverse=True
    )[:10]

    return {
        "config": {
            "nome": config.get("nome_fantasia", config.get("razao_social", "Empresa")),
            "cnpj": config.get("cnpj", ""),
            "regime": config.get("regime_tributario", "").replace("_", " ").title(),
            "atividade": config.get("atividade_principal", ""),
        },
        "data_geracao": hoje.strftime("%d/%m/%Y"),
        "hora_geracao": datetime.now().strftime("%H:%M:%S"),
        "pagar": {
            "total_pendente": pagar["total_pendente"],
            "total_vencido": pagar["total_vencido"],
            "qtd_pendentes": pagar["qtd_pendentes"],
            "qtd_vencidas": pagar["qtd_vencidas"],
        },
        "receber": {
            "total_pendente": receber["total_pendente"],
            "total_atrasado": receber["total_atrasado"],
            "qtd_pendentes": receber["qtd_pendentes"],
            "qtd_atrasadas": receber["qtd_atrasadas"],
        },
        "fluxo": {
            "receitas": fluxo["total_receitas"],
            "despesas": fluxo["total_despesas"],
            "saldo": fluxo["saldo"],
        },
        "vendas": {
            "total": vendas["total_vendas"],
            "qtd": vendas["qtd_vendas"],
            "ticket_medio": vendas["ticket_medio"],
            "por_categoria": vendas["por_categoria"],
        },
        "faturamento_anual": {
            "meses": [m["nome_mes"] for m in fat_anual["meses"]],
            "receitas": [m["receitas"] for m in fat_anual["meses"]],
            "despesas": [m["despesas"] for m in fat_anual["meses"]],
            "total_receitas": fat_anual["total_receitas"],
            "total_despesas": fat_anual["total_despesas"],
            "lucro": fat_anual["lucro_bruto_anual"],
        },
        "clientes": clientes,
        "tributario": {
            "regime": trib.get("regime", "N/A"),
            "periodo": trib.get("periodo", "N/A"),
            "faturamento": trib.get("faturamento_mes", 0),
            "impostos": trib.get("impostos_a_pagar", 0),
        },
        "alertas_pagar": [
            {
                "descricao": c["descricao"],
                "valor": c["valor"],
                "vencimento": c["data_vencimento"],
                "dias": c.get("dias_restantes", 0),
                "vencida": c.get("vencida", False),
            }
            for c in vencendo
        ],
        "alertas_receber": [
            {
                "descricao": c["descricao"],
                "valor": c["valor"],
                "vencimento": c["data_vencimento"],
                "dias": c.get("dias_restantes", 0),
                "atrasada": c.get("atrasada", False),
            }
            for c in a_vencer
        ],
        "ultimas_transacoes": [
            {
                "data": t["data"],
                "tipo": t["tipo"],
                "descricao": t["descricao"],
                "valor": t["valor"],
                "status": t.get("status", "pendente"),
            }
            for t in ultimas
        ],
    }


def gerar_dashboard():
    """Gera o dashboard HTML completo e salva em relatorios_gerados/."""
    dados = coletar_dados_dashboard()
    dados_json = json.dumps(dados, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - {dados['config']['nome']}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #1e293b;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: rgba(255,255,255,0.95);
            border-radius: 16px;
            padding: 24px 32px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }}
        .header h1 {{
            font-size: 24px;
            color: #667eea;
        }}
        .header .info {{
            font-size: 13px;
            color: #64748b;
            text-align: right;
        }}
        .header .regime {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        .cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }}
        .card {{
            background: rgba(255,255,255,0.95);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        .card h3 {{
            font-size: 13px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
        }}
        .card .valor-principal {{
            font-size: 28px;
            font-weight: 700;
            color: #1e293b;
        }}
        .card .valor-principal.positivo {{ color: #10b981; }}
        .card .valor-principal.negativo {{ color: #ef4444; }}
        .card .detalhe {{
            font-size: 13px;
            color: #64748b;
            margin-top: 8px;
        }}
        .card .detalhe .alerta {{
            color: #ef4444;
            font-weight: 600;
        }}
        .graficos {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .grafico-container {{
            background: rgba(255,255,255,0.95);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        .grafico-container h3 {{
            font-size: 16px;
            color: #1e293b;
            margin-bottom: 16px;
        }}
        .tabela-container {{
            background: rgba(255,255,255,0.95);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            overflow-x: auto;
        }}
        .tabela-container h3 {{
            font-size: 16px;
            color: #1e293b;
            margin-bottom: 16px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            text-align: left;
            padding: 10px 12px;
            border-bottom: 2px solid #e2e8f0;
            font-size: 12px;
            color: #64748b;
            text-transform: uppercase;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #f1f5f9;
            font-size: 14px;
        }}
        tr:hover {{ background: #f8fafc; }}
        .badge {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        }}
        .badge-pago {{ background: #d1fae5; color: #065f46; }}
        .badge-pendente {{ background: #fef3c7; color: #92400e; }}
        .badge-vencida {{ background: #fee2e2; color: #991b1b; }}
        .badge-receita {{ background: #d1fae5; color: #065f46; }}
        .badge-despesa {{ background: #fee2e2; color: #991b1b; }}
        .trib-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
        }}
        .trib-card h3 {{
            font-size: 16px;
            margin-bottom: 16px;
            opacity: 0.9;
        }}
        .trib-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
        }}
        .trib-item {{
            background: rgba(255,255,255,0.15);
            border-radius: 12px;
            padding: 16px;
        }}
        .trib-item .label {{ font-size: 12px; opacity: 0.8; }}
        .trib-item .value {{ font-size: 22px; font-weight: 700; margin-top: 4px; }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: rgba(255,255,255,0.7);
            font-size: 12px;
        }}
        @media (max-width: 768px) {{
            .cards {{ grid-template-columns: 1fr; }}
            .graficos {{ grid-template-columns: 1fr; }}
            .header {{ flex-direction: column; text-align: center; }}
            .header .info {{ text-align: center; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1 id="empresa-nome"></h1>
                <div style="margin-top:4px">
                    <span>CNPJ: <span id="empresa-cnpj"></span></span>
                    <span class="regime" id="empresa-regime" style="margin-left:12px"></span>
                </div>
            </div>
            <div class="info">
                <div>Dashboard gerado em</div>
                <div style="font-size:18px;font-weight:700;color:#1e293b" id="data-geracao"></div>
            </div>
        </div>

        <div class="cards">
            <div class="card">
                <h3>Contas a Pagar</h3>
                <div class="valor-principal" id="pagar-total"></div>
                <div class="detalhe">
                    <span id="pagar-qtd"></span> pendentes
                    <span id="pagar-vencidas"></span>
                </div>
            </div>
            <div class="card">
                <h3>Contas a Receber</h3>
                <div class="valor-principal positivo" id="receber-total"></div>
                <div class="detalhe">
                    <span id="receber-qtd"></span> pendentes
                    <span id="receber-atrasadas"></span>
                </div>
            </div>
            <div class="card">
                <h3>Faturamento do M&ecirc;s</h3>
                <div class="valor-principal" id="fluxo-saldo"></div>
                <div class="detalhe">
                    Receitas: <span id="fluxo-receitas"></span> |
                    Despesas: <span id="fluxo-despesas"></span>
                </div>
            </div>
            <div class="card">
                <h3>Clientes</h3>
                <div class="valor-principal" id="clientes-total" style="color:#667eea"></div>
                <div class="detalhe">
                    Ativos: <span id="clientes-ativos"></span> |
                    PF: <span id="clientes-pf"></span> |
                    PJ: <span id="clientes-pj"></span>
                </div>
            </div>
        </div>

        <div class="trib-card">
            <h3>Fechamento Tribut&aacute;rio</h3>
            <div class="trib-grid">
                <div class="trib-item">
                    <div class="label">Regime</div>
                    <div class="value" id="trib-regime" style="font-size:16px"></div>
                </div>
                <div class="trib-item">
                    <div class="label">Per&iacute;odo</div>
                    <div class="value" id="trib-periodo" style="font-size:16px"></div>
                </div>
                <div class="trib-item">
                    <div class="label">Faturamento</div>
                    <div class="value" id="trib-fat"></div>
                </div>
                <div class="trib-item">
                    <div class="label">Impostos a Pagar</div>
                    <div class="value" id="trib-impostos"></div>
                </div>
            </div>
        </div>

        <div class="graficos">
            <div class="grafico-container">
                <h3>Faturamento Mensal</h3>
                <canvas id="grafico-faturamento"></canvas>
            </div>
            <div class="grafico-container">
                <h3>Vendas por Categoria</h3>
                <canvas id="grafico-categorias"></canvas>
            </div>
        </div>

        <div class="tabela-container">
            <h3>Alertas - Contas Pr&oacute;ximas do Vencimento</h3>
            <table>
                <thead>
                    <tr>
                        <th>Tipo</th>
                        <th>Descri&ccedil;&atilde;o</th>
                        <th>Valor</th>
                        <th>Vencimento</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="tabela-alertas"></tbody>
            </table>
            <div id="sem-alertas" style="text-align:center;padding:20px;color:#64748b;display:none">
                Nenhuma conta pr&oacute;xima do vencimento.
            </div>
        </div>

        <div class="tabela-container">
            <h3>&Uacute;ltimas Transa&ccedil;&otilde;es</h3>
            <table>
                <thead>
                    <tr>
                        <th>Data</th>
                        <th>Tipo</th>
                        <th>Descri&ccedil;&atilde;o</th>
                        <th>Valor</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="tabela-transacoes"></tbody>
            </table>
        </div>

        <div class="footer">
            Sistema de Automa&ccedil;&atilde;o de Escrit&oacute;rio com IA &mdash;
            Dashboard gerado automaticamente em <span id="footer-data"></span>
        </div>
    </div>

    <script>
    const D = {dados_json};

    function fmt(v) {{
        return 'R$ ' + Number(v).toLocaleString('pt-BR', {{minimumFractionDigits: 2, maximumFractionDigits: 2}});
    }}
    function fmtData(d) {{
        if (!d) return '-';
        const p = d.split('-');
        return p[2] + '/' + p[1] + '/' + p[0];
    }}

    // Header
    document.getElementById('empresa-nome').textContent = D.config.nome;
    document.getElementById('empresa-cnpj').textContent = D.config.cnpj;
    document.getElementById('empresa-regime').textContent = D.config.regime;
    document.getElementById('data-geracao').textContent = D.data_geracao + ' ' + D.hora_geracao;
    document.getElementById('footer-data').textContent = D.data_geracao;

    // Cards
    document.getElementById('pagar-total').textContent = fmt(D.pagar.total_pendente);
    document.getElementById('pagar-qtd').textContent = D.pagar.qtd_pendentes;
    if (D.pagar.qtd_vencidas > 0) {{
        document.getElementById('pagar-vencidas').innerHTML =
            ' | <span class="alerta">' + D.pagar.qtd_vencidas + ' vencida(s): ' + fmt(D.pagar.total_vencido) + '</span>';
        document.querySelector('#pagar-total').classList.add('negativo');
    }}

    document.getElementById('receber-total').textContent = fmt(D.receber.total_pendente);
    document.getElementById('receber-qtd').textContent = D.receber.qtd_pendentes;
    if (D.receber.qtd_atrasadas > 0) {{
        document.getElementById('receber-atrasadas').innerHTML =
            ' | <span class="alerta">' + D.receber.qtd_atrasadas + ' atrasada(s)</span>';
    }}

    const saldo = D.fluxo.saldo;
    document.getElementById('fluxo-saldo').textContent = fmt(saldo);
    document.getElementById('fluxo-saldo').classList.add(saldo >= 0 ? 'positivo' : 'negativo');
    document.getElementById('fluxo-receitas').textContent = fmt(D.fluxo.receitas);
    document.getElementById('fluxo-despesas').textContent = fmt(D.fluxo.despesas);

    document.getElementById('clientes-total').textContent = D.clientes.ativos + ' ativos';
    document.getElementById('clientes-ativos').textContent = D.clientes.ativos;
    document.getElementById('clientes-pf').textContent = D.clientes.pessoa_fisica;
    document.getElementById('clientes-pj').textContent = D.clientes.pessoa_juridica;

    // Tributario
    document.getElementById('trib-regime').textContent = D.tributario.regime.replace(/_/g,' ').toUpperCase();
    document.getElementById('trib-periodo').textContent = D.tributario.periodo;
    document.getElementById('trib-fat').textContent = fmt(D.tributario.faturamento);
    document.getElementById('trib-impostos').textContent = fmt(D.tributario.impostos);

    // Grafico Faturamento
    new Chart(document.getElementById('grafico-faturamento'), {{
        type: 'bar',
        data: {{
            labels: D.faturamento_anual.meses,
            datasets: [
                {{
                    label: 'Receitas',
                    data: D.faturamento_anual.receitas,
                    backgroundColor: 'rgba(16, 185, 129, 0.7)',
                    borderRadius: 6,
                }},
                {{
                    label: 'Despesas',
                    data: D.faturamento_anual.despesas,
                    backgroundColor: 'rgba(239, 68, 68, 0.7)',
                    borderRadius: 6,
                }}
            ]
        }},
        options: {{
            responsive: true,
            plugins: {{
                legend: {{ position: 'top' }},
            }},
            scales: {{
                y: {{
                    beginAtZero: true,
                    ticks: {{
                        callback: function(v) {{ return 'R$ ' + v.toLocaleString('pt-BR'); }}
                    }}
                }}
            }}
        }}
    }});

    // Grafico Categorias
    const cats = Object.entries(D.vendas.por_categoria);
    if (cats.length > 0) {{
        new Chart(document.getElementById('grafico-categorias'), {{
            type: 'doughnut',
            data: {{
                labels: cats.map(c => c[0]),
                datasets: [{{
                    data: cats.map(c => c[1]),
                    backgroundColor: ['#667eea','#10b981','#f59e0b','#ef4444','#8b5cf6','#06b6d4','#ec4899'],
                    borderWidth: 2,
                    borderColor: '#fff',
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ position: 'bottom' }},
                }}
            }}
        }});
    }} else {{
        document.getElementById('grafico-categorias').parentElement.innerHTML +=
            '<p style="text-align:center;color:#64748b;padding:40px">Sem dados de vendas no m&ecirc;s atual.</p>';
    }}

    // Tabela Alertas
    const alertas = [...D.alertas_pagar.map(a => ({{...a, tipo: 'Pagar'}})),
                     ...D.alertas_receber.map(a => ({{...a, tipo: 'Receber'}}))];
    alertas.sort((a, b) => a.dias - b.dias);
    const tBody = document.getElementById('tabela-alertas');
    if (alertas.length === 0) {{
        document.getElementById('sem-alertas').style.display = 'block';
    }} else {{
        alertas.forEach(a => {{
            const vencida = a.vencida || a.atrasada;
            const badge = vencida ? '<span class="badge badge-vencida">VENCIDA</span>'
                : '<span class="badge badge-pendente">' + a.dias + ' dias</span>';
            tBody.innerHTML += '<tr>' +
                '<td><span class="badge ' + (a.tipo === 'Pagar' ? 'badge-despesa' : 'badge-receita') + '">' + a.tipo + '</span></td>' +
                '<td>' + a.descricao + '</td>' +
                '<td>' + fmt(a.valor) + '</td>' +
                '<td>' + fmtData(a.vencimento) + '</td>' +
                '<td>' + badge + '</td></tr>';
        }});
    }}

    // Tabela Transacoes
    const tTrans = document.getElementById('tabela-transacoes');
    D.ultimas_transacoes.forEach(t => {{
        const tipoBadge = t.tipo === 'receita' ? 'badge-receita' : 'badge-despesa';
        const statusBadge = t.status === 'pago' ? 'badge-pago' : 'badge-pendente';
        tTrans.innerHTML += '<tr>' +
            '<td>' + fmtData(t.data) + '</td>' +
            '<td><span class="badge ' + tipoBadge + '">' + t.tipo + '</span></td>' +
            '<td>' + t.descricao + '</td>' +
            '<td>' + fmt(t.valor) + '</td>' +
            '<td><span class="badge ' + statusBadge + '">' + t.status + '</span></td></tr>';
    }});
    </script>
</body>
</html>"""

    caminho = RELATORIOS_DIR / "dashboard.html"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)

    return str(caminho)
