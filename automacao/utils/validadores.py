"""Validadores para CPF, CNPJ, e-mail e outros dados brasileiros."""

import re


def validar_cpf(cpf):
    """Valida CPF brasileiro. Retorna True se válido."""
    cpf = ''.join(filter(str.isdigit, str(cpf)))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    # Primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    d1 = 0 if resto < 2 else 11 - resto
    if int(cpf[9]) != d1:
        return False
    # Segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    d2 = 0 if resto < 2 else 11 - resto
    return int(cpf[10]) == d2


def validar_cnpj(cnpj):
    """Valida CNPJ brasileiro. Retorna True se válido."""
    cnpj = ''.join(filter(str.isdigit, str(cnpj)))
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False
    # Primeiro dígito verificador
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
    resto = soma % 11
    d1 = 0 if resto < 2 else 11 - resto
    if int(cnpj[12]) != d1:
        return False
    # Segundo dígito verificador
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
    resto = soma % 11
    d2 = 0 if resto < 2 else 11 - resto
    return int(cnpj[13]) == d2


def validar_email(email):
    """Valida formato de e-mail."""
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(padrao, str(email)))


def validar_telefone(telefone):
    """Valida telefone brasileiro (com ou sem DDD)."""
    tel = ''.join(filter(str.isdigit, str(telefone)))
    return len(tel) in (10, 11)


def validar_data(data_str, formato="%d/%m/%Y"):
    """Valida se string é uma data válida no formato especificado."""
    from datetime import datetime
    try:
        datetime.strptime(data_str, formato)
        return True
    except (ValueError, TypeError):
        return False
