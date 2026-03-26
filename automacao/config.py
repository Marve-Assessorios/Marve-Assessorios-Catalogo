"""Configurações centrais do sistema de automação."""

import json
import os
from pathlib import Path

# Diretórios base
BASE_DIR = Path(__file__).resolve().parent.parent
DADOS_DIR = BASE_DIR / "dados"
RELATORIOS_DIR = BASE_DIR / "relatorios_gerados"
CONFIG_EMPRESA_PATH = DADOS_DIR / "config_empresa.json"
CLIENTES_PATH = DADOS_DIR / "clientes.json"
TRANSACOES_PATH = DADOS_DIR / "transacoes.json"

# Garantir que diretórios existam
DADOS_DIR.mkdir(exist_ok=True)
RELATORIOS_DIR.mkdir(exist_ok=True)


def carregar_config_empresa():
    """Carrega configuração da empresa do arquivo JSON."""
    if not CONFIG_EMPRESA_PATH.exists():
        config_padrao = {
            "razao_social": "Empresa Exemplo LTDA",
            "nome_fantasia": "Empresa Exemplo",
            "cnpj": "00.000.000/0001-00",
            "inscricao_estadual": "",
            "inscricao_municipal": "",
            "regime_tributario": "simples_nacional",
            "endereco": {
                "logradouro": "",
                "numero": "",
                "complemento": "",
                "bairro": "",
                "cidade": "",
                "estado": "",
                "cep": ""
            },
            "contato": {
                "telefone": "",
                "email": "",
                "whatsapp": ""
            },
            "configuracoes": {
                "moeda": "BRL",
                "fuso_horario": "America/Sao_Paulo",
                "dia_fechamento": 1,
                "alerta_vencimento_dias": 7
            }
        }
        salvar_json(CONFIG_EMPRESA_PATH, config_padrao)
        return config_padrao
    return carregar_json(CONFIG_EMPRESA_PATH)


def carregar_json(caminho):
    """Carrega arquivo JSON."""
    caminho = Path(caminho)
    if not caminho.exists():
        return {}
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_json(caminho, dados):
    """Salva dados em arquivo JSON."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def carregar_transacoes():
    """Carrega transações financeiras."""
    if not TRANSACOES_PATH.exists():
        dados_padrao = {"transacoes": [], "proximo_id": 1}
        salvar_json(TRANSACOES_PATH, dados_padrao)
        return dados_padrao
    return carregar_json(TRANSACOES_PATH)


def salvar_transacoes(dados):
    """Salva transações financeiras."""
    salvar_json(TRANSACOES_PATH, dados)


def carregar_clientes():
    """Carrega base de clientes."""
    if not CLIENTES_PATH.exists():
        dados_padrao = {"clientes": [], "proximo_id": 1}
        salvar_json(CLIENTES_PATH, dados_padrao)
        return dados_padrao
    return carregar_json(CLIENTES_PATH)


def salvar_clientes(dados):
    """Salva base de clientes."""
    salvar_json(CLIENTES_PATH, dados)
