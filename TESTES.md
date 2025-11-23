# 🧪 Guia de Testes - TINTIN

## 📋 Índice
- [Instalação](#instalação)
- [Executando Testes](#executando-testes)
- [Cobertura de Código](#cobertura-de-código)
- [CI/CD Pipeline](#cicd-pipeline)
- [Estrutura de Testes](#estrutura-de-testes)

## 🚀 Instalação

### Instalar dependências de teste

```bash
pip install -r configuração/requirements.txt
pip install pytest pytest-cov pytest-flask pytest-mock
```

## ▶️ Executando Testes

### Executar todos os testes

```bash
pytest tests/ -v
```

### Executar teste específico

```bash
pytest tests/test_auth_routes.py -v
```

### Executar por marcadores

```bash
# Apenas testes de autenticação
pytest -m auth

# Apenas testes de perfil
pytest -m profile

# Apenas testes unitários
pytest -m unit
```

### Executar com saída detalhada

```bash
pytest tests/ -vv -s
```

## 📊 Cobertura de Código

### Gerar relatório de cobertura

```bash
pytest tests/ --cov=backend --cov-report=term-missing
```

### Gerar relatório HTML

```bash
pytest tests/ --cov=backend --cov-report=html
```

O relatório HTML estará disponível em `htmlcov/index.html`

### Gerar relatório XML (para CI)

```bash
pytest tests/ --cov=backend --cov-report=xml
```

### Verificar threshold de cobertura

```bash
pytest tests/ --cov=backend --cov-fail-under=70
```

## 🔄 CI/CD Pipeline

### Workflow do GitHub Actions

A pipeline é executada automaticamente em:
- ✅ Push para branches `main`, `develop`, `feature/*`
- ✅ Pull Requests para `main` e `develop`

### Jobs da Pipeline

1. **Test** 🧪
   - Executa em Python 3.9, 3.10, 3.11
   - Roda todos os testes com cobertura
   - Verifica threshold mínimo de 70%
   - Gera relatórios de cobertura

2. **Lint** 📝
   - Verifica qualidade do código com flake8
   - Verifica formatação com black
   - Verifica ordenação de imports com isort

3. **Security** 🔒
   - Escaneia código com bandit
   - Verifica vulnerabilidades com safety

4. **Deploy Ready** 🚀
   - Confirma que todos os testes passaram
   - Apenas executa na branch `main`

### Status da Pipeline

Você pode ver o status da pipeline em:
```
https://github.com/Kwezin/Lab-Eng-Software/actions
```

### Badge de Status

Adicione ao README.md principal:

```markdown
![Tests](https://github.com/Kwezin/Lab-Eng-Software/workflows/Tests%20CI%2FCD/badge.svg)
```

## 📁 Estrutura de Testes

```
tests/
├── conftest.py              # Fixtures compartilhadas
├── test_database.py         # Testes do banco de dados
├── test_auth_routes.py      # Testes de autenticação
├── test_profile_routes.py   # Testes de perfil
├── test_discover_routes.py  # Testes de descoberta
├── test_chat_routes.py      # Testes de chat
├── test_ratings_routes.py   # Testes de avaliações
└── test_app.py             # Testes da aplicação principal
```

## 🎯 Boas Práticas

### Antes de fazer commit

```bash
# Execute os testes
pytest tests/ -v

# Verifique a cobertura
pytest tests/ --cov=backend --cov-report=term-missing

# Formate o código
black backend/
isort backend/

# Verifique lint
flake8 backend/
```

### Antes de fazer push

```bash
# Execute todos os checks
pytest tests/ -v --cov=backend --cov-fail-under=70 && \
black --check backend/ && \
isort --check-only backend/ && \
flake8 backend/
```

## 🐛 Debug de Testes

### Executar com pdb

```bash
pytest tests/ --pdb
```

### Ver print statements

```bash
pytest tests/ -s
```

### Executar último teste que falhou

```bash
pytest --lf
```

### Executar testes que falharam primeiro

```bash
pytest --ff
```

## 📈 Métricas

### Cobertura Atual
- **Meta:** ≥ 70%
- **Branches:** main, develop
- **Python:** 3.9, 3.10, 3.11

### Relatórios
- Cobertura: `htmlcov/index.html`
- XML: `coverage.xml`
- Bandit: `bandit-report.json`

## 🔧 Troubleshooting

### Erro: ModuleNotFoundError

```bash
export PYTHONPATH="${PYTHONPATH}:/workspaces/Lab-Eng-Software"
```

### Erro: Database locked

```bash
rm -f /tmp/test_db/test_tintin.db
```

### Limpar cache do pytest

```bash
pytest --cache-clear
rm -rf .pytest_cache __pycache__ **/__pycache__
```

## 📚 Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [GitHub Actions](https://docs.github.com/en/actions)

## 🤝 Contribuindo

1. Crie testes para novas funcionalidades
2. Mantenha cobertura ≥ 70%
3. Execute testes localmente antes de push
4. Aguarde pipeline passar antes de merge

---

**Desenvolvido com ❤️ para manter qualidade e boas práticas DevOps**
