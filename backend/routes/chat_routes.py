"""
Rotas de Chat - Mensagens entre matches (MELHORADO)
Salvar como: backend/routes/chat_routes.py
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import sys
import os

# Adicionar o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    """
    Envia uma mensagem em um chat
    
    Body esperado:
    {
        "match_id": 1,
        "message_text": "Olá! Como vai?"
    }
    """
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not all(k in data for k in ['match_id', 'message_text']):
        return jsonify({'error': 'match_id e message_text são obrigatórios'}), 400
    
    message_text = data['message_text'].strip()
    if not message_text:
        return jsonify({'error': 'Mensagem não pode estar vazia'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se o match existe e o usuário faz parte dele
        cursor.execute(
            '''
            SELECT id FROM matches 
            WHERE id = ? AND (user1_id = ? OR user2_id = ?) AND is_active = 1
            ''',
            (data['match_id'], current_user_id, current_user_id)
        )
        
        match = cursor.fetchone()
        if not match:
            return jsonify({'error': 'Match não encontrado ou inválido'}), 404
        
        # Inserir mensagem
        cursor.execute(
            '''
            INSERT INTO messages (match_id, sender_id, message_text)
            VALUES (?, ?, ?)
            ''',
            (data['match_id'], current_user_id, message_text)
        )
        
        message_id = cursor.lastrowid
        conn.commit()
        
        return jsonify({
            'message': 'Mensagem enviada com sucesso',
            'message_id': message_id
        }), 201
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao enviar mensagem: {e}")
        return jsonify({'error': 'Erro ao enviar mensagem'}), 500
        
    finally:
        conn.close()


@chat_bp.route('/messages/<int:match_id>', methods=['GET'])
@jwt_required()
def get_messages(match_id):
    """
    Retorna todas as mensagens de um chat
    """
    current_user_id = int(get_jwt_identity())
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se o usuário faz parte do match
        cursor.execute(
            '''
            SELECT id FROM matches 
            WHERE id = ? AND (user1_id = ? OR user2_id = ?)
            ''',
            (match_id, current_user_id, current_user_id)
        )
        
        match = cursor.fetchone()
        if not match:
            return jsonify({'error': 'Match não encontrado'}), 404
        
        # Buscar mensagens
        cursor.execute(
            '''
            SELECT 
                m.id,
                m.sender_id,
                m.message_text,
                m.sent_at,
                m.is_read,
                u.name as sender_name
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.match_id = ?
            ORDER BY m.sent_at ASC
            ''',
            (match_id,)
        )
        
        messages = [dict(row) for row in cursor.fetchall()]
        
        # Marcar mensagens como lidas
        cursor.execute(
            '''
            UPDATE messages 
            SET is_read = 1 
            WHERE match_id = ? AND sender_id != ? AND is_read = 0
            ''',
            (match_id, current_user_id)
        )
        conn.commit()
        
        return jsonify({'messages': messages}), 200
        
    except Exception as e:
        print(f"Erro ao buscar mensagens: {e}")
        return jsonify({'error': 'Erro ao buscar mensagens'}), 500
        
    finally:
        conn.close()


@chat_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """
    Retorna lista de conversas com a última mensagem de cada
    """
    current_user_id = int(get_jwt_identity())
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = '''
            SELECT 
                m.id as match_id,
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
                (
                    SELECT message_text 
                    FROM messages 
                    WHERE match_id = m.id 
                    ORDER BY sent_at DESC 
                    LIMIT 1
                ) as last_message,
                (
                    SELECT sent_at 
                    FROM messages 
                    WHERE match_id = m.id 
                    ORDER BY sent_at DESC 
                    LIMIT 1
                ) as last_message_time,
                (
                    SELECT COUNT(*) 
                    FROM messages 
                    WHERE match_id = m.id 
                    AND sender_id != ? 
                    AND is_read = 0
                ) as unread_count
            FROM matches m
            JOIN users u1 ON m.user1_id = u1.id
            JOIN users u2 ON m.user2_id = u2.id
            WHERE m.is_active = 1 
            AND (m.user1_id = ? OR m.user2_id = ?)
            ORDER BY COALESCE(
                (
                    SELECT sent_at 
                    FROM messages 
                    WHERE match_id = m.id 
                    ORDER BY sent_at DESC 
                    LIMIT 1
                ),
                m.matched_at
            ) DESC
        '''
        
        cursor.execute(query, (
            current_user_id, current_user_id, current_user_id,
            current_user_id, current_user_id, current_user_id, current_user_id
        ))
        
        conversations = [dict(row) for row in cursor.fetchall()]
        
        return jsonify({'conversations': conversations}), 200
        
    except Exception as e:
        print(f"Erro ao buscar conversas: {e}")
        return jsonify({'error': 'Erro ao buscar conversas'}), 500
        
    finally:
        conn.close()


@chat_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """
    Retorna o total de mensagens não lidas
    """
    current_user_id = int(get_jwt_identity())
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            '''
            SELECT COUNT(*) as unread_count
            FROM messages msg
            JOIN matches m ON msg.match_id = m.id
            WHERE (m.user1_id = ? OR m.user2_id = ?)
            AND msg.sender_id != ?
            AND msg.is_read = 0
            ''',
            (current_user_id, current_user_id, current_user_id)
        )
        
        result = cursor.fetchone()
        unread_count = result['unread_count'] if result else 0
        
        return jsonify({'unread_count': unread_count}), 200
        
    except Exception as e:
        print(f"Erro ao buscar contagem de não lidas: {e}")
        return jsonify({'error': 'Erro ao buscar mensagens não lidas'}), 500
        
    finally:
        conn.close()


@chat_bp.route('/mark-read/<int:match_id>', methods=['POST'])
@jwt_required()
def mark_messages_read(match_id):
    """
    Marca todas as mensagens de um match como lidas
    """
    current_user_id = int(get_jwt_identity())
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            '''
            UPDATE messages 
            SET is_read = 1 
            WHERE match_id = ? AND sender_id != ? AND is_read = 0
            ''',
            (match_id, current_user_id)
        )
        conn.commit()
        
        return jsonify({'message': 'Mensagens marcadas como lidas'}), 200
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao marcar mensagens: {e}")
        return jsonify({'error': 'Erro ao marcar mensagens'}), 500
        
    finally:
        conn.close()