# 🚀 Configuração da Pipeline CI/CD - GitHub Actions

## ✅ Pipeline Criada com Sucesso!

A pipeline foi configurada e incluirá os seguintes badges no README:

```markdown
![Tests CI/CD](https://github.com/Kwezin/Lab-Eng-Software/workflows/Tests%20CI%2FCD/badge.svg)
![Coverage](https://img.shields.io/codecov/c/github/Kwezin/Lab-Eng-Software)
![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue)
```

## 🔄 Quando a Pipeline Executa

A pipeline executa automaticamente em:
- ✅ `git push` para branches: `main`, `develop`, `feature/*`
- ✅ Pull Requests para: `main`, `develop`

## 📋 Jobs da Pipeline

### 1️⃣ Test Job (Testes Unitários)
- **Matriz:** Python 3.9, 3.10, 3.11
- **Ações:**
  - Checkout do código
  - Instalação de dependências
  - Execução de todos os testes
  - Geração de relatórios de cobertura
  - Upload para Codecov
  - Verificação de cobertura mínima (70%)

### 2️⃣ Lint Job (Qualidade de Código)
- **Ferramentas:**
  - `flake8` - Verificação de estilo e erros
  - `black` - Formatação de código
  - `isort` - Ordenação de imports

### 3️⃣ Security Job (Segurança)
- **Ferramentas:**
  - `bandit` - Análise de segurança do código
  - `safety` - Verificação de vulnerabilidades nas dependências

### 4️⃣ Deploy Ready (Aprovação)
- **Condição:** Apenas em `main`
- **Requisitos:** Todos os jobs anteriores devem passar
- **Resultado:** Confirmação que o código está pronto para produção

## 🎯 Cobertura de Código

### Meta de Cobertura
- **Mínimo exigido:** 70%
- **Falha CI se:** Cobertura < 70%

### Relatórios Gerados
- Terminal (--cov-report=term-missing)
- HTML (htmlcov/index.html)
- XML (coverage.xml) - para Codecov

## 🛠️ Executar Localmente

### Opção 1: Script Automatizado
```bash
./run_tests.sh
```

### Opção 2: Comandos Manuais
```bash
# Instalar dependências
pip install pytest pytest-cov pytest-flask pytest-mock

# Executar testes
pytest tests/ -v --cov=backend --cov-report=term-missing

# Verificar cobertura
coverage report --fail-under=70

# Lint
flake8 backend/
black --check backend/
isort --check-only backend/
```

## 📊 Visualizar Resultados

### No GitHub
1. Acesse: https://github.com/Kwezin/Lab-Eng-Software/actions
2. Veja todas as execuções da pipeline
3. Clique em uma execução para ver detalhes

### Artifacts Disponíveis
- Relatórios de cobertura HTML
- Relatórios de segurança Bandit
- Logs de execução

## 🔒 Política de Branch Protection (Recomendado)

Configure no GitHub para exigir que testes passem antes de merge:

1. Settings → Branches → Add rule
2. Branch name pattern: `main`
3. ✅ Require status checks to pass before merging
4. ✅ Require branches to be up to date before merging
5. Selecione: `test`, `lint`, `security`

## 📝 Arquivos Criados

```
.github/
└── workflows/
    └── tests.yml          # Pipeline principal

pytest.ini                 # Configuração do pytest
run_tests.sh              # Script para testes locais
TESTES.md                 # Documentação completa
.gitignore                # Ignora arquivos de teste
```

## 🚀 Próximos Passos

1. **Commit e Push dos arquivos da pipeline:**
```bash
git add .github/workflows/tests.yml pytest.ini run_tests.sh TESTES.md .gitignore
git commit -m "feat: adiciona pipeline CI/CD com testes automatizados"
git push origin main
```

2. **Verifique a primeira execução:**
   - Acesse Actions no GitHub
   - Veja a pipeline executando

3. **Configure Codecov (Opcional):**
   - Visite: https://codecov.io/
   - Conecte seu repositório
   - Configure token em Secrets se repositório privado

4. **Adicione badges ao README.md:**
```markdown
![Tests CI/CD](https://github.com/Kwezin/Lab-Eng-Software/workflows/Tests%20CI%2FCD/badge.svg)
```

## ✨ Benefícios

- ✅ Testes automáticos em cada push
- ✅ Previne código quebrado na main
- ✅ Cobertura de código garantida
- ✅ Verificações de segurança
- ✅ Qualidade de código consistente
- ✅ Deploy apenas com testes passando
- ✅ Múltiplas versões Python testadas

## 🆘 Troubleshooting

### Pipeline falha após push
1. Veja logs no Actions
2. Execute `./run_tests.sh` localmente
3. Corrija erros encontrados
4. Faça novo commit e push

### Erro de permissão no GitHub Actions
- Verifique Settings → Actions → General
- Enable: "Read and write permissions"

### Codecov não recebe relatórios
- Configure CODECOV_TOKEN nos Secrets
- Verifique conexão do repositório

---

**Pipeline configurada seguindo melhores práticas DevOps! 🎉**
