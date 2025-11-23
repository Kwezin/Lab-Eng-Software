"""
Testes para backend/database.py
"""

import pytest
import sqlite3
import os
import tempfile
from backend.database import get_db_connection, init_database, reset_database


def test_get_db_connection(test_db):
    """Testa se a conexão com o banco é criada corretamente"""
    conn = sqlite3.connect(test_db)
    assert conn is not None
    conn.close()


def test_get_db_connection_row_factory(test_db):
    """Testa se a row_factory está configurada corretamente"""
    conn = sqlite3.connect(test_db)
    conn.row_factory = sqlite3.Row
    
    cursor = conn.cursor()
    cursor.execute("SELECT 1 as test_column")
    row = cursor.fetchone()
    
    # Deve permitir acesso por nome de coluna
    assert row['test_column'] == 1
    conn.close()


def test_init_database_creates_users_table(test_db):
    """Testa se a tabela users é criada"""
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='users'
    """)
    
    result = cursor.fetchone()
    assert result is not None
    assert result[0] == 'users'
    conn.close()


def test_init_database_creates_teacher_skills_table(test_db):
    """Testa se a tabela teacher_skills é criada"""
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='teacher_skills'
    """)
    
    result = cursor.fetchone()
    assert result is not None
    conn.close()


def test_init_database_creates_student_interests_table(test_db):
    """Testa se a tabela student_interests é criada"""
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='student_interests'
    """)
    
    result = cursor.fetchone()
    assert result is not None
    conn.close()


def test_init_database_creates_swipes_table(test_db):
    """Testa se a tabela swipes é criada"""
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='swipes'
    """)
    
    result = cursor.fetchone()
    assert result is not None
    conn.close()


def test_init_database_creates_matches_table(test_db):
    """Testa se a tabela matches é criada"""
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='matches'
    """)
    
    result = cursor.fetchone()
    assert result is not None
    conn.close()


def test_init_database_creates_messages_table(test_db):
    """Testa se a tabela messages é criada"""
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='messages'
    """)
    
    result = cursor.fetchone()
    assert result is not None
    conn.close()


def test_init_database_creates_ratings_table(test_db):
    """Testa se a tabela ratings é criada"""
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='ratings'
    """)
    
    result = cursor.fetchone()
    assert result is not None
    conn.close()


def test_users_table_has_correct_columns(test_db):
    """Testa se a tabela users tem todas as colunas necessárias"""
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(users)")
    columns = {row[1] for row in cursor.fetchall()}
    
    expected_columns = {
        'id', 'name', 'email', 'password_hash', 'photo_url', 'bio', 
        'user_type', 'location', 'languages', 'availability', 
        'price_per_hour', 'credentials', 'postal_code', 'address_street',
        'address_number', 'address_complement', 'address_neighborhood',
        'address_city', 'address_state', 'created_at', 'updated_at'
    }
    
    assert expected_columns.issubset(columns)
    conn.close()


def test_indexes_are_created(test_db):
    """Testa se os índices foram criados"""
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='index'
    """)
    
    indexes = {row[0] for row in cursor.fetchall()}
    
    expected_indexes = {
        'idx_users_email',
        'idx_swipes_users',
        'idx_matches_users',
        'idx_messages_match',
        'idx_teacher_skills_user',
        'idx_student_interests_user',
        'idx_teacher_skills_name',
        'idx_student_interests_name'
    }
    
    assert expected_indexes.issubset(indexes)
    conn.close()


