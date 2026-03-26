# Sistema de Automação de Escritório com IA

## Visão Geral
Sistema de automação para tarefas diárias de escritório contábil/empresarial brasileiro.
Inclui fechamento tributário mensal (todos os regimes), controle financeiro, gestão de clientes e geração de relatórios.

## Estrutura do Projeto
```
automacao/                    # Código Python do sistema
├── main.py                   # Entry point - CLI unificada
├── config.py                 # Configurações e I/O de dados
├── financeiro/               # Contas a pagar/receber, fluxo de caixa, conciliação
├── tributario/               # Cálculos tributários (Simples, Presumido, Real, MEI)
├── relatorios/               # Geração de relatórios (vendas, faturamento, estoque)
├── clientes/                 # Cadastro, follow-up, cobranças
└── utils/                    # Formatadores BR e validadores (CPF, CNPJ)
dados/                        # JSONs com dados da empresa, clientes, transações
relatorios_gerados/           # Saída dos relatórios (TXT e HTML)
.github/workflows/            # GitHub Actions (diário, mensal, trigger remoto)
```

## Comandos Rápidos
```bash
python -m automacao.main status                              # Status geral
python -m automacao.main diario                              # Rotina diária
python -m automacao.main fechamento --mes 3 --ano 2026       # Fechamento tributário
python -m automacao.main fechamento --regime mei              # Fechamento MEI
python -m automacao.main financeiro --tipo fluxo             # Fluxo de caixa
python -m automacao.main relatorio --tipo vendas             # Relatório de vendas
python -m automacao.main relatorio --tipo faturamento        # Faturamento anual
```

## Regimes Tributários Suportados
- **Simples Nacional**: LC 123/2006, Anexos I-V, cálculo de DAS com alíquota efetiva
- **Lucro Presumido**: PIS/COFINS mensal + IRPJ/CSLL trimestral
- **Lucro Real**: PIS/COFINS não-cumulativo + IRPJ/CSLL sobre lucro ajustado
- **MEI**: DAS-MEI fixo mensal + controle de limite de faturamento

## Configuração da Empresa
Edite `dados/config_empresa.json` com os dados reais:
- `regime_tributario`: simples_nacional, lucro_presumido, lucro_real, mei
- `atividade_principal`: comercio, industria, servicos
- `cnpj`: CNPJ da empresa
- `configuracoes.alerta_vencimento_dias`: dias de antecedência para alertas

## Legislação
O módulo `automacao/tributario/legislacao.py` contém resumo da legislação brasileira.
O módulo `automacao/tributario/tabelas_aliquotas.py` contém as tabelas de alíquotas.

**A IA deve sempre verificar se as tabelas estão atualizadas com a legislação vigente.**
Fontes oficiais: gov.br/receitafederal, planalto.gov.br

## Dados
- `dados/transacoes.json`: Receitas e despesas
- `dados/clientes.json`: Base de clientes
- `dados/config_empresa.json`: Configuração da empresa

## GitHub Actions (Ativação Remota)
- **automacao-diaria.yml**: Roda automaticamente às 8h (Brasília) ou manualmente
- **fechamento-mensal.yml**: Roda no dia 1 de cada mês ou manualmente com parâmetros
- **trigger-remoto.yml**: Execução manual de qualquer tarefa via GitHub Actions

## Instruções para a IA
1. Ao iniciar sessão, execute `python -m automacao.main status` para ver o estado atual
2. Verifique se há contas vencidas ou próximas do vencimento
3. Mantenha as tabelas de alíquotas atualizadas conforme legislação vigente
4. Ao adicionar transações, valide CPF/CNPJ e datas
5. Gere relatórios sempre que solicitado e salve em `relatorios_gerados/`
6. Para fechamento tributário, confirme o regime com o usuário antes de calcular
