# 🎓 TINTIN - Plataforma de Conexão Professor-Aluno

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📖 Sobre o Projeto

**TINTIN** é uma plataforma inovadora de matching inteligente que conecta professores e alunos de forma eficiente e personalizada. Inspirado no conceito de "swipe", o sistema permite que educadores compartilhem suas habilidades e estudantes encontrem exatamente o que precisam aprender, criando conexões significativas baseadas em compatibilidade real.

### 🌟 Impacto Social e Benefícios

A plataforma TINTIN traz benefícios transformadores para a sociedade:

#### 🎯 **Democratização do Acesso à Educação**
- **Reduz barreiras geográficas**: Conecta professores e alunos independentemente da localização
- **Facilita o acesso ao conhecimento**: Qualquer pessoa pode encontrar um professor adequado às suas necessidades
- **Educação inclusiva**: Suporta diferentes níveis de aprendizado e áreas de conhecimento

#### 💡 **Economia Compartilhada do Conhecimento**
- **Valoriza profissionais independentes**: Professores autônomos podem encontrar alunos sem intermediários
- **Networking educacional**: Cria uma comunidade de ensino-aprendizagem colaborativa
- **Transparência**: Sistema de avaliações garante qualidade e confiança

#### 🚀 **Eficiência e Personalização**
- **Matching inteligente**: Algoritmo conecta pessoas com interesses compatíveis
- **Economia de tempo**: Elimina buscas demoradas por professores adequados
- **Aprendizado customizado**: Cada aluno encontra o professor ideal para suas necessidades específicas

#### 🌍 **Desenvolvimento Social**
- **Fomenta a educação continuada**: Facilita o aprendizado ao longo da vida
- **Geração de renda**: Permite que profissionais monetizem seu conhecimento
- **Combate ao desemprego**: Cria oportunidades para educadores compartilharem expertise

## ✨ Funcionalidades
### 🔐 Autenticação
- Registro completo em uma única etapa
- Login com JWT
- Suporte para dois tipos de usuário: `teacher` e `student`

### 👤 Perfis Completos
- **Informações básicas**: nome, email, bio, foto
- **Localização**: cidade/estado
- **Idiomas**: idiomas que fala
- **Disponibilidade**: horários disponíveis
- **Preço por hora**: para professores
- **Credenciais**: formação acadêmica
- **Tags personalizadas**:
  - Professores: skills que podem ensinar
  - Alunos: interests que querem aprender
- **Avaliações**: sistema de ratings e comentários

### 🎯 Matching Inteligente
- **Match Score**: cálculo de compatibilidade baseado em interseção de tags
- Perfis mais relevantes aparecem primeiro
- Sistema de swipe (like/skip)
- Criação automática de matches mútuos

### 💬 Chat
- Mensagens entre matches
- Indicador de mensagens não lidas
- Lista de conversas ordenada por última mensagem

### 📊 Sistema de Avaliação
- Flag `requires_evaluation` nas tags
- Permite indicar se professor/aluno exige avaliação prévia
- Média de avaliações exibida nos perfis

## 🛠️ Tecnologias

### Backend
- **Flask** - Framework web Python
- **SQLite** - Banco de dados
- **Flask-JWT-Extended** - Autenticação com JWT
- **Flask-CORS** - Suporte a CORS

### Frontend
- HTML5
- CSS3 (com gradientes e animações)
- JavaScript Vanilla
- Fetch API para requisições

## 📁 Estrutura do Projeto

```
Lab-Eng-Software/
├── backend/
│   ├── __init__.py
│   ├── app.py                 # Aplicação Flask principal
│   ├── database.py            # Configuração do banco de dados
│   └── routes/
│       ├── __init__.py
│       ├── auth_routes.py     # Rotas de autenticação
│       ├── profile_routes.py  # Rotas de perfil
│       ├── discover_routes.py # Rotas de descoberta/matching
│       └── chat_routes.py     # Rotas de chat/mensagens
├── frontend/
│   ├── login.html             # Página de login/registro
│   ├── profile.html           # Visualização de perfil
│   ├── profile_edit.html      # Edição de perfil
│   ├── discover.html          # Descobrir perfis (swipe)
│   ├── matches.html           # Lista de matches
│   ├── chat.html              # Chat individual
│   └── menu.html              # Menu principal
├── seed_database.py           # Script para popular banco com dados de teste
├── test_new_features.py       # Testes das novas funcionalidades
├── test_complete_flow.py      # Teste de fluxo completo
├── CHANGELOG.md               # Documentação das alterações
└── README.md                  # Este arquivo
```

## � Pré-requisitos

Antes de iniciar, certifique-se de ter instalado em seu sistema:

### Opção 1: Instalação Local
- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **pip** (geralmente já vem com Python)
- **Git** (opcional, para clonar o repositório)

