"""
Configurações e fixtures para testes com pytest
"""

import pytest
import sys
import os
import tempfile
import sqlite3

# Adicionar backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app import create_app
from backend.database import init_database, DATABASE_PATH


@pytest.fixture
def test_db():
    """Cria um banco de dados temporário para testes"""
    # Criar arquivo temporário
    db_fd, db_path = tempfile.mkstemp()
    
    # Substituir o caminho do banco temporariamente
    import backend.database as db_module
    original_path = db_module.DATABASE_PATH
    db_module.DATABASE_PATH = db_path
    
    # Inicializar o banco
    init_database()
    
    yield db_path
    
    # Limpar
    os.close(db_fd)
    os.unlink(db_path)
    db_module.DATABASE_PATH = original_path


@pytest.fixture
def app(test_db):
    """Cria uma instância da aplicação Flask para testes"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    yield app


@pytest.fixture
def client(app):
    """Cliente de teste para fazer requisições HTTP"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Runner para comandos CLI"""
    return app.test_cli_runner()


@pytest.fixture
def db_connection(test_db):
    """Conexão com o banco de dados de teste"""
    conn = sqlite3.connect(test_db)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@pytest.fixture
def auth_headers(client):
    """Retorna headers de autenticação com token JWT válido"""
    def _get_headers(user_type='student'):
        # Registrar usuário
        response = client.post('/api/auth/register', json={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
            'user_type': user_type
        })
        data = response.get_json()
        token = data.get('token')
        return {'Authorization': f'Bearer {token}'}
    
    return _get_headers


@pytest.fixture
def create_user(client):
    """Helper para criar usuários de teste"""
    def _create_user(name='Test User', email='test@example.com', 
                     password='password123', user_type='student', **kwargs):
        user_data = {
            'name': name,
            'email': email,
            'password': password,
            'user_type': user_type,
            **kwargs
        }
        response = client.post('/api/auth/register', json=user_data)
        return response.get_json()
    
    return _create_user


@pytest.fixture
def create_teacher(create_user):
    """Helper para criar professor de teste"""
    def _create_teacher(name='Teacher User', email='teacher@example.com', **kwargs):
        return create_user(
            name=name,
            email=email,
            user_type='teacher',
            skills=[{'name': 'Python', 'description': 'Expert', 'level': 'advanced'}],
            **kwargs
        )
    
    return _create_teacher


@pytest.fixture
def create_student(create_user):
    """Helper para criar aluno de teste"""
    def _create_student(name='Student User', email='student@example.com', **kwargs):
        return create_user(
            name=name,
            email=email,
            user_type='student',
            interests=[{'name': 'Python', 'difficulty': 'beginner', 'description': 'Want to learn'}],
            **kwargs
        )
    
    return _create_student


@pytest.fixture
def create_match(client, db_connection):
    """Helper para criar um match entre dois usuários"""
    def _create_match(user1_id, user2_id):
        cursor = db_connection.cursor()
        cursor.execute(
            'INSERT INTO matches (user1_id, user2_id) VALUES (?, ?)',
            (min(user1_id, user2_id), max(user1_id, user2_id))
        )
        db_connection.commit()
        return cursor.lastrowid
    
    return _create_match
