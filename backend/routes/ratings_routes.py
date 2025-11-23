"""
Rotas de Avaliações de Matches
Salvar como: backend/routes/ratings_routes.py
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database import get_db_connection

ratings_bp = Blueprint('ratings', __name__)


def _fetch_match(cursor, match_id):
    cursor.execute(
        'SELECT id, user1_id, user2_id, is_active FROM matches WHERE id = ?',
        (match_id,)
    )
    return cursor.fetchone()


def _format_rating_row(row):
    if not row:
        return None
    return {
        'rating': row['rating'],
        'comment': row['comment'],
        'created_at': row['created_at']
    }


@ratings_bp.route('', methods=['POST'])
@jwt_required()
def submit_rating():
    """Cria ou atualiza uma avaliação para um match"""
    current_user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    match_id = data.get('match_id')
    rating = data.get('rating')
    comment = (data.get('comment') or '').strip()

    if match_id is None:
        return jsonify({'error': 'match_id é obrigatório'}), 400

    try:
        match_id = int(match_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'match_id inválido'}), 400

    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return jsonify({'error': 'rating deve ser um número inteiro entre 1 e 5'}), 400

    if rating < 1 or rating > 5:
        return jsonify({'error': 'rating deve estar entre 1 e 5'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        match = _fetch_match(cursor, match_id)
        if not match or match['is_active'] != 1:
            return jsonify({'error': 'Match não encontrado ou inativo'}), 404

        user1 = match['user1_id']
        user2 = match['user2_id']

        if current_user_id not in (user1, user2):
            return jsonify({'error': 'Você não tem permissão para avaliar este match'}), 403

        rated_id = user2 if current_user_id == user1 else user1

        cursor.execute(
            '''
            INSERT INTO ratings (match_id, rater_id, rated_id, rating, comment)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(match_id, rater_id) DO UPDATE SET
                rating = excluded.rating,
                comment = excluded.comment,
                created_at = CURRENT_TIMESTAMP
            ''',
            (match_id, current_user_id, rated_id, rating, comment)
        )

        conn.commit()

        return jsonify({
            'message': 'Avaliação registrada com sucesso',
            'match_id': match_id,
            'rating': rating,
            'comment': comment
        }), 200

    except sqlite3.Error as exc:
        conn.rollback()
        print(f"Erro ao salvar avaliação: {exc}")
        return jsonify({'error': 'Erro ao salvar avaliação'}), 500

    finally:
        conn.close()


@ratings_bp.route('/match/<int:match_id>', methods=['GET'])
@jwt_required()
def get_match_rating(match_id):
    """Retorna a avaliação feita e recebida pelo usuário em um match"""
    current_user_id = int(get_jwt_identity())

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        match = _fetch_match(cursor, match_id)
        if not match:
            return jsonify({'error': 'Match não encontrado'}), 404

        user1 = match['user1_id']
        user2 = match['user2_id']

        if current_user_id not in (user1, user2):
            return jsonify({'error': 'Você não tem acesso a este match'}), 403

        other_user_id = user2 if current_user_id == user1 else user1

        cursor.execute(
            'SELECT id, name FROM users WHERE id = ?',
            (other_user_id,)
        )
        other_user = cursor.fetchone()

        cursor.execute(
            '''
            SELECT rating, comment, created_at
            FROM ratings
            WHERE match_id = ? AND rater_id = ? AND rated_id = ?
            ''',
            (match_id, current_user_id, other_user_id)
        )
        your_rating = _format_rating_row(cursor.fetchone())

        cursor.execute(
            '''
            SELECT rating, comment, created_at
            FROM ratings
            WHERE match_id = ? AND rated_id = ? AND rater_id = ?
            ''',
            (match_id, current_user_id, other_user_id)
        )
        received_rating = _format_rating_row(cursor.fetchone())

        return jsonify({
            'match_id': match_id,
            'can_rate': match['is_active'] == 1,
            'your_rating': your_rating,
            'received_rating': received_rating,
            'other_user': {
                'id': other_user['id'] if other_user else other_user_id,
                'name': other_user['name'] if other_user else ''
            }
        }), 200

    except sqlite3.Error as exc:
        print(f"Erro ao buscar avaliações: {exc}")
        return jsonify({'error': 'Erro ao buscar avaliações'}), 500

    finally:
        conn.close()
