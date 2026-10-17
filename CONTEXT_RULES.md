# CONTEXT_RULES: Regras de Governança para Agentes de IA

Estas regras são obrigatórias para qualquer assistente de IA que gere ou altere código neste repositório.

## Diretrizes Arquiteturais (Obrigatórias)

- Python 3.11+ como versão mínima.
- Type hints em todas as funções, métodos e parâmetros.
- Seguir o princípio Single Responsibility (SRP) e o código limpo (PEP 8).
- Documentação no padrão Google style docstrings para módulos, classes, funções e parâmetros.
- Funções pequenas, coesas e com um único propósito.
- Tratamento de exceções específico, com mensagens claras.
- Logs estruturados com o módulo padrão `logging`.
- Código legível e manutenível, com nomes de variáveis e funções descritivos.

## Proibições Explícitas

- Não utilizar bibliotecas externas não autorizadas (somente biblioteca padrão; `pytest` é permitido apenas nos testes).
- Não alterar, remover ou adaptar os cenários de teste fornecidos.
- Não modificar a estrutura de pastas definida na especificação.
- Não persistir dados em arquivos ou bancos de dados.
- Não alterar a assinatura (nome e parâmetros) das funções públicas sem autorização.
- Não gerar código sem testes correspondentes para novas funcionalidades.
- Não inserir código duplicado ou desnecessário.
- Não assumir comportamentos não especificados no contrato de negócio.
