#!/bin/bash

# Script para iniciar o servidor Flask em background
# e mantê-lo rodando

cd /workspaces/Lab-Eng-Software

# Parar servidores existentes
pkill -9 -f "python.*app.py" 2>/dev/null
sleep 2

# Iniciar novo servidor em background
nohup python3 backend/app.py > server.log 2>&1 &
SERVER_PID=$!

echo "🚀 Servidor iniciado!"
echo "📍 PID: $SERVER_PID"
echo "📝 Log: tail -f server.log"
echo ""
echo "Para parar o servidor, execute:"
echo "  pkill -9 -f 'python.*app.py'"
echo ""

# Aguardar um pouco para o servidor iniciar
sleep 3

# Verificar se está rodando
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Servidor está rodando na porta 5000"
    echo "🌐 Acesse: http://localhost:5000"
else
    echo "❌ Erro ao iniciar o servidor"
    echo "📋 Últimas linhas do log:"
    tail -20 server.log
fi
