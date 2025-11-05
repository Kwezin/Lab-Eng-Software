"""
Rotas de Autenticação - Login e Registro com SQLite
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not all(k in data for k in ['name', 'email', 'password']):
        return jsonify({'error': 'Nome, email e senha são obrigatórios'}), 400
    
    if '@' not in data['email']:
        return jsonify({'error': 'Email inválido'}), 400
    
    if len(data['password']) < 6:
        return jsonify({'error': 'Senha deve ter no mínimo 6 caracteres'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        password_hash = generate_password_hash(data['password'])
        print("cheguei aqui")
       
        cursor.execute(
            'INSERT INTO users (name, email, password_hash, photo_url, bio, user_type) VALUES (?, ?, ?, ?, ?, ?)',
            (data['name'].strip(), data['email'].lower().strip(), password_hash, data.get('photo_url'), data.get('bio'), "student" )
        )
        print("deu certo o cursor")
        user_id = cursor.lastrowid
        conn.commit()
        
        token = create_access_token(identity=user_id, expires_delta=timedelta(days=7))
        
        return jsonify({'message': 'Usuário criado com sucesso', 'token': token, 'user_id': user_id}), 201
        
    except sqlite3.IntegrityError:
        conn.rollback()
        return jsonify({'error': 'Email já cadastrado'}), 409
    except Exception as e:
        conn.rollback()
        print(f"Erro: {e}")
        return jsonify({'error': 'Erro ao criar conta'}), 500
    finally:
        conn.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not all(k in data for k in ['email', 'password']):
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id, name, email, password_hash, user_type FROM users WHERE email = ?', (data['email'].lower().strip(),))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password_hash'], data['password']):
            token = create_access_token(identity=user['id'], expires_delta=timedelta(days=7))
            return jsonify({'token': token, 'user_id': user['id'], 'name': user['name'], 'user_type': user['user_type']}), 200
        else:
            return jsonify({'error': 'Email ou senha incorretos'}), 401
    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({'error': 'Erro ao fazer login'}), 500
    finally:
        conn.close()

@auth_bp.route('/validate', methods=['GET'])
@jwt_required()
def validate_token():
    user_id = get_jwt_identity()
    return jsonify({'valid': True, 'user_id': user_id}), 200