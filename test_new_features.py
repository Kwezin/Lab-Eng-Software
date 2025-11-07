"""
Script para testar as novas funcionalidades do banco de dados
"""
import requests
import json

API_BASE = "http://localhost:5000/api"

def test_register_teacher():
    """Testa registro de professor com novos campos"""
    print("\n" + "="*60)
    print("🧪 Testando registro de PROFESSOR com novos campos")
    print("="*60)
    
    data = {
        "name": "Teste Professor",
        "email": "teste.prof@example.com",
        "password": "senha123",
        "user_type": "teacher",
        "bio": "Professor de programação com experiência",
        "location": "São Paulo, SP",
        "languages": "Português, Inglês",
        "availability": "Noites e fins de semana",
        "price_per_hour": 80.00,
        "credentials": "Bacharelado em Ciência da Computação",
        "skills": [
            {
                "name": "Python",
                "description": "10 anos de experiência",
                "level": "expert",
                "requires_evaluation": True
            },
            {
                "name": "JavaScript",
                "description": "Desenvolvimento web fullstack",
                "level": "advanced",
                "requires_evaluation": False
            }
        ]
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/register", json=data)
        print(f"\n📤 Status: {response.status_code}")
        print(f"📥 Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.json().get('token'), response.json().get('user_id')
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None, None

def test_register_student():
    """Testa registro de estudante com novos campos"""
    print("\n" + "="*60)
    print("🧪 Testando registro de ESTUDANTE com novos campos")
    print("="*60)
    
    data = {
        "name": "Teste Estudante",
        "email": "teste.estudante@example.com",
        "password": "senha123",
        "user_type": "student",
        "bio": "Quero aprender programação",
        "location": "Rio de Janeiro, RJ",
        "languages": "Português",
        "interests": [
            {
                "name": "Python",
                "difficulty": "beginner",
                "description": "Quero aprender do zero",
                "desired_level": "intermediate",
                "requires_evaluation": False
            },
            {
                "name": "JavaScript",
                "difficulty": "beginner",
                "description": "Desenvolvimento web",
                "desired_level": "beginner",
                "requires_evaluation": True
            }
        ]
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/register", json=data)
        print(f"\n📤 Status: {response.status_code}")
        print(f"📥 Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.json().get('token'), response.json().get('user_id')
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None, None

def test_get_profile(token):
    """Testa busca de perfil próprio"""
    print("\n" + "="*60)
    print("🧪 Testando GET /api/profile/me")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/profile/me", headers=headers)
        print(f"\n📤 Status: {response.status_code}")
        print(f"📥 Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def test_discover_profiles(token):
    """Testa descoberta de perfis"""
    print("\n" + "="*60)
    print("🧪 Testando GET /api/discover/profiles")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/discover/profiles", headers=headers)
        print(f"\n📤 Status: {response.status_code}")
        profiles = response.json().get('profiles', [])
        print(f"📥 Encontrados {len(profiles)} perfis")
        
        for profile in profiles[:2]:  # Mostrar apenas os 2 primeiros
            print(f"\n  👤 {profile.get('name')} ({profile.get('user_type')})")
            print(f"     Match Score: {profile.get('match_score', 0)}")
            if profile.get('skills'):
                print(f"     Skills: {[s['skill_name'] for s in profile['skills']]}")
            if profile.get('interests'):
                print(f"     Interests: {[i['interest_name'] for i in profile['interests']]}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def test_update_profile(token):
    """Testa atualização de perfil"""
    print("\n" + "="*60)
    print("🧪 Testando PUT /api/profile/update")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "bio": "Bio atualizada com sucesso!",
        "location": "Brasília, DF",
        "availability": "Tardes e noites"
    }
    
    try:
        response = requests.put(f"{API_BASE}/profile/update", json=data, headers=headers)
        print(f"\n📤 Status: {response.status_code}")
        print(f"📥 Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("\n" + "🎓 TINTIN - Teste de Novas Funcionalidades ".center(60, "="))
    
    # Testar registro de professor
    teacher_token, teacher_id = test_register_teacher()
    
    if teacher_token:
        # Testar busca do próprio perfil
        test_get_profile(teacher_token)
        
        # Testar atualização de perfil
        test_update_profile(teacher_token)
    
    # Testar registro de estudante
    student_token, student_id = test_register_student()
    
    if student_token:
        # Testar busca do próprio perfil
        test_get_profile(student_token)
        
        # Testar descoberta de perfis (deve mostrar o professor registrado)
        test_discover_profiles(student_token)
    
    print("\n" + "="*60)
    print("✅ Testes concluídos!")
    print("="*60)
