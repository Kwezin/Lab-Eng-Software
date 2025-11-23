#!/bin/bash

# Script para executar testes localmente antes de push
# Simula o ambiente da pipeline do GitHub Actions

set -e

echo "🧪 TINTIN - Test Runner Local"
echo "=============================="
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para printar com cor
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Verificar se está no diretório correto
if [ ! -f "backend/app.py" ]; then
    print_error "Execute este script da raiz do projeto!"
    exit 1
fi

# Criar diretório para banco de dados de teste
mkdir -p /tmp/test_db

# Configurar variáveis de ambiente
export DATABASE_PATH=/tmp/test_db/test_tintin.db
export FLASK_ENV=testing
export SECRET_KEY=test-secret-key-local

# 1. Verificar instalação de dependências
print_info "Verificando dependências..."
if ! python -c "import pytest" 2>/dev/null; then
    print_error "pytest não instalado. Instalando dependências..."
    pip install -r configuração/requirements.txt
    pip install pytest pytest-cov pytest-flask pytest-mock
fi
print_success "Dependências OK"
echo ""

# 2. Executar testes com cobertura
print_info "Executando testes..."
if pytest tests/ -v --cov=backend --cov-report=term-missing --cov-report=html --cov-report=xml; then
    print_success "Todos os testes passaram!"
else
    print_error "Alguns testes falharam!"
    exit 1
fi
echo ""

# 3. Verificar threshold de cobertura
print_info "Verificando cobertura mínima (70%)..."
if coverage report --fail-under=70; then
    print_success "Cobertura adequada!"
else
    print_error "Cobertura abaixo do mínimo (70%)!"
    exit 1
fi
echo ""

# 4. Lint checks (opcional, não bloqueia)
print_info "Executando verificações de lint..."

# Instalar ferramentas de lint se necessário
pip install -q flake8 black isort 2>/dev/null || true

# Flake8
if command -v flake8 &> /dev/null; then
    if flake8 backend/ --count --max-complexity=10 --max-line-length=127 --statistics; then
        print_success "Flake8 OK"
    else
        print_error "Flake8 encontrou problemas (não bloqueante)"
    fi
else
    print_info "Flake8 não instalado, pulando..."
fi

# Black
if command -v black &> /dev/null; then
    if black --check backend/; then
        print_success "Black OK"
    else
        print_error "Black encontrou problemas de formatação (não bloqueante)"
        print_info "Execute: black backend/ para corrigir"
    fi
else
    print_info "Black não instalado, pulando..."
fi

# Isort
if command -v isort &> /dev/null; then
    if isort --check-only backend/; then
        print_success "Isort OK"
    else
        print_error "Isort encontrou problemas nos imports (não bloqueante)"
        print_info "Execute: isort backend/ para corrigir"
    fi
else
    print_info "Isort não instalado, pulando..."
fi

echo ""
echo "=============================="
print_success "Pipeline local concluída com sucesso! 🎉"
print_info "Relatório de cobertura HTML: htmlcov/index.html"
print_info "Você pode fazer push com segurança!"
echo ""
