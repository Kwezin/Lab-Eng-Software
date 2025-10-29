"""
Configuração do Banco de Dados SQLite
Salvar como: backend/database.py
"""

import sqlite3
from datetime import datetime

DATABASE_PATH = 'tintin.db'

def get_db_connection():
    """Retorna uma conexão com o banco de dados SQLite"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    return conn


def init_database():
    """Inicializa o banco de dados com todas as tabelas necessárias"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabela de Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            photo_url TEXT,
            bio TEXT,
            user_type TEXT NOT NULL CHECK(user_type IN ('student', 'teacher')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de Habilidades/Tags para Professores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teacher_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            skill_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Tabela de Interesses/Dificuldades para Alunos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_interests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            interest_name TEXT NOT NULL,
            difficulty_level TEXT CHECK(difficulty_level IN ('beginner', 'intermediate', 'advanced')),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Tabela de Swipes (deslizes)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS swipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user_id INTEGER NOT NULL,
            to_user_id INTEGER NOT NULL,
            swipe_type TEXT NOT NULL CHECK(swipe_type IN ('like', 'skip')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (from_user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (to_user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(from_user_id, to_user_id)
        )
    ''')
    
    # Tabela de Matches
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER NOT NULL,
            user2_id INTEGER NOT NULL,
            matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user1_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (user2_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user1_id, user2_id)
        )
    ''')
    
    # Tabela de Mensagens
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            message_text TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT 0,
            FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
            FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Tabela de Avaliações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            rater_id INTEGER NOT NULL,
            rated_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
            FOREIGN KEY (rater_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (rated_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(match_id, rater_id)
        )
    ''')
    
    # Criar índices para melhor performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_swipes_users ON swipes(from_user_id, to_user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_matches_users ON matches(user1_id, user2_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_match ON messages(match_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_teacher_skills_user ON teacher_skills(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_student_interests_user ON student_interests(user_id)')
    
    conn.commit()
    conn.close()
    
    print("✅ Banco de dados inicializado com sucesso!")


def reset_database():
    """Remove todas as tabelas e recria o banco (USE COM CUIDADO!)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Deletar todas as tabelas
    cursor.execute('DROP TABLE IF EXISTS ratings')
    cursor.execute('DROP TABLE IF EXISTS messages')
    cursor.execute('DROP TABLE IF EXISTS matches')
    cursor.execute('DROP TABLE IF EXISTS swipes')
    cursor.execute('DROP TABLE IF EXISTS student_interests')
    cursor.execute('DROP TABLE IF EXISTS teacher_skills')
    cursor.execute('DROP TABLE IF EXISTS users')
    
    conn.commit()
    conn.close()
    
    print("⚠️  Banco de dados resetado!")
    
    # Recriar as tabelas
    init_database()


if __name__ == '__main__':
    # Inicializar o banco de dados
    init_database()