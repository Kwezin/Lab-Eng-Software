# 🎓 TINTIN - Plataforma de Conexão Professor-Aluno

## 📖 Sobre o Projeto

TINTIN é uma plataforma estilo "Tinder" para conectar professores e alunos. Professores cadastram as habilidades que podem ensinar, alunos cadastram o que querem aprender, e o sistema faz matching inteligente baseado em tags compatíveis.

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

## 🚀 Como Executar

### 1. Instalar Dependências

```bash
pip install flask flask-cors flask-jwt-extended
```

### 2. Inicializar Banco de Dados

```bash
# Criar banco de dados
python -c "from backend.database import init_database; init_database()"

# Popular com dados de teste
python seed_database.py
```

### 3. Iniciar Servidor

```bash
python backend/app.py
```

O servidor estará disponível em:
- Local: `http://localhost:5000`
- Frontend: `http://localhost:5000/menu.html`
- API: `http://localhost:5000/api`

### 4. Executar Testes

```bash
# Testes das novas funcionalidades
python test_new_features.py

# Teste de fluxo completo
python test_complete_flow.py
```

## 🔑 Credenciais de Teste

Após executar `seed_database.py`, você pode usar:

### Professores:
- `carlos@example.com` - Senha: `senha123` (Python, JavaScript)
- `maria@example.com` - Senha: `senha123` (React, SQL)
- `joao@example.com` - Senha: `senha123` (Figma, Ilustração)
- `ana@example.com` - Senha: `senha123` (Violão, Musicalização)
- `pedro@example.com` - Senha: `senha123` (Eletricidade)

### Alunos:
- `lucas@example.com` - Senha: `senha123` (Python, JavaScript)
- `julia@example.com` - Senha: `senha123` (Violão, Música)
- `ricardo@example.com` - Senha: `senha123` (Figma, UX)
- `fernanda@example.com` - Senha: `senha123` (Eletricidade)
- `gabriel@example.com` - Senha: `senha123` (React, SQL)

## 📡 API Endpoints

### Autenticação
- `POST /api/auth/register` - Registrar novo usuário
- `POST /api/auth/login` - Fazer login
- `GET /api/auth/validate` - Validar token

### Perfil
- `GET /api/profile/me` - Buscar perfil próprio
- `GET /api/profile/<user_id>` - Buscar perfil público
- `PUT /api/profile/update` - Atualizar perfil
- `POST /api/profile/complete` - Completar perfil (opcional)

### Descoberta
- `GET /api/discover/profiles` - Listar perfis disponíveis (com match score)
- `POST /api/discover/swipe` - Registrar swipe (like/skip)
- `GET /api/discover/matches` - Listar matches
- `GET /api/discover/stats` - Estatísticas do usuário

### Chat
- `POST /api/chat/send` - Enviar mensagem
- `GET /api/chat/messages/<match_id>` - Buscar mensagens de um chat
- `GET /api/chat/conversations` - Listar conversas
- `GET /api/chat/unread-count` - Contar mensagens não lidas
- `POST /api/chat/mark-read/<match_id>` - Marcar mensagens como lidas

## 🎯 Sistema de Tags

### Para Professores (Skills)
```json
{
  "name": "Python",
  "description": "10 anos de experiência",
  "level": "expert",
  "requires_evaluation": true
}
```

**Campos:**
- `name` - Nome da habilidade (obrigatório)
- `description` - Descrição da experiência
- `level` - Nível: `beginner`, `intermediate`, `advanced`, `expert`
- `requires_evaluation` - Se exige avaliação prévia (boolean)

### Para Alunos (Interests)
```json
{
  "name": "Python",
  "difficulty": "beginner",
  "description": "Quero aprender do zero",
  "desired_level": "intermediate",
  "requires_evaluation": false
}
```

**Campos:**
- `name` - Nome do interesse (obrigatório)
- `difficulty` - Nível atual: `beginner`, `intermediate`, `advanced`
- `description` - Descrição do objetivo
- `desired_level` - Nível que deseja atingir
- `requires_evaluation` - Se solicita avaliação antes de iniciar (boolean)

## 📊 Match Score

O sistema calcula um **match score** baseado na interseção de tags:

- Quando **student** busca **teachers**: compara `student.interests` com `teacher.skills`
- Quando **teacher** busca **students**: compara `teacher.skills` com `student.interests`
- Cada tag compatível adiciona +1 ao score
- Perfis são ordenados por score decrescente (mais relevantes primeiro)

**Exemplo:**
- Student quer aprender: `["Python", "JavaScript"]`
- Teacher ensina: `["Python", "JavaScript", "React"]`
- **Match Score: 2** ✨

## 🎨 Próximas Melhorias

### Backend
- [ ] Sistema de avaliações por skill específica
- [ ] Filtros avançados (localização, preço, idioma)
- [ ] Sistema de notificações em tempo real (WebSockets)
- [ ] Upload de fotos
- [ ] Verificação de email

### Frontend
- [ ] Atualizar formulário de registro com novos campos
- [ ] Exibir badges de avaliação (🔍) nas tags
- [ ] Mostrar match score nos cards
- [ ] Adicionar filtros de busca
- [ ] Melhorar UX do chat (scroll automático, typing indicator)
- [ ] Dashboard com estatísticas

## 📝 Changelog

Consulte [CHANGELOG.md](CHANGELOG.md) para ver o histórico de alterações detalhado.

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é parte da disciplina de Engenharia de Software.

---

Desenvolvido com 💜 pela equipe TINTIN
