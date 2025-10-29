mkdir -p backend/routes
mkdir -p frontend
mkdir -p tests

# Criar arquivos __init__.py se não existirem
touch backend/__init__.py
touch backend/routes/__init__.py

# Inicializar banco de dados
echo "🗄️  Inicializando banco de dados..."
python backend/database.py

echo ""
echo "✅ Ambiente preparado!"
echo ""
echo "🚀 Iniciando servidor Flask..."
echo "📍 Backend: http://localhost:5000"
echo "📍 Frontend: Abra frontend/login.html no navegador"
echo ""
echo "⏹️  Para parar: Ctrl+C"
echo ""

# Iniciar aplicação
python backend/app.py