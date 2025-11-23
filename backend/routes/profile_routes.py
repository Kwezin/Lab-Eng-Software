"""
Rotas de Perfil - Complementar cadastro com tipo de usuário
Salvar como: backend/routes/profile_routes.py
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database import get_db_connection

profile_bp = Blueprint('profile', __name__)


def sanitize_postal_code(value):
    if value is None:
        return None
    digits = ''.join(filter(str.isdigit, str(value)))
    return digits[:8] if digits else None


def normalize_user_field(field, value):
    if value is None:
        return None

    if field == 'postal_code':
        return sanitize_postal_code(value)

    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return None
        if field == 'address_state':
            return cleaned[:2].upper()
        return cleaned

    return value


@profile_bp.route('/complete', methods=['POST'])
@jwt_required()
def complete_profile():
    """
    Completa o perfil do usuário após cadastro inicial
    
    Body esperado:
    {
        "user_type": "student" ou "teacher",
        "skills": [  // Se for teacher
            {"name": "Python", "description": "5 anos de experiência", "level": "advanced", "requires_evaluation": false}
        ],
        "interests": [  // Se for student
            {
                "name": "Python", 
                "difficulty": "beginner", 
                "description": "Quero aprender o básico",
                "desired_level": "beginner",
                "requires_evaluation": false
            }
        ],
        // Campos adicionais opcionais: location, languages, availability, price_per_hour, credentials
    }
    """
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    print(f"📥 Dados recebidos: {data}")
    print(f"👤 User ID: {current_user_id}")
    
    if 'user_type' not in data:
        return jsonify({'error': 'Tipo de usuário é obrigatório'}), 400
    
    if data['user_type'] not in ['student', 'teacher']:
        return jsonify({'error': 'Tipo deve ser "student" ou "teacher"'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Atualizar tipo de usuário e possíveis campos adicionais
        update_fields = ['user_type']
        update_values = [data['user_type']]

        # Campos opcionais que podem vir no body
        optional_user_fields = [
            'name',
            'bio',
            'photo_url',
            'location',
            'languages',
            'availability',
            'price_per_hour',
            'credentials',
            'postal_code',
            'address_street',
            'address_number',
            'address_complement',
            'address_neighborhood',
            'address_city',
            'address_state'
        ]
        for f in optional_user_fields:
            if f in data:
                normalized_value = normalize_user_field(f, data.get(f))
                if f == 'postal_code' and normalized_value and len(normalized_value) != 8:
                    return jsonify({'error': 'Informe um CEP válido com 8 dígitos.'}), 400
                update_fields.append(f)
                update_values.append(normalized_value)

        # construir a query dinâmica para atualizar usuário
        set_clause = ', '.join([f + ' = ?' for f in update_fields]) + ', updated_at = CURRENT_TIMESTAMP'
        cursor.execute(
            f'UPDATE users SET {set_clause} WHERE id = ?',
            tuple(update_values) + (current_user_id,)
        )
        print(f"✅ Tipo de usuário atualizado para: {data['user_type']}")
        
        # Se for professor, adicionar habilidades
        if data['user_type'] == 'teacher' and 'skills' in data:
            if len(data['skills']) == 0:
                return jsonify({'error': 'Professores devem adicionar pelo menos uma habilidade'}), 400

            for skill in data['skills']:
                if not skill.get('name'):
                    continue

                cursor.execute(
                    '''
                    INSERT INTO teacher_skills (user_id, skill_name, skill_description, skill_level, requires_evaluation)
                    VALUES (?, ?, ?, ?, ?)
                    ''',
                    (
                        current_user_id,
                        skill['name'],
                        skill.get('description', ''),
                        skill.get('level'),
                        1 if skill.get('requires_evaluation') else 0
                    )
                )
                print(f"✅ Habilidade adicionada: {skill['name']}")
        
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
                    (user_id, interest_name, difficulty_level, description, desired_level, requires_evaluation) 
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        current_user_id,
                        interest['name'],
                        interest.get('difficulty', 'beginner'),
                        interest.get('description', ''),
                        interest.get('desired_level'),
                        1 if interest.get('requires_evaluation') else 0
                    )
                )
                print(f"✅ Interesse adicionado: {interest['name']}")
        
        conn.commit()
        print("✅ Perfil completado com sucesso!")
        
        return jsonify({
            'message': 'Perfil completado com sucesso',
            'user_type': data['user_type']
        }), 200
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao completar perfil: {e}")
        return jsonify({'error': f'Erro ao salvar perfil: {str(e)}'}), 500
        
    finally:
        conn.close()


@profile_bp.route('/me', methods=['GET'])
@jwt_required()
def get_my_profile():
    """Retorna o perfil completo do usuário autenticado"""
    current_user_id = int(get_jwt_identity())
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Buscar dados do usuário
        cursor.execute(
            '''SELECT id, name, email, bio, user_type, photo_url, location, languages, availability,
                      price_per_hour, credentials, postal_code, address_street, address_number,
                      address_complement, address_neighborhood, address_city, address_state, created_at
               FROM users WHERE id = ?''',
            (current_user_id,)
        )
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        profile = dict(user)
        
        # Se for professor, buscar habilidades
        if profile['user_type'] == 'teacher':
            cursor.execute(
                'SELECT skill_name, skill_description, skill_level, requires_evaluation FROM teacher_skills WHERE user_id = ?',
                (current_user_id,)
            )
            profile['skills'] = [dict(s) for s in cursor.fetchall()]
        
        # Se for aluno, buscar interesses
        elif profile['user_type'] == 'student':
            cursor.execute(
                'SELECT interest_name, difficulty_level, description, desired_level, requires_evaluation FROM student_interests WHERE user_id = ?',
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
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Buscar tipo do usuário
        cursor.execute('SELECT user_type FROM users WHERE id = ?', (current_user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        user_type = user['user_type']
        
        # Atualizar campos básicos do usuário
        update_fields = []
        update_values = []
        
        basic_fields = [
            'name',
            'bio',
            'photo_url',
            'location',
            'languages',
            'availability',
            'price_per_hour',
            'credentials',
            'postal_code',
            'address_street',
            'address_number',
            'address_complement',
            'address_neighborhood',
            'address_city',
            'address_state'
        ]
        for field in basic_fields:
            if field in data:
                normalized_value = normalize_user_field(field, data.get(field))
                if field == 'postal_code' and normalized_value and len(normalized_value) != 8:
                    return jsonify({'error': 'Informe um CEP válido com 8 dígitos.'}), 400
                update_fields.append(field)
                update_values.append(normalized_value)
        
        if update_fields:
            set_clause = ', '.join([f'{field} = ?' for field in update_fields]) + ', updated_at = CURRENT_TIMESTAMP'
            cursor.execute(
                f'UPDATE users SET {set_clause} WHERE id = ?',
                tuple(update_values) + (current_user_id,)
            )
            print(f"✅ Campos atualizados: {', '.join(update_fields)}")
        
        # Atualizar skills (se for professor e enviou skills)
        if user_type == 'teacher' and 'skills' in data:
            # Remover skills antigas
            cursor.execute('DELETE FROM teacher_skills WHERE user_id = ?', (current_user_id,))
            print("🗑️  Skills antigas removidas")
            
            # Adicionar novas skills
            for skill in data['skills']:
                if not skill.get('name'):
                    continue
                cursor.execute(
                    '''INSERT INTO teacher_skills (user_id, skill_name, skill_description, skill_level, requires_evaluation)
                       VALUES (?, ?, ?, ?, ?)''',
                    (
                        current_user_id,
                        skill['name'],
                        skill.get('description', ''),
                        skill.get('level'),
                        1 if skill.get('requires_evaluation') else 0
                    )
                )
                print(f"  ✅ Skill adicionada: {skill['name']}")
        
        # Atualizar interests (se for aluno e enviou interests)
        if user_type == 'student' and 'interests' in data:
            # Remover interests antigos
            cursor.execute('DELETE FROM student_interests WHERE user_id = ?', (current_user_id,))
            print("🗑️  Interests antigos removidos")
            
            # Adicionar novos interests
            for interest in data['interests']:
                if not interest.get('name'):
                    continue
                cursor.execute(
                    '''INSERT INTO student_interests (user_id, interest_name, difficulty_level, description, desired_level, requires_evaluation)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (
                        current_user_id,
                        interest['name'],
                        interest.get('difficulty', 'beginner'),
                        interest.get('description', ''),
                        interest.get('desired_level'),
                        1 if interest.get('requires_evaluation') else 0
                    )
                )
                print(f"  ✅ Interest adicionado: {interest['name']}")
        
        conn.commit()
        
        return jsonify({'message': 'Perfil atualizado com sucesso'}), 200
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao atualizar perfil: {e}")
        import traceback
        traceback.print_exc()
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
            '''SELECT id, name, bio, user_type, photo_url, location, languages,
                      availability, price_per_hour, credentials, postal_code, address_street,
                      address_number, address_complement, address_neighborhood, address_city,
                      address_state
               FROM users WHERE id = ?''',
            (user_id,)
        )
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        profile = dict(user)
        
        # Buscar habilidades/interesses conforme tipo
        if profile['user_type'] == 'teacher':
            cursor.execute(
                'SELECT skill_name, skill_description, skill_level, requires_evaluation FROM teacher_skills WHERE user_id = ?',
                (user_id,)
            )
            profile['skills'] = [dict(s) for s in cursor.fetchall()]
        elif profile['user_type'] == 'student':
            cursor.execute(
                'SELECT interest_name, difficulty_level, description, desired_level, requires_evaluation FROM student_interests WHERE user_id = ?',
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