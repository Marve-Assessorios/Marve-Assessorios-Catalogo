"""Gerador de relatórios em formato HTML (para impressão/PDF via navegador)."""

from datetime import datetime
from pathlib import Path
from ..config import RELATORIOS_DIR, carregar_config_empresa


def gerar_html(titulo, conteudo_texto, nome_arquivo=None):
    """
    Gera um relatório em HTML a partir do conteúdo em texto.

    Args:
        titulo: Título do relatório
        conteudo_texto: Conteúdo em texto puro (será preservada a formatação)
        nome_arquivo: Nome do arquivo (sem extensão). Se None, gera automaticamente.

    Returns:
        Caminho do arquivo gerado
    """
    config = carregar_config_empresa()
    empresa = config.get("nome_fantasia", config.get("razao_social", "Empresa"))
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    if nome_arquivo is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"relatorio_{timestamp}"

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo} - {empresa}</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            margin: 40px;
            color: #333;
            background: #fff;
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #333;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .header p {{
            margin: 5px 0;
            font-size: 12px;
            color: #666;
        }}
        .content {{
            white-space: pre-wrap;
            font-size: 13px;
            line-height: 1.5;
        }}
        .footer {{
            margin-top: 40px;
            border-top: 1px solid #ccc;
            padding-top: 10px;
            font-size: 11px;
            color: #999;
            text-align: center;
        }}
        @media print {{
            body {{ margin: 20px; }}
            .footer {{ position: fixed; bottom: 20px; left: 0; right: 0; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{empresa}</h1>
        <p>{titulo}</p>
        <p>Gerado em: {data_geracao}</p>
    </div>
    <div class="content">{conteudo_texto}</div>
    <div class="footer">
        <p>Relatório gerado automaticamente pelo Sistema de Automação de Escritório</p>
        <p>{empresa} - {data_geracao}</p>
    </div>
</body>
</html>"""

    caminho = RELATORIOS_DIR / f"{nome_arquivo}.html"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)

    return str(caminho)


def salvar_relatorio_texto(titulo, conteudo, nome_arquivo=None):
    """Salva relatório em formato texto."""
    if nome_arquivo is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"relatorio_{timestamp}"

    caminho = RELATORIOS_DIR / f"{nome_arquivo}.txt"
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(f"{titulo}\n")
        f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
        f.write(conteudo)

    return str(caminho)
