"""
Rotas de Descoberta - Swipe e Match
Salvar como: backend/routes/discover_routes.py
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import sys
import os

# Adicionar o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection

discover_bp = Blueprint('discover', __name__)


@discover_bp.route('/profiles', methods=['GET'])
@jwt_required()
def get_profiles():
    """
    Retorna perfis disponíveis para swipe
    
    Retorna usuários que:
    - Não são o próprio usuário
    - Ainda não receberam swipe do usuário atual
    - São do tipo oposto (teacher <-> student)
    """
    current_user_id = int(get_jwt_identity())
    conn = get_db_connection()
    cursor = conn.cursor()
    print(f'corrent_user_id {current_user_id}')
    try:
        # Buscar tipo do usuário atual
        cursor.execute('SELECT user_type FROM users WHERE id = ?', (current_user_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        current_user_type = user_data['user_type']
        
        # Tipo oposto para matching
        opposite_type = 'teacher' if current_user_type == 'student' else 'student'
        
        # Buscar perfis disponíveis (limite maior para podermos ordenar por relevância)
        query = '''
            SELECT u.id, u.name, u.bio, u.user_type, u.photo_url
            FROM users u
            WHERE u.id != ?
            AND u.user_type = ?
            AND u.id NOT IN (
                SELECT to_user_id FROM swipes WHERE from_user_id = ?
            )
            ORDER BY RANDOM()
            LIMIT 50
        '''

        cursor.execute(query, (current_user_id, opposite_type, current_user_id))
        profiles = [dict(row) for row in cursor.fetchall()]

        # Se o usuário atual for student, carregar seus interesses para usar como parâmetro de match
        current_user_interests = []
        if current_user_type == 'student':
            cursor.execute('SELECT interest_name FROM student_interests WHERE user_id = ?', (current_user_id,))
            current_user_interests = [r['interest_name'].lower() for r in cursor.fetchall()]

        # Adicionar habilidades/interesses de cada perfil e calcular score simples por interseção de tags
        for profile in profiles:
            profile['match_score'] = 0
            if profile['user_type'] == 'teacher':
                cursor.execute(
                    'SELECT skill_name, skill_description, skill_level, requires_evaluation FROM teacher_skills WHERE user_id = ?',
                    (profile['id'],)
                )
                skills = [dict(s) for s in cursor.fetchall()]
                profile['skills'] = skills

                # calcular score simples quando o student tem interesse coincidente com skill_name
                if current_user_interests:
                    for s in skills:
                        if s.get('skill_name') and s['skill_name'].lower() in current_user_interests:
                            profile['match_score'] += 1
            else:
                cursor.execute(
                    'SELECT interest_name, difficulty_level, description, desired_level, requires_evaluation FROM student_interests WHERE user_id = ?',
                    (profile['id'],)
                )
                profile['interests'] = [dict(i) for i in cursor.fetchall()]

                # se current user for teacher, podemos também providenciar score baseando-se em interesses do aluno
                if current_user_type == 'teacher' and current_user_interests:
                    # para caso inverso (teacher procurando student), checar alinhamento
                    for i in profile['interests']:
                        if i.get('interest_name') and i['interest_name'].lower() in current_user_interests:
                            profile['match_score'] += 1

            # carregar média de avaliações do usuário
            cursor.execute(
                '''
                SELECT AVG(rating) AS avg_rating, COUNT(*) AS total_ratings
                FROM ratings
                WHERE rated_id = ?
                ''',
                (profile['id'],)
            )
            rating_row = cursor.fetchone()

            average = None
            count = 0
            if rating_row:
                count = rating_row['total_ratings'] or 0
                if rating_row['avg_rating'] is not None:
                    average = round(float(rating_row['avg_rating']), 2)

            profile['rating_summary'] = {
                'average': average,
                'count': count
            }

        # Ordenar por match_score decrescente para apresentar candidatos mais relevantes primeiro
        profiles.sort(key=lambda p: p.get('match_score', 0), reverse=True)

        return jsonify({'profiles': profiles}), 200
        
    except Exception as e:
        print(f"Erro ao buscar perfis: {e}")
        return jsonify({'error': 'Erro ao buscar perfis'}), 500
        
    finally:
        conn.close()


@discover_bp.route('/swipe', methods=['POST'])
@jwt_required()
def swipe():
    """
    Registra um swipe (like ou skip)
    
    Body esperado:
    {
        "to_user_id": 123,
        "swipe_type": "like" ou "skip"
    }
    
    Retorna:
    {
        "message": "Swipe registrado",
        "match": true/false
    }
    """
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not all(k in data for k in ['to_user_id', 'swipe_type']):
        return jsonify({'error': 'to_user_id e swipe_type são obrigatórios'}), 400
    
    if data['swipe_type'] not in ['like', 'skip']:
        return jsonify({'error': 'swipe_type deve ser "like" ou "skip"'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Registrar swipe
        cursor.execute(
            '''
            INSERT INTO swipes (from_user_id, to_user_id, swipe_type)
            VALUES (?, ?, ?)
            ''',
            (current_user_id, data['to_user_id'], data['swipe_type'])
        )
        
        is_match = False
        
        # Se foi "like", verificar se há match
        if data['swipe_type'] == 'like':
            cursor.execute(
                '''
                SELECT id FROM swipes
                WHERE from_user_id = ? AND to_user_id = ? AND swipe_type = 'like'
                ''',
                (data['to_user_id'], current_user_id)
            )
            
            mutual_like = cursor.fetchone()
            
            if mutual_like:
                # Criar match (garantir ordem consistente dos IDs)
                user1_id = min(current_user_id, data['to_user_id'])
                user2_id = max(current_user_id, data['to_user_id'])
                
                cursor.execute(
                    '''
                    INSERT OR IGNORE INTO matches (user1_id, user2_id)
                    VALUES (?, ?)
                    ''',
                    (user1_id, user2_id)
                )
                
                is_match = True
        
        conn.commit()
        
        return jsonify({
            'message': 'Swipe registrado com sucesso',
            'match': is_match
        }), 200
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao registrar swipe: {e}")
        return jsonify({'error': 'Erro ao registrar swipe'}), 500
        
    finally:
        conn.close()


@discover_bp.route('/matches', methods=['GET'])
@jwt_required()
def get_matches():
    """
    Retorna lista de matches do usuário com informações detalhadas
    """
    current_user_id = int(get_jwt_identity())
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Buscar informações básicas dos matches
        query = '''
            SELECT 
                m.id as match_id,
                m.matched_at,
                CASE 
                    WHEN m.user1_id = ? THEN u2.id
                    ELSE u1.id
                END as other_user_id,
                CASE 
                    WHEN m.user1_id = ? THEN u2.name
                    ELSE u1.name
                END as other_user_name,
                CASE 
                    WHEN m.user1_id = ? THEN u2.photo_url
                    ELSE u1.photo_url
                END as other_user_photo,
                CASE 
                    WHEN m.user1_id = ? THEN u2.user_type
                    ELSE u1.user_type
                END as other_user_type,
                CASE 
                    WHEN m.user1_id = ? THEN u2.bio
                    ELSE u1.bio
                END as other_user_bio,
                CASE 
                    WHEN m.user1_id = ? THEN u2.location
                    ELSE u1.location
                END as other_user_location
            FROM matches m
            JOIN users u1 ON m.user1_id = u1.id
            JOIN users u2 ON m.user2_id = u2.id
            WHERE m.is_active = 1 
            AND (m.user1_id = ? OR m.user2_id = ?)
            ORDER BY m.matched_at DESC
        '''
        
        cursor.execute(query, (
            current_user_id, current_user_id, current_user_id,
            current_user_id, current_user_id, current_user_id,
            current_user_id, current_user_id
        ))
        
        matches = [dict(row) for row in cursor.fetchall()]
        
        # Para cada match, buscar tags/habilidades e mensagens não lidas
        for match in matches:
            other_user_id = match['other_user_id']
            other_user_type = match['other_user_type']
            
            # Buscar tags do outro usuário
            if other_user_type == 'teacher':
                cursor.execute('''
                    SELECT skill_name, skill_level
                    FROM teacher_skills
                    WHERE user_id = ?
                    LIMIT 5
                ''', (other_user_id,))
                match['tags'] = [{'name': row['skill_name'], 'level': row['skill_level']} 
                               for row in cursor.fetchall()]
            else:
                cursor.execute('''
                    SELECT interest_name, desired_level
                    FROM student_interests
                    WHERE user_id = ?
                    LIMIT 5
                ''', (other_user_id,))
                match['tags'] = [{'name': row['interest_name'], 'level': row['desired_level']} 
                               for row in cursor.fetchall()]
            
            # Contar mensagens não lidas
            # O receiver é o usuário atual, então filtramos por mensagens onde ele NÃO é o sender
            cursor.execute('''
                SELECT COUNT(*) as unread_count
                FROM messages
                WHERE match_id = ? AND sender_id != ? AND is_read = 0
            ''', (match['match_id'], current_user_id))
            
            unread_row = cursor.fetchone()
            match['unread_count'] = unread_row['unread_count'] if unread_row else 0
            
            # Buscar última mensagem
            cursor.execute('''
                SELECT message_text, sent_at, sender_id
                FROM messages
                WHERE match_id = ?
                ORDER BY sent_at DESC
                LIMIT 1
            ''', (match['match_id'],))
            
            last_msg = cursor.fetchone()
            if last_msg:
                match['last_message'] = {
                    'content': last_msg['message_text'],
                    'sent_at': last_msg['sent_at'],
                    'is_mine': last_msg['sender_id'] == current_user_id
                }
            else:
                match['last_message'] = None

            # Avaliações relacionadas ao match
            cursor.execute(
                'SELECT rating FROM ratings WHERE match_id = ? AND rater_id = ?',
                (match['match_id'], current_user_id)
            )
            my_rating_row = cursor.fetchone()
            match['my_rating'] = my_rating_row['rating'] if my_rating_row else None

            cursor.execute(
                'SELECT rating FROM ratings WHERE match_id = ? AND rated_id = ? AND rater_id = ?',
                (match['match_id'], current_user_id, other_user_id)
            )
            received_row = cursor.fetchone()
            match['received_rating'] = received_row['rating'] if received_row else None
        
        return jsonify({'matches': matches}), 200
        
    except Exception as e:
        import traceback
        print(f"Erro ao buscar matches: {e}")
        print(traceback.format_exc())
        return jsonify({'error': 'Erro ao buscar matches'}), 500
        
    finally:
        conn.close()


@discover_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """
    Retorna estatísticas do usuário
    """
    current_user_id = int(get_jwt_identity())
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Total de swipes dados
        cursor.execute(
            'SELECT COUNT(*) as total FROM swipes WHERE from_user_id = ?',
            (current_user_id,)
        )
        total_swipes = cursor.fetchone()['total']
        
        # Total de matches
        cursor.execute(
            '''
            SELECT COUNT(*) as total FROM matches 
            WHERE (user1_id = ? OR user2_id = ?) AND is_active = 1
            ''',
            (current_user_id, current_user_id)
        )
        total_matches = cursor.fetchone()['total']
        
        # Likes recebidos
        cursor.execute(
            '''
            SELECT COUNT(*) as total FROM swipes 
            WHERE to_user_id = ? AND swipe_type = 'like'
            ''',
            (current_user_id,)
        )
        likes_received = cursor.fetchone()['total']
        
        return jsonify({
            'total_swipes': total_swipes,
            'total_matches': total_matches,
            'likes_received': likes_received
        }), 200
        
    except Exception as e:
        print(f"Erro ao buscar estatísticas: {e}")
        return jsonify({'error': 'Erro ao buscar estatísticas'}), 500
        
    finally:
        conn.close()