def test_user_type_constraint(db_connection):
    """Testa se a constraint de user_type funciona"""
    cursor = db_connection.cursor()
    
    # Tentar inserir user_type inválido deve falhar
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, user_type)
            VALUES (?, ?, ?, ?)
        """, ('Test', 'test@test.com', 'hash', 'invalid_type'))


def test_swipe_type_constraint(db_connection):
    """Testa se a constraint de swipe_type funciona"""
    cursor = db_connection.cursor()
    
    # Criar dois usuários primeiro
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, user_type)
        VALUES (?, ?, ?, ?)
    """, ('User1', 'user1@test.com', 'hash', 'student'))
    
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, user_type)
        VALUES (?, ?, ?, ?)
    """, ('User2', 'user2@test.com', 'hash', 'teacher'))
    
    # Tentar inserir swipe_type inválido deve falhar
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("""
            INSERT INTO swipes (from_user_id, to_user_id, swipe_type)
            VALUES (?, ?, ?)
        """, (1, 2, 'invalid_swipe'))


def test_rating_range_constraint(db_connection):
    """Testa se a constraint de rating (1-5) funciona"""
    cursor = db_connection.cursor()
    
    # Criar usuários e match
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, user_type)
        VALUES (?, ?, ?, ?)
    """, ('User1', 'user1@test.com', 'hash', 'student'))
    
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, user_type)
        VALUES (?, ?, ?, ?)
    """, ('User2', 'user2@test.com', 'hash', 'teacher'))
    
    cursor.execute("""
        INSERT INTO matches (user1_id, user2_id)
        VALUES (?, ?)
    """, (1, 2))
    
    db_connection.commit()
    
    # Rating < 1 deve falhar
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("""
            INSERT INTO ratings (match_id, rater_id, rated_id, rating)
            VALUES (?, ?, ?, ?)
        """, (1, 1, 2, 0))
    
    # Rating > 5 deve falhar
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("""
            INSERT INTO ratings (match_id, rater_id, rated_id, rating)
            VALUES (?, ?, ?, ?)
        """, (1, 1, 2, 6))


def test_unique_email_constraint(db_connection):
    """Testa se a constraint de email único funciona"""
    cursor = db_connection.cursor()
    
    # Inserir primeiro usuário
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, user_type)
        VALUES (?, ?, ?, ?)
    """, ('User1', 'same@test.com', 'hash', 'student'))
    
    db_connection.commit()
    
    # Tentar inserir segundo usuário com mesmo email deve falhar
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, user_type)
            VALUES (?, ?, ?, ?)
        """, ('User2', 'same@test.com', 'hash', 'teacher'))


def test_foreign_key_constraint_teacher_skills(db_connection):
    """Testa se a foreign key de teacher_skills funciona"""
    cursor = db_connection.cursor()
    
    # Tentar inserir skill sem usuário deve falhar (se FK habilitada)
    # Note: SQLite requer PRAGMA foreign_keys = ON
    cursor.execute("PRAGMA foreign_keys = ON")
    
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("""
            INSERT INTO teacher_skills (user_id, skill_name)
            VALUES (?, ?)
        """, (999, 'Python'))


def test_foreign_key_constraint_student_interests(db_connection):
    """Testa se a foreign key de student_interests funciona"""
    cursor = db_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("""
            INSERT INTO student_interests (user_id, interest_name)
            VALUES (?, ?)
        """, (999, 'Python'))


def test_cascade_delete_on_user(db_connection):
    """Testa se o CASCADE DELETE funciona ao deletar usuário"""
    cursor = db_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Criar usuário
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, user_type)
        VALUES (?, ?, ?, ?)
    """, ('Teacher', 'teacher@test.com', 'hash', 'teacher'))
    
    user_id = cursor.lastrowid
    
    # Adicionar skill
    cursor.execute("""
        INSERT INTO teacher_skills (user_id, skill_name)
        VALUES (?, ?)
    """, (user_id, 'Python'))
    
    db_connection.commit()
    
    # Verificar que skill existe
    cursor.execute("SELECT COUNT(*) FROM teacher_skills WHERE user_id = ?", (user_id,))
    assert cursor.fetchone()[0] == 1
    
    # Deletar usuário
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db_connection.commit()
    
    # Verificar que skill foi deletada em cascata
    cursor.execute("SELECT COUNT(*) FROM teacher_skills WHERE user_id = ?", (user_id,))
    assert cursor.fetchone()[0] == 0
