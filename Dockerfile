# Dockerfile para o Backend TINTIN
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivo de dependências
COPY configuração/requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Criar diretório para o banco de dados
RUN mkdir -p /app/data

# Expor a porta 5000
EXPOSE 5000

# Variáveis de ambiente
ENV FLASK_APP=backend/app.py
ENV PYTHONUNBUFFERED=1

# Comando para iniciar a aplicação
CMD ["python", "backend/app.py"]