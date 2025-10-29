"""
Rotas de Autenticação - Login e Registro
Salvar como: backend/routes/auth_routes.py
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import psycopg2
from psycopg2.extras import RealDictCursor

auth_bp = Blueprint('auth', __name__)

# Configuração do banco de dados
DB_CONFIG = {
    'host': 'localhost',
    'database': 'tintin_db',
    'user': 'postgres',
    'password': 'postgres',
    'port': '5432'
}

def get_db_connection():
    """Retorna uma conexão com o banco de dados"""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Rota de cadastro de novo usuário
    
    Body esperado:
    {
        "name": "Nome Completo",
        "email": "email@example.com",
        "password": "senha123",
        "bio": "Descrição opcional"
    }
    
    Retorna:
    {
        "message": "Usuário criado com sucesso",
        "token": "jwt_token",
        "user_id": 1
    }
    """
    data = request.get_json()
    
    # Validação dos campos obrigatórios
    if not all(k in data for k in ['name', 'email', 'password']):
        return jsonify({'error': 'Nome, email e senha são obrigatórios'}), 400
    
    # Validação básica de email
    if '@' not in data['email']:
        return jsonify({'error': 'Email inválido'}), 400
    
    # Validação de senha
    if len(data['password']) < 6:
        return jsonify({'error': 'Senha deve ter no mínimo 6 caracteres'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Criptografar senha
        password_hash = generate_password_hash(data['password'])
        
        # Inserir usuário no banco
        cur.execute(
            '''
            INSERT INTO users (name, email, password_hash, photo_url, bio) 
            VALUES (%s, %s, %s, %s, %s) 
            RETURNING id
            ''',
            (
                data['name'].strip(),
                data['email'].lower().strip(),
                password_hash,
                data.get('photo_url'),
                data.get('bio')
            )
        )
        
        user_id = cur.fetchone()['id']
        conn.commit()
        
        # Gerar token JWT (válido por 7 dias)
        token = create_access_token(
            identity=user_id,
            expires_delta=timedelta(days=7)
        )
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'token': token,
            'user_id': user_id
        }), 201
        
    except psycopg2.IntegrityError as e:
        conn.rollback()
        # Email já existe
        return jsonify({'error': 'Email já cadastrado'}), 409
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao cadastrar usuário: {e}")
        return jsonify({'error': 'Erro ao criar conta. Tente novamente.'}), 500
        
    finally:
        cur.close()
        conn.close()


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Rota de login de usuário
    
    Body esperado:
    {
        "email": "email@example.com",
        "password": "senha123"
    }
    
    Retorna:
    {
        "token": "jwt_token",
        "user_id": 1,
        "name": "Nome do Usuário"
    }
    """
    data = request.get_json()
    
    # Validação dos campos
    if not all(k in data for k in ['email', 'password']):
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Buscar usuário por email
        cur.execute(
            'SELECT id, name, email, password_hash FROM users WHERE email = %s',
            (data['email'].lower().strip(),)
        )
        user = cur.fetchone()
        
        # Verificar se usuário existe e senha está correta
        if user and check_password_hash(user['password_hash'], data['password']):
            # Gerar token JWT
            token = create_access_token(
                identity=user['id'],
                expires_delta=timedelta(days=7)
            )
            
            return jsonify({
                'token': token,
                'user_id': user['id'],
                'name': user['name']
            }), 200
        else:
            return jsonify({'error': 'Email ou senha incorretos'}), 401
            
    except Exception as e:
        print(f"Erro ao fazer login: {e}")
        return jsonify({'error': 'Erro ao fazer login. Tente novamente.'}), 500
        
    finally:
        cur.close()
        conn.close()


@auth_bp.route('/validate', methods=['GET'])
def validate_token():
    """
    Rota para validar se o token JWT ainda é válido
    Requer token no header: Authorization: Bearer <token>
    """
    from flask_jwt_extended import jwt_required, get_jwt_identity
    
    @jwt_required()
    def _validate():
        user_id = get_jwt_identity()
        return jsonify({
            'valid': True,
            'user_id': user_id
        }), 200
    
    return _validate()
