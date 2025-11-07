#!/bin/bash

# Script de Deploy Automatizado - TINTIN na EC2
# Execute este script na sua EC2 após conectar via SSH

set -e  # Parar em caso de erro

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🎓 TINTIN - Deploy Automático      ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker não encontrado!${NC}"
    echo -e "${YELLOW}Instalando Docker...${NC}"
    
    # Instalar Docker
    sudo yum update -y
    sudo yum install -y docker
    sudo service docker start
    sudo usermod -a -G docker ec2-user
    
    # Instalar Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    echo -e "${GREEN}✅ Docker instalado com sucesso!${NC}"
    echo -e "${YELLOW}⚠️  Faça logout e login novamente para aplicar permissões${NC}"
    exit 0
fi

echo -e "${GREEN}✅ Docker encontrado${NC}"

# Definir variáveis
REPO_URL="https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git"
PROJECT_DIR="/home/ec2-user/tintin"
BACKUP_DIR="/home/ec2-user/tintin-backup-$(date +%Y%m%d-%H%M%S)"

# Fazer backup se já existir
if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}📦 Fazendo backup da instalação anterior...${NC}"
    cp -r "$PROJECT_DIR" "$BACKUP_DIR"
    echo -e "${GREEN}✅ Backup criado em: $BACKUP_DIR${NC}"
fi

# Clonar ou atualizar repositório
if [ -d "$PROJECT_DIR/.git" ]; then
    echo -e "${BLUE}🔄 Atualizando repositório...${NC}"
    cd "$PROJECT_DIR"
    git fetch origin
    git reset --hard origin/main  # ou master, dependendo da sua branch
else
    echo -e "${BLUE}📥 Clonando repositório...${NC}"
    rm -rf "$PROJECT_DIR"
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

echo -e "${GREEN}✅ Código atualizado${NC}"

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
    echo -e "${BLUE}📝 Criando arquivo .env...${NC}"
    cat > .env << EOF
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
FLASK_ENV=production
EOF
    echo -e "${GREEN}✅ Arquivo .env criado${NC}"
fi

# Parar containers antigos
echo -e "${BLUE}🛑 Parando containers antigos...${NC}"
docker-compose down || true

# Remover imagens antigas (opcional)
echo -e "${BLUE}🧹 Limpando imagens antigas...${NC}"
docker system prune -f

# Build e iniciar containers
echo -e "${BLUE}🏗️  Construindo e iniciando containers...${NC}"
docker-compose up -d --build

# Aguardar containers iniciarem
echo -e "${YELLOW}⏳ Aguardando containers iniciarem...${NC}"
sleep 10

# Verificar status
echo -e "${BLUE}📊 Verificando status dos containers...${NC}"
docker-compose ps

# Inicializar banco de dados se necessário
echo -e "${BLUE}🗄️  Inicializando banco de dados...${NC}"
docker-compose exec -T tintin-app python -c "from backend.database import init_database; init_database()" || true

# Popular com dados de exemplo (opcional - comente se não quiser)
echo -e "${BLUE}🌱 Populando banco com dados de exemplo...${NC}"
docker-compose exec -T tintin-app python seed_database.py || true

# Verificar logs
echo -e "${BLUE}📋 Últimas linhas do log:${NC}"
docker-compose logs --tail=20

# Obter IP público da EC2
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✨ Deploy Concluído com Sucesso! ✨  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo -e ""
echo -e "${BLUE}🌐 Acesse a aplicação em:${NC}"
echo -e "   ${GREEN}http://$PUBLIC_IP${NC}"
echo -e ""
echo -e "${BLUE}📊 Comandos úteis:${NC}"
echo -e "   ${YELLOW}Ver logs:${NC}       docker-compose logs -f"
echo -e "   ${YELLOW}Reiniciar:${NC}      docker-compose restart"
echo -e "   ${YELLOW}Parar:${NC}          docker-compose down"
echo -e "   ${YELLOW}Atualizar:${NC}      ./deploy.sh"
echo -e ""
echo -e "${BLUE}🔒 Segurança:${NC}"
echo -e "   ${YELLOW}⚠️  Não esqueça de configurar o Security Group da EC2${NC}"
echo -e "   ${YELLOW}⚠️  Libere as portas 80 (HTTP) e 22 (SSH)${NC}"
echo -e ""