### Opção 2: Usando Docker (Recomendado para Produção)
- **Docker** - [Instalação](https://docs.docker.com/get-docker/)
- **Docker Compose** - [Instalação](https://docs.docker.com/compose/install/)

## 🚀 Como Executar

### 🐳 Método 1: Docker (Recomendado)

A forma mais simples e confiável de executar a aplicação:

```bash
# 1. Clone o repositório (se ainda não tiver)
git clone https://github.com/Kwezin/Lab-Eng-Software.git
cd Lab-Eng-Software

# 2. Configure variáveis de ambiente (opcional)
# Crie um arquivo .env com:
# SECRET_KEY=sua-chave-secreta
# JWT_SECRET_KEY=sua-chave-jwt-secreta

# 3. Construa e inicie os containers
docker-compose up -d

# 4. Acesse a aplicação
# Abra seu navegador em: http://localhost
```

**Comandos úteis do Docker:**
```bash
# Ver logs da aplicação
docker-compose logs -f

# Parar a aplicação
docker-compose down

# Reiniciar a aplicação
docker-compose restart

# Reconstruir após mudanças no código
docker-compose up -d --build
```

### 💻 Método 2: Instalação Local

Para desenvolvimento ou teste local:

#### 1. Instalar Dependências

```bash
# Clone o repositório
git clone https://github.com/Kwezin/Lab-Eng-Software.git
cd Lab-Eng-Software

# Crie um ambiente virtual (recomendado)
python -m venv venv

# Ative o ambiente virtual
# No Linux/Mac:
source venv/bin/activate
# No Windows:
venv\Scripts\activate

# Instale as dependências
pip install -r configuração/requirements.txt
```

#### 2. Inicializar Banco de Dados

```bash
# Criar banco de dados
python -c "from backend.database import init_database; init_database()"

# Popular com dados de teste (opcional)
python seed_database.py
```

#### 3. Executar a Aplicação

```bash
# Usando o script de inicialização
bash start_server.sh

# OU manualmente
python backend/app.py
```

#### 4. Acessar a Aplicação

Abra seu navegador em: **http://localhost:5000**

### 🧪 Executando Testes

```bash
# Executar todos os testes
bash run_tests.sh

# OU executar testes específicos
pytest test_auth.py -v
pytest test_complete_flow.py -v
pytest test_new_features.py -v
```

## 🎮 Guia de Uso Rápido

### Para Novos Usuários

1. **Acesse a plataforma** em http://localhost:5000 (local) ou seu domínio configurado

2. **Cadastre-se**:
   - Clique em "Registrar"
   - Escolha seu tipo: **Professor** ou **Aluno**
   - Preencha suas informações básicas

3. **Complete seu perfil**:
   - Adicione foto, bio e informações de contato
   - **Professores**: Liste suas habilidades/skills e preço por hora
   - **Alunos**: Liste seus interesses/interests que deseja aprender

4. **Descubra matches**:
   - Navegue até "Descobrir"
   - Veja perfis compatíveis com seu perfil
   - Dê **like** (❤️) em perfis interessantes ou **skip** (✕)

5. **Converse**:
   - Quando ambos derem like, um **match** é criado!
   - Acesse "Matches" para ver suas conexões
   - Inicie conversas pelo chat integrado

6. **Avalie**:
   - Após aulas, avalie seus professores/alunos
   - Construa sua reputação na plataforma

### 👨‍🏫 Para Professores

```
Perfil → Adicionar Skills → Descobrir Alunos → Match → Chat → Ensinar → Receber Avaliação
```

### 🎓 Para Alunos

```
Perfil → Adicionar Interests → Descobrir Professores → Match → Chat → Aprender → Avaliar
```

## 🔐 Credenciais de Teste

Se você executou o script `seed_database.py`, pode usar estas contas de teste:

### Professores
- **Email**: carlos@example.com | **Senha**: senha123 (Python, JavaScript)
- **Email**: maria@example.com | **Senha**: senha123 (React, SQL)
- **Email**: joao@example.com | **Senha**: senha123 (Figma, Ilustração)

### Alunos
- **Email**: lucas@example.com | **Senha**: senha123 (Quer aprender: Python, JavaScript)
- **Email**: julia@example.com | **Senha**: senha123 (Quer aprender: Violão, Música)

## 🛠️ Tecnologias Utilizadas

### Backend
- **[Flask 3.0.0](https://flask.palletsprojects.com/)** - Framework web Python minimalista e poderoso
- **[SQLite](https://www.sqlite.org/)** - Banco de dados relacional leve e eficiente
- **[Flask-JWT-Extended 4.6.0](https://flask-jwt-extended.readthedocs.io/)** - Autenticação JWT para APIs seguras
- **[Flask-CORS 4.0.0](https://flask-cors.readthedocs.io/)** - Gerenciamento de CORS para frontend-backend
- **[Werkzeug 3.0.1](https://werkzeug.palletsprojects.com/)** - Utilitários WSGI e segurança de senhas

### Frontend
- **HTML5** - Estrutura semântica moderna
- **CSS3** - Estilização com gradientes, animações e responsividade
- **JavaScript (Vanilla)** - Interatividade sem dependências externas
- **Fetch API** - Requisições HTTP assíncronas

### DevOps
- **Docker** - Containerização da aplicação
- **Docker Compose** - Orquestração de containers
- **pytest** - Framework de testes automatizados

## 📁 Estrutura Detalhada do Projeto

```
Lab-Eng-Software/
├── 📁 backend/                     # Código do servidor
│   ├── app.py                      # Aplicação Flask principal
│   ├── database.py                 # Configuração e modelos do banco
│   ├── __init__.py                 # Inicialização do pacote
│   └── 📁 routes/                  # Módulos de rotas da API
│       ├── auth_routes.py          # Autenticação (registro/login)
│       ├── profile_routes.py       # Gerenciamento de perfis
│       ├── discover_routes.py      # Sistema de descoberta e matching
│       ├── chat_routes.py          # Chat e mensagens
│       └── ratings_routes.py       # Sistema de avaliações
│
├── 📁 frontend/                    # Interface do usuário
│   ├── login.html                  # Login e registro
│   ├── menu.html                   # Dashboard principal
│   ├── profile.html                # Visualização de perfil
│   ├── profile_edit.html           # Edição de perfil
│   ├── discover.html               # Swipe e descoberta
│   ├── matches.html                # Lista de conexões
│   └── chat.html                   # Interface de chat
│
├── 📁 tests/                       # Testes automatizados
│   ├── conftest.py                 # Configuração pytest
│   ├── test_database.py            # Testes de banco
│   ├── test_auth.py                # Testes de autenticação
│   ├── test_complete_flow.py       # Testes de integração
│   └── test_new_features.py        # Testes de novas features
│
├── 📁 configuração/                # Arquivos de configuração
│   ├── requirements.txt            # Dependências Python
│   ├── start.sh                    # Script de inicialização (Linux/Mac)
│   └── start.bat                   # Script de inicialização (Windows)
│
├── 📄 docker-compose.yml           # Configuração Docker Compose
├── 📄 Dockerfile                   # Imagem Docker da aplicação
├── 📄 seed_database.py             # Popular banco com dados de teste
├── 📄 start_server.sh              # Script para iniciar servidor
├── 📄 run_tests.sh                 # Script para executar testes
├── 📄 deploy.sh                    # Script de deploy
├── 📄 pytest.ini                   # Configuração de testes
│
└── 📄 README.md                    # Este arquivo
```

## 🌐 API Endpoints

### Autenticação
- `POST /api/auth/register` - Registrar novo usuário
- `POST /api/auth/login` - Fazer login

### Perfil
- `GET /api/profile` - Obter perfil do usuário logado
- `PUT /api/profile` - Atualizar perfil
- `GET /api/profile/<user_id>` - Visualizar perfil de outro usuário

### Descoberta e Matching
- `GET /api/discover` - Listar perfis para descobrir
- `POST /api/interactions` - Registrar like/skip
- `GET /api/matches` - Listar matches do usuário

### Chat
- `GET /api/matches/<match_id>/messages` - Obter mensagens de um match
- `POST /api/matches/<match_id>/messages` - Enviar mensagem
- `PUT /api/matches/<match_id>/read` - Marcar mensagens como lidas

### Avaliações
- `POST /api/ratings` - Avaliar usuário
- `GET /api/ratings/<user_id>` - Obter avaliações de um usuário

## 🔧 Configuração Avançada

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto para configurações personalizadas:

```env
# Segurança
SECRET_KEY=sua-chave-secreta-super-segura-aqui
JWT_SECRET_KEY=sua-chave-jwt-super-segura-aqui

# Flask
FLASK_ENV=production
FLASK_DEBUG=0

# Banco de Dados
DATABASE_PATH=/app/data/database.db

# Servidor
PORT=5000
HOST=0.0.0.0
```

### Deploy em Produção

Para deploy, consulte o arquivo [deploy.sh](deploy.sh) que contém scripts automatizados.

**Recomendações de segurança para produção:**
1. ✅ Altere `SECRET_KEY` e `JWT_SECRET_KEY`
2. ✅ Configure HTTPS/SSL
3. ✅ Use um banco de dados robusto (PostgreSQL/MySQL)
4. ✅ Configure backups automáticos
5. ✅ Implemente rate limiting
6. ✅ Configure monitoramento e logs

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👥 Autores

- **Kwezin** - [GitHub](https://github.com/Kwezin)

## 📞 Suporte

Se encontrar problemas ou tiver dúvidas:

1. Verifique a [documentação completa](IMPLEMENTACAO_COMPLETA.md)
2. Consulte os [testes](TESTES.md) para exemplos de uso
3. Abra uma [issue no GitHub](https://github.com/Kwezin/Lab-Eng-Software/issues)

## 🎯 Roadmap Futuro

- [ ] Notificações push em tempo real
- [ ] Filtros avançados de busca
- [ ] Sistema de pagamento integrado
- [ ] App mobile (React Native)
- [ ] Videochamadas integradas
- [ ] Gamificação e badges
- [ ] Dashboard de estatísticas para professores
- [ ] Sistema de agendamento de aulas

---

⭐ **Se este projeto te ajudou, considere dar uma estrela no GitHub!**

Desenvolvido com ❤️ para democratizar o acesso à educação
