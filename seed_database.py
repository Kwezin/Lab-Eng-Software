"""
Script para popular o banco de dados com dados de teste
Executar: python seed_database.py
"""

import sys
import os
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.database import get_db_connection

def seed_database():
    """Popula o banco com dados de teste"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("🌱 Seedando banco de dados com dados de teste...")
    
    try:
        # Professores
        professors = [
            {
                'name': 'Carlos Silva',
                'email': 'carlos@example.com',
                'password': 'senha123',
                'bio': 'Professor de Python com 5 anos de experiência',
                'skills': [
                    {'name': 'Python', 'description': '5 anos ensinando'},
                    {'name': 'JavaScript', 'description': 'Desenvolvimento web'}
                ]
            },
            {
                'name': 'Maria Santos',
                'email': 'maria@example.com',
                'password': 'senha123',
                'bio': 'Engenheira de Software apaixonada por ensinar',
                'skills': [
                    {'name': 'React', 'description': 'Frontend moderno'},
                    {'name': 'SQL', 'description': 'Banco de dados'}
                ]
            },
            {
                'name': 'João Costa',
                'email': 'joao@example.com',
                'password': 'senha123',
                'bio': 'Designer gráfico e ilustrador',
                'skills': [
                    {'name': 'Figma', 'description': 'Design de UI/UX'},
                    {'name': 'Ilustração', 'description': 'Arte digital'}
                ]
            },
            {
                'name': 'Ana Paula',
                'email': 'ana@example.com',
                'password': 'senha123',
                'bio': 'Violonista profissional e professora de música',
                'skills': [
                    {'name': 'Violão', 'description': 'Clássico e popular'},
                    {'name': 'Musicalização', 'description': 'Para iniciantes'}
                ]
            },
            {
                'name': 'Pedro Oliveira',
                'email': 'pedro@example.com',
                'password': 'senha123',
                'bio': 'Eletricista experiente com 10 anos no mercado',
                'skills': [
                    {'name': 'Eletricidade Residencial', 'description': 'Instalações básicas'},
                    {'name': 'Manutenção Elétrica', 'description': 'Reparo de equipamentos'}
                ]
            }
        ]
        
        # Alunos
        students = [
            {
                'name': 'Lucas Ferreira',
                'email': 'lucas@example.com',
                'password': 'senha123',
                'bio': 'Iniciante querendo aprender programação',
                'interests': [
                    {'name': 'Python', 'difficulty': 'beginner', 'description': 'Primeiro linguagem de programação'},
                    {'name': 'JavaScript', 'difficulty': 'beginner', 'description': 'Web development'}
                ]
            },
            {
                'name': 'Julia Martins',
                'email': 'julia@example.com',
                'password': 'senha123',
                'bio': 'Gostaria de aprender a tocar violão',
                'interests': [
                    {'name': 'Violão', 'difficulty': 'beginner', 'description': 'Desde o início'},
                    {'name': 'Música', 'difficulty': 'beginner', 'description': 'Teoria musical'}
                ]
            },
            {
                'name': 'Ricardo Gomes',
                'email': 'ricardo@example.com',
                'password': 'senha123',
                'bio': 'Aprendendo design e UI/UX',
                'interests': [
                    {'name': 'Figma', 'difficulty': 'beginner', 'description': 'Design de interfaces'},
                    {'name': 'UX Research', 'difficulty': 'intermediate', 'description': 'Pesquisa de usuários'}
                ]
            },
            {
                'name': 'Fernanda Rocha',
                'email': 'fernanda@example.com',
                'password': 'senha123',
                'bio': 'Aprendendo a trocar tomadas e interruptores',
                'interests': [
                    {'name': 'Eletricidade Residencial', 'difficulty': 'beginner', 'description': 'Manutenção básica da casa'},
                    {'name': 'Eletricista', 'difficulty': 'beginner', 'description': 'Pequenos reparos'}
                ]
            },
            {
                'name': 'Gabriel Silva',
                'email': 'gabriel@example.com',
                'password': 'senha123',
                'bio': 'Desenvolvedor iniciante querendo melhorar em React',
                'interests': [
                    {'name': 'React', 'difficulty': 'intermediate', 'description': 'Componentes e hooks'},
                    {'name': 'SQL', 'difficulty': 'beginner', 'description': 'Banco de dados'}
                ]
            }
        ]
        
        # Inserir Professores
        print("\n👨‍🏫 Inserindo Professores...")
        for prof in professors:
            password_hash = generate_password_hash(prof['password'])
            cursor.execute(
                '''INSERT INTO users (name, email, password_hash, bio, user_type, location, languages, credentials) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (prof['name'], prof['email'], password_hash, prof['bio'], 'teacher', prof.get('location'), prof.get('languages'), prof.get('credentials'))
            )
            prof_id = cursor.lastrowid
            
            # Inserir skills
            for skill in prof['skills']:
                cursor.execute(
                    '''INSERT INTO teacher_skills (user_id, skill_name, skill_description, skill_level, requires_evaluation) 
                       VALUES (?, ?, ?, ?, ?)''',
                    (prof_id, skill['name'], skill['description'], skill.get('level'), 1 if skill.get('requires_evaluation') else 0)
                )
            
            print(f"  ✅ {prof['name']} (ID: {prof_id})")
        
        # Inserir Alunos
        print("\n📚 Inserindo Alunos...")
        for student in students:
            password_hash = generate_password_hash(student['password'])
            cursor.execute(
                '''INSERT INTO users (name, email, password_hash, bio, user_type, location, languages) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (student['name'], student['email'], password_hash, student['bio'], 'student', student.get('location'), student.get('languages'))
            )
            student_id = cursor.lastrowid
            
            # Inserir interests
            for interest in student['interests']:
                cursor.execute(
                    '''INSERT INTO student_interests (user_id, interest_name, difficulty_level, description, desired_level, requires_evaluation) 
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (student_id, interest['name'], interest['difficulty'], interest['description'], interest.get('desired_level'), 1 if interest.get('requires_evaluation') else 0)
                )
            
            print(f"  ✅ {student['name']} (ID: {student_id})")
        
        conn.commit()
        
        print("\n" + "="*60)
        print("✨ Banco de dados populado com sucesso!")
        print("="*60)
        print("\n📊 Dados inseridos:")
        print(f"  👨‍🏫 Professores: {len(professors)}")
        print(f"  📚 Alunos: {len(students)}")
        print("\n🔑 Credenciais de teste:")
        print("  Email: qualquer um dos acima")
        print("  Senha: senha123")
        print("\n💡 Agora você pode fazer login e ver os perfis no discover!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao popular banco: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == '__main__':
    seed_database()