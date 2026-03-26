"""Gestão de cadastro de clientes."""

from datetime import date
from ..config import carregar_clientes, salvar_clientes
from ..utils.validadores import validar_cpf, validar_cnpj, validar_email


def listar_clientes(status="ativo"):
    """Lista clientes filtrados por status."""
    dados = carregar_clientes()
    if status == "todos":
        return dados.get("clientes", [])
    return [c for c in dados.get("clientes", []) if c.get("status") == status]


def buscar_cliente(cliente_id=None, cpf_cnpj=None, nome=None):
    """Busca cliente por ID, CPF/CNPJ ou nome."""
    dados = carregar_clientes()
    for c in dados.get("clientes", []):
        if cliente_id and c["id"] == cliente_id:
            return c
        if cpf_cnpj and c.get("cpf_cnpj", "").replace(".", "").replace("-", "").replace("/", "") == cpf_cnpj.replace(".", "").replace("-", "").replace("/", ""):
            return c
        if nome and nome.lower() in c.get("nome", "").lower():
            return c
    return None


def adicionar_cliente(nome, cpf_cnpj, tipo="pessoa_fisica", email="", telefone="",
                      endereco="", observacoes=""):
    """Adiciona novo cliente."""
    # Validações
    erros = []
    if not nome or len(nome.strip()) < 2:
        erros.append("Nome é obrigatório (mínimo 2 caracteres)")

    if tipo == "pessoa_fisica" and cpf_cnpj:
        if not validar_cpf(cpf_cnpj):
            erros.append("CPF inválido")
    elif tipo == "pessoa_juridica" and cpf_cnpj:
        if not validar_cnpj(cpf_cnpj):
            erros.append("CNPJ inválido")

    if email and not validar_email(email):
        erros.append("E-mail inválido")

    if erros:
        return {"sucesso": False, "erros": erros}

    # Verificar duplicidade
    existente = buscar_cliente(cpf_cnpj=cpf_cnpj)
    if existente and cpf_cnpj:
        return {"sucesso": False, "erros": [f"Cliente já cadastrado com este CPF/CNPJ (ID: {existente['id']})"]}

    dados = carregar_clientes()
    novo_id = dados.get("proximo_id", 1)

    novo_cliente = {
        "id": novo_id,
        "nome": nome.strip(),
        "cpf_cnpj": cpf_cnpj,
        "tipo": tipo,
        "email": email,
        "telefone": telefone,
        "endereco": endereco,
        "data_cadastro": date.today().strftime("%Y-%m-%d"),
        "observacoes": observacoes,
        "status": "ativo"
    }

    dados["clientes"].append(novo_cliente)
    dados["proximo_id"] = novo_id + 1
    salvar_clientes(dados)

    return {"sucesso": True, "cliente": novo_cliente}


def atualizar_cliente(cliente_id, **campos):
    """Atualiza dados de um cliente."""
    dados = carregar_clientes()
    for c in dados["clientes"]:
        if c["id"] == cliente_id:
            for chave, valor in campos.items():
                if chave in c and chave != "id":
                    c[chave] = valor
            salvar_clientes(dados)
            return {"sucesso": True, "cliente": c}
    return {"sucesso": False, "erros": ["Cliente não encontrado"]}


def inativar_cliente(cliente_id):
    """Inativa um cliente."""
    return atualizar_cliente(cliente_id, status="inativo")


def resumo_clientes():
    """Gera resumo da base de clientes."""
    dados = carregar_clientes()
    clientes = dados.get("clientes", [])

    ativos = [c for c in clientes if c.get("status") == "ativo"]
    inativos = [c for c in clientes if c.get("status") == "inativo"]
    pf = [c for c in ativos if c.get("tipo") == "pessoa_fisica"]
    pj = [c for c in ativos if c.get("tipo") == "pessoa_juridica"]

    return {
        "total": len(clientes),
        "ativos": len(ativos),
        "inativos": len(inativos),
        "pessoa_fisica": len(pf),
        "pessoa_juridica": len(pj)
    }
