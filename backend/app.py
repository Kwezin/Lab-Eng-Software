"""
Aplicação Flask Principal com Frontend Integrado
Salvar como: backend/app.py
"""

from flask import Flask, send_from_directory, request
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
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    
    # Configurações
    app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui-mude-em-producao'
    app.config['JWT_SECRET_KEY'] = 'sua-chave-jwt-secreta-aqui-mude-em-producao'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
    
    # Detectar o domínio (localhost ou Codespace)
    allowed_origins = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    # Se em Codespace, adicionar o domínio dinâmico
    codespace_domain = os.environ.get('CODESPACE_NAME')
    if codespace_domain:
        codespace_url = f"https://{codespace_domain}-5000.preview.app.github.dev"
        allowed_origins.append(codespace_url)
        print(f"🌐 Codespace detectado: {codespace_url}")
    
    # Habilitar CORS para permitir requisições do frontend
    CORS(app, 
        origins=allowed_origins,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        supports_credentials=True
    )
    
    print(f"✅ CORS Habilitado para: {allowed_origins}")
    
    # Inicializar JWT
    jwt = JWTManager(app)
    
    # Log de requisições para debug
    @app.before_request
    def log_request():
        print(f"📨 {request.method} {request.path}")
        print(f"   Origin: {request.origin}")
        if request.method in ['POST', 'PUT']:
            print(f"   Body: {request.get_json()}")
    
    # Registrar blueprints (rotas)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(discover_bp, url_prefix='/api/discover')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    
    # Rota de teste
    @app.route('/api')
    def api_index():
        return {
            'message': 'TINTIN API está funcionando!',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'discover': '/api/discover',
                'profile': '/api/profile',
                'chat': '/api/chat'
            }
        }
    
    # Rota de health check
    @app.route('/api/health')
    def health():
        return {'status': 'healthy'}, 200
    
    # Servir arquivos estáticos do frontend
    @app.route('/')
    def index():
        """Redireciona para a página de login"""
        return send_from_directory(app.static_folder, 'login.html')
    
    @app.route('/<path:filename>')
    def serve_static(filename):
        """Serve arquivos estáticos (HTML, CSS, JS, etc)"""
        return send_from_directory(app.static_folder, filename)
    
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
    print("📍 (Em Codespace, use a URL do seu preview)")
    print("")
    print("⏹️  Para parar: Ctrl+C")
    print("")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )