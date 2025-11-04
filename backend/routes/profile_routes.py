"""
Rotas de Perfil - Complementar cadastro com tipo de usuário
Salvar como: backend/routes/profile_routes.py
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db_connection

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/complete', methods=['POST'])
@jwt_required()
def complete_profile():
    """
    Completa o perfil do usuário após cadastro inicial
    
    Body esperado:
    {
        "user_type": "student" ou "teacher",
        "skills": [  // Se for teacher
            {"name": "Python", "description": "5 anos de experiência"},
            {"name": "Trocar Chuveiro", "description": "Eletricista"}
        ],
        "interests": [  // Se for student
            {
                "name": "Python", 
                "difficulty": "beginner", 
                "description": "Quero aprender o básico"
            }
        ]
    }
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if 'user_type' not in data:
        return jsonify({'error': 'Tipo de usuário é obrigatório'}), 400
    
    if data['user_type'] not in ['student', 'teacher']:
        return jsonify({'error': 'Tipo deve ser "student" ou "teacher"'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Atualizar tipo de usuário
        cursor.execute(
            'UPDATE users SET user_type = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (data['user_type'], current_user_id)
        )
        
        # Se for professor, adicionar habilidades
        if data['user_type'] == 'teacher' and 'skills' in data:
            if len(data['skills']) == 0:
                return jsonify({'error': 'Professores devem adicionar pelo menos uma habilidade'}), 400
            
            for skill in data['skills']:
                if not skill.get('name'):
                    continue
                    
                cursor.execute(
                    'INSERT INTO teacher_skills (user_id, skill_name, skill_description) VALUES (?, ?, ?)',
                    (current_user_id, skill['name'], skill.get('description', ''))
                )
        
        # Se for aluno, adicionar interesses
        elif data['user_type'] == 'student' and 'interests' in data:
            if len(data['interests']) == 0:
                return jsonify({'error': 'Alunos devem adicionar pelo menos um interesse'}), 400
            
            for interest in data['interests']:
                if not interest.get('name'):
                    continue
                    
                cursor.execute(
                    '''
                    INSERT INTO student_interests 
                    (user_id, interest_name, difficulty_level, description) 
                    VALUES (?, ?, ?, ?)
                    ''',
                    (
                        current_user_id,
                        interest['name'],
                        interest.get('difficulty', 'beginner'),
                        interest.get('description', '')
                    )
                )
        
        conn.commit()
        
        return jsonify({
            'message': 'Perfil completado com sucesso',
            'user_type': data['user_type']
        }), 200
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao completar perfil: {e}")
        return jsonify({'error': 'Erro ao salvar perfil'}), 500
        
    finally:
        conn.close()


@profile_bp.route('/me', methods=['GET'])
@jwt_required()
def get_my_profile():
    """Retorna o perfil completo do usuário autenticado"""
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Buscar dados do usuário
        cursor.execute(
            'SELECT id, name, email, bio, user_type, photo_url, created_at FROM users WHERE id = ?',
            (current_user_id,)
        )
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        profile = dict(user)
        
        # Se for professor, buscar habilidades
        if profile['user_type'] == 'teacher':
            cursor.execute(
                'SELECT skill_name, skill_description FROM teacher_skills WHERE user_id = ?',
                (current_user_id,)
            )
            profile['skills'] = [dict(s) for s in cursor.fetchall()]
        
        # Se for aluno, buscar interesses
        elif profile['user_type'] == 'student':
            cursor.execute(
                'SELECT interest_name, difficulty_level, description FROM student_interests WHERE user_id = ?',
                (current_user_id,)
            )
            profile['interests'] = [dict(i) for i in cursor.fetchall()]
        
        return jsonify(profile), 200
        
    except Exception as e:
        print(f"Erro ao buscar perfil: {e}")
        return jsonify({'error': 'Erro ao buscar perfil'}), 500
        
    finally:
        conn.close()


@profile_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_profile():
    """Atualiza informações do perfil"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Campos que podem ser atualizados
        if 'name' in data:
            cursor.execute(
                'UPDATE users SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (data['name'], current_user_id)
            )
        
        if 'bio' in data:
            cursor.execute(
                'UPDATE users SET bio = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (data['bio'], current_user_id)
            )
        
        if 'photo_url' in data:
            cursor.execute(
                'UPDATE users SET photo_url = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (data['photo_url'], current_user_id)
            )
        
        conn.commit()
        
        return jsonify({'message': 'Perfil atualizado com sucesso'}), 200
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao atualizar perfil: {e}")
        return jsonify({'error': 'Erro ao atualizar perfil'}), 500
        
    finally:
        conn.close()


@profile_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_profile(user_id):
    """Retorna o perfil público de outro usuário"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Buscar dados do usuário (sem email e senha)
        cursor.execute(
            'SELECT id, name, bio, user_type, photo_url FROM users WHERE id = ?',
            (user_id,)
        )
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        profile = dict(user)
        
        # Buscar habilidades/interesses conforme tipo
        if profile['user_type'] == 'teacher':
            cursor.execute(
                'SELECT skill_name, skill_description FROM teacher_skills WHERE user_id = ?',
                (user_id,)
            )
            profile['skills'] = [dict(s) for s in cursor.fetchall()]
        elif profile['user_type'] == 'student':
            cursor.execute(
                'SELECT interest_name, difficulty_level, description FROM student_interests WHERE user_id = ?',
                (user_id,)
            )
            profile['interests'] = [dict(i) for i in cursor.fetchall()]
        
        # Buscar média de avaliações
        cursor.execute(
            '''
            SELECT AVG(rating) as avg_rating, COUNT(*) as total_ratings
            FROM ratings
            WHERE rated_id = ?
            ''',
            (user_id,)
        )
        rating_data = cursor.fetchone()
        if rating_data and rating_data['avg_rating']:
            profile['avg_rating'] = round(rating_data['avg_rating'], 1)
            profile['total_ratings'] = rating_data['total_ratings']
        else:
            profile['avg_rating'] = None
            profile['total_ratings'] = 0
        
        return jsonify(profile), 200
        
    except Exception as e:
        print(f"Erro ao buscar perfil: {e}")
        return jsonify({'error': 'Erro ao buscar perfil'}), 500
        
    finally:
        conn.close()