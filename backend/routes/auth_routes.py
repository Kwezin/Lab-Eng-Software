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
    """
    Registro completo de usuário com perfil
    
    Body esperado:
    {
        "name": "Nome Completo",
        "email": "email@example.com",
        "password": "senha123",
        "user_type": "student" ou "teacher",
        "bio": "Descrição opcional",
        "photo_url": "URL opcional",
        "location": "Cidade, Estado",
        "languages": "Português, Inglês",
        "availability": "Noites e fins de semana",
        "price_per_hour": 50.00,
        "credentials": "Formação acadêmica",
        "skills": [  // Se for teacher
            {
                "name": "Python",
                "description": "5 anos de experiência",
                "level": "advanced",
                "requires_evaluation": false
            }
        ],
        "interests": [  // Se for student
            {
                "name": "Python",
                "difficulty": "beginner",
                "description": "Quero aprender programação",
                "desired_level": "intermediate",
                "requires_evaluation": false
            }
        ]
    }
    """
    data = request.get_json()
    
    # Validar campos obrigatórios
    if not all(k in data for k in ['name', 'email', 'password']):
        return jsonify({'error': 'Nome, email e senha são obrigatórios'}), 400
    
    if '@' not in data['email']:
        return jsonify({'error': 'Email inválido'}), 400
    
    if len(data['password']) < 6:
        return jsonify({'error': 'Senha deve ter no mínimo 6 caracteres'}), 400
    
    # Validar tipo de usuário
    user_type = data.get('user_type', 'student').lower()
    if user_type not in ['student', 'teacher']:
        return jsonify({'error': 'Tipo de usuário deve ser "student" ou "teacher"'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        password_hash = generate_password_hash(data['password'])
        print(f"📝 Registrando novo usuário: {data['name']} ({user_type})")
       
        # Inserir usuário com todos os campos opcionais
        cursor.execute(
            '''INSERT INTO users (name, email, password_hash, photo_url, bio, user_type, 
               location, languages, availability, price_per_hour, credentials) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                data['name'].strip(), 
                data['email'].lower().strip(), 
                password_hash, 
                data.get('photo_url'), 
                data.get('bio'),
                user_type,
                data.get('location'),
                data.get('languages'),
                data.get('availability'),
                data.get('price_per_hour'),
                data.get('credentials')
            )
        )
        print("✅ Usuário inserido com sucesso")
        user_id = cursor.lastrowid
        
        # Se for professor, adicionar habilidades
        if user_type == 'teacher' and 'skills' in data and len(data['skills']) > 0:
            for skill in data['skills']:
                if not skill.get('name'):
                    continue
                cursor.execute(
                    '''INSERT INTO teacher_skills (user_id, skill_name, skill_description, skill_level, requires_evaluation)
                       VALUES (?, ?, ?, ?, ?)''',
                    (
                        user_id,
                        skill['name'],
                        skill.get('description', ''),
                        skill.get('level'),
                        1 if skill.get('requires_evaluation') else 0
                    )
                )
                print(f"  ✅ Habilidade adicionada: {skill['name']}")
        
        # Se for aluno, adicionar interesses
        elif user_type == 'student' and 'interests' in data and len(data['interests']) > 0:
            for interest in data['interests']:
                if not interest.get('name'):
                    continue
                cursor.execute(
                    '''INSERT INTO student_interests (user_id, interest_name, difficulty_level, description, desired_level, requires_evaluation)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (
                        user_id,
                        interest['name'],
                        interest.get('difficulty', 'beginner'),
                        interest.get('description', ''),
                        interest.get('desired_level'),
                        1 if interest.get('requires_evaluation') else 0
                    )
                )
                print(f"  ✅ Interesse adicionado: {interest['name']}")
        
        conn.commit()
        
        token = create_access_token(identity=str(user_id), expires_delta=timedelta(days=7))
        
        return jsonify({
            'message': 'Usuário criado com sucesso', 
            'token': token, 
            'user_id': user_id,
            'user_type': user_type
        }), 201
        
    except sqlite3.IntegrityError:
        conn.rollback()
        return jsonify({'error': 'Email já cadastrado'}), 409
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
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
            token = create_access_token(identity=str(user['id']), expires_delta=timedelta(days=7))
            return jsonify({
                'token': token, 
                'user_id': user['id'], 
                'name': user['name'], 
                'user_type': user['user_type']
            }), 200
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