"""Formatadores para valores brasileiros (moeda, CPF, CNPJ, datas)."""

from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP


def formatar_moeda(valor, simbolo="R$"):
    """Formata valor numérico para moeda brasileira. Ex: 1234.56 -> R$ 1.234,56"""
    if isinstance(valor, (int, float)):
        valor = Decimal(str(valor))
    valor = valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    parte_inteira, parte_decimal = str(valor).split(".")
    parte_inteira = int(parte_inteira)
    sinal = ""
    if parte_inteira < 0:
        sinal = "-"
        parte_inteira = abs(parte_inteira)
    inteiro_formatado = f"{parte_inteira:,}".replace(",", ".")
    return f"{sinal}{simbolo} {inteiro_formatado},{parte_decimal}"


def formatar_cpf(cpf):
    """Formata CPF: 12345678901 -> 123.456.789-01"""
    cpf = ''.join(filter(str.isdigit, str(cpf)))
    if len(cpf) != 11:
        return cpf
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def formatar_cnpj(cnpj):
    """Formata CNPJ: 12345678000195 -> 12.345.678/0001-95"""
    cnpj = ''.join(filter(str.isdigit, str(cnpj)))
    if len(cnpj) != 14:
        return cnpj
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"


def formatar_data(data_obj, formato="dd/mm/aaaa"):
    """Formata data para padrão brasileiro."""
    if isinstance(data_obj, str):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                data_obj = datetime.strptime(data_obj, fmt).date()
                break
            except ValueError:
                continue
        else:
            return data_obj
    if isinstance(data_obj, datetime):
        data_obj = data_obj.date()
    if formato == "dd/mm/aaaa":
        return data_obj.strftime("%d/%m/%Y")
    elif formato == "extenso":
        meses = [
            "", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
        ]
        return f"{data_obj.day} de {meses[data_obj.month]} de {data_obj.year}"
    return data_obj.strftime("%d/%m/%Y")


def formatar_percentual(valor):
    """Formata valor como percentual brasileiro. Ex: 0.15 -> 15,00%"""
    pct = Decimal(str(valor)) * 100
    pct = pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{str(pct).replace('.', ',')}%"
