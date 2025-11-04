"""
Aplicação Flask Principal
Salvar como: backend/app.py
"""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
import sys
import os

# Adicionar o diretório pai ao path para imports funcionarem
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar rotas
from routes.auth_routes import auth_bp
from routes.discover_routes import discover_bp
from routes.profile_routes import profile_bp
from routes.chat_routes import chat_bp
from database import init_database

def create_app():
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui-mude-em-producao'
    app.config['JWT_SECRET_KEY'] = 'sua-chave-jwt-secreta-aqui-mude-em-producao'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
    
    # Habilitar CORS para permitir requisições do frontend
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5000", "http://127.0.0.1:5000"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Inicializar JWT
    jwt = JWTManager(app)
    
    # Registrar blueprints (rotas)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(discover_bp, url_prefix='/api/discover')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    
    # Rota de teste
    @app.route('/')
    def index():
        return {
            'message': 'TINTIN API está funcionando!',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'discover': '/api/discover'
            }
        }
    
    # Rota de health check
    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200
    
    return app


if __name__ == '__main__':
    # Inicializar o banco de dados
    print("🔧 Inicializando banco de dados...")
    init_database()
    
    # Criar e executar a aplicação
    app = create_app()
    print("🚀 Iniciando servidor Flask...")
    print("📍 Acesse: http://localhost:5000")
    print("📍 API: http://localhost:5000/api")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )