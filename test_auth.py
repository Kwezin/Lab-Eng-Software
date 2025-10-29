"""
Testes Unitários para Autenticação
Salvar como: tests/test_auth.py

Para executar:
pytest tests/test_auth.py -v
"""

import pytest
import json
from datetime import datetime

# Fixture para cliente de teste
@pytest.fixture
def client():
    """Cria um cliente de teste Flask"""
    from backend.app import app
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        yield client


@pytest.fixture
def clean_database():
    """Limpa o banco de dados antes de cada teste"""
    import psycopg2
    
    conn = psycopg2.connect(
        host='localhost',
        database='tintin_db',
        user='postgres',
        password='postgres'
    )
    cur = conn.cursor()
    
    # Limpar tabelas na ordem correta (devido às foreign keys)
    cur.execute('DELETE FROM ratings')
    cur.execute('DELETE FROM messages')
    cur.execute('DELETE FROM matches')
    cur.execute('DELETE FROM swipes')
    cur.execute('DELETE FROM skills')
    cur.execute('DELETE FROM users')
    
    conn.commit()
    cur.close()
    conn.close()
    
    yield


class TestUserRegistration:
    """Testes de cadastro de usuário"""
    
    def test_register_success(self, client, clean_database):
        """Teste de cadastro bem-sucedido"""
        response = client.post('/api/auth/register',
            data=json.dumps({
                'name': 'João Silva',
                'email': 'joao@example.com',
                'password': 'senha123',
                'bio': 'Desenvolvedor Python'
            }),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        
        assert response.status_code == 201
        assert 'token' in data
        assert 'user_id' in data
        assert data['message'] == 'Usuário criado com sucesso'
        assert isinstance(data['user_id'], int)
        assert isinstance(data['token'], str)
    
    
    def test_register_missing_name(self, client, clean_database):
        """Teste de cadastro sem nome"""
        response = client.post('/api/auth/register',
            data=json.dumps({
                'email': 'teste@example.com',
                'password': 'senha123'
            }),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert 'error' in data
        assert 'obrigatórios' in data['error'].lower()
    
    
    def test_register_missing_email(self, client, clean_database):
        """Teste de cadastro sem email"""
        response = client.post('/api/auth/register',
            data=json.dumps({
                'name': 'João Silva',
                'password': 'senha123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    
    def test_register_missing_password(self, client, clean_database):
        """Teste de cadastro sem senha"""
        response = client.post('/api/auth/register',
            data=json.dumps({
                'name': 'João Silva',
                'email': 'joao@example.com'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    
    def test_register_invalid_email(self, client, clean_database):
        """Teste de cadastro com email inválido"""
        response = client.post('/api/auth/register',
            data=json.dumps({
                'name': 'João Silva',
                'email': 'email-invalido',
                'password': 'senha123'
            }),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert 'email inválido' in data['error'].lower()
    
    
    def test_register_short_password(self, client, clean_database):
        """Teste de cadastro com senha muito curta"""
        response = client.post('/api/auth/register',
            data=json.dumps({
                'name': 'João Silva',
                'email': 'joao@example.com',
                'password': '123'
            }),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert 'mínimo 6 caracteres' in data['error'].lower()
    
    
    def test_register_duplicate_email(self, client, clean_database):
        """Teste de cadastro com email duplicado"""
        # Primeiro cadastro
        client.post('/api/auth/register',
            data=json.dumps({
                'name': 'Usuário Um',
                'email': 'duplicate@example.com',
                'password': 'senha123'
            }),
            content_type='application/json'
        )
        
        # Segundo cadastro com mesmo email
        response = client.post('/api/auth/register',
            data=json.dumps({
                'name': 'Usuário Dois',
                'email': 'duplicate@example.com',
                'password': 'senha456'
            }),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        
        assert response.status_code == 409
        assert 'já cadastrado' in data['error'].lower()
    
    
    def test_register_email_case_insensitive(self, client, clean_database):
        """Teste de cadastro com email em diferentes casos"""
        # Cadastrar com email minúsculo
        client.post('/api/auth/register',
            data=json.dumps({
                'name': 'Usuário Um',
                'email': 'teste@example.com',
                'password': 'senha123'
            }),
            content_type='application/json'
        )
        
        # Tentar cadastrar com email em maiúsculo
        response = client.post('/api/auth/register',
            data=json.dumps({
                'name': 'Usuário Dois',
                'email': 'TESTE@EXAMPLE.COM',
                'password': 'senha456'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 409


class TestUserLogin:
    """Testes de login de usuário"""
    
    @pytest.fixture
    def registered_user(self, client, clean_database):
        """Cria um usuário registrado para testes de login"""
        response = client.post('/api/auth/register',
            data=json.dumps({
                'name': 'Maria Santos',
                'email': 'maria@example.com',
                'password': 'senha123'
            }),
            content_type='application/json'
        )
        return json.loads(response.data)
    
    
    def test_login_success(self, client, registered_user):
        """Teste de login bem-sucedido"""
        response = client.post('/api/auth/login',
            data=json.dumps({
                'email': 'maria@example.com',
                'password': 'senha123'
            }),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert 'token' in data
        assert 'user_id' in data
        assert 'name' in data
        assert data['name'] == 'Maria Santos'
    
    
    def test_login_wrong_password(self, client, registered_user):
        """Teste de login com senha incorreta"""
        response = client.post('/api/auth/login',
            data=json.dumps({
                'email': 'maria@example.com',
                'password': 'senhaerrada'
            }),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        
        assert response.status_code == 401
        assert 'incorretos' in data['error'].lower()
    
    
    def test_login_nonexistent_user(self, client, clean_database):
        """Teste de login com usuário inexistente"""
        response = client.post('/api/auth/login',
            data=json.dumps({
                'email': 'naoexiste@example.com',
                'password': 'senha123'
            }),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        
        assert response.status_code == 401
        assert 'incorretos' in data['error'].lower()
    
    
    def test_login_missing_email(self, client):
        """Teste de login sem email"""
        response = client.post('/api/auth/login',
            data=json.dumps({
                'password': 'senha123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    
    def test_login_missing_password(self, client):
        """Teste de login sem senha"""
        response = client.post('/api/auth/login',
            data=json.dumps({
                'email': 'teste@example.com'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    
    def test_login_empty_fields(self, client):
        """Teste de login com campos vazios"""
        response = client.post('/api/auth/login',
            data=json.dumps({
                'email': '',
                'password': ''
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400 or response.status_code == 401
    
    
    def test_login_email_case_insensitive(self, client, registered_user):
        """Teste de login com email em diferentes casos"""
        response = client.post('/api/auth/login',
            data=json.dumps({
                'email': 'MARIA@EXAMPLE.COM',
                'password': 'senha123'
            }),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert 'token' in data


class TestTokenValidation:
    """Testes de validação de token JWT"""
    
    @pytest.fixture
    def user_with_token(self, client, clean_database):
        """Cria um usuário e retorna o token"""
        response = client.post('/api/auth/register',
            data=json.dumps({
                'name': 'Pedro Alves',
                'email': 'pedro@example.com',
                'password': 'senha123'
            }),
            content_type='application/json'
        )
        return json.loads(response.data)
    
    
    def test_validate_valid_token(self, client, user_with_token):
        """Teste de validação de token válido"""
        response = client.get('/api/auth/validate',
            headers={'Authorization': f'Bearer {user_with_token["token"]}'}
        )
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['valid'] == True
            assert data['user_id'] == user_with_token['user_id']
    
    
    def test_validate_missing_token(self, client):
        """Teste de validação sem token"""
        response = client.get('/api/auth/validate')
        
        # Deve retornar 401 Unauthorized
        assert response.status_code == 401
    
    
    def test_validate_invalid_token(self, client):
        """Teste de validação com token inválido"""
        response = client.get('/api/auth/validate',
            headers={'Authorization': 'Bearer token-invalido-xyz'}
        )
        
        assert response.status_code in [401, 422]


# Executar testes se o arquivo for rodado diretamente
if __name__ == '__main__':
    pytest.main([__file__, '-v'])