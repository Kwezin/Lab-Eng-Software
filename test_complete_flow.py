"""
Teste completo do fluxo: Login -> Descobrir perfis -> Swipe -> Match
"""
import requests
import json

API_BASE = "http://localhost:5000/api"

def test_login(email, password):
    """Testa login"""
    print(f"\n🔐 Login: {email}")
    response = requests.post(f"{API_BASE}/auth/login", json={
        "email": email,
        "password": password
    })
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login bem-sucedido! User: {data['name']} ({data['user_type']})")
        return data['token'], data['user_id'], data['user_type']
    else:
        print(f"❌ Erro: {response.json()}")
        return None, None, None

def test_discover(token):
    """Testa descoberta de perfis"""
    print("\n🔍 Descobrindo perfis...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/discover/profiles", headers=headers)
    
    if response.status_code == 200:
        profiles = response.json().get('profiles', [])
        print(f"✅ Encontrados {len(profiles)} perfis")
        
        for i, profile in enumerate(profiles[:3], 1):
            print(f"\n  {i}. 👤 {profile['name']} ({profile['user_type']})")
            print(f"     📍 {profile.get('location', 'N/A')}")
            print(f"     💬 {profile.get('bio', 'Sem bio')}")
            print(f"     🎯 Match Score: {profile.get('match_score', 0)}")
            
            if profile.get('skills'):
                print(f"     📚 Skills:")
                for skill in profile['skills'][:3]:
                    eval_badge = " 🔍" if skill.get('requires_evaluation') else ""
                    level = skill.get('skill_level', 'N/A')
                    print(f"        • {skill['skill_name']} ({level}){eval_badge}")
            
            if profile.get('interests'):
                print(f"     💡 Interesses:")
                for interest in profile['interests'][:3]:
                    eval_badge = " 🔍" if interest.get('requires_evaluation') else ""
                    level = interest.get('difficulty_level', 'N/A')
                    print(f"        • {interest['interest_name']} ({level}){eval_badge}")
        
        return profiles
    else:
        print(f"❌ Erro: {response.json()}")
        return []

def test_swipe(token, to_user_id, swipe_type):
    """Testa swipe"""
    print(f"\n👉 Dando {swipe_type} no usuário {to_user_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_BASE}/discover/swipe", 
                            json={"to_user_id": to_user_id, "swipe_type": swipe_type},
                            headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('match'):
            print(f"🎉 É UM MATCH!")
        else:
            print(f"✅ Swipe registrado")
        return data.get('match', False)
    else:
        print(f"❌ Erro: {response.json()}")
        return False

def test_get_profile(token, user_id):
    """Testa busca de perfil específico"""
    print(f"\n👤 Buscando perfil do usuário {user_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/profile/{user_id}", headers=headers)
    
    if response.status_code == 200:
        profile = response.json()
        print(f"✅ Perfil encontrado:")
        print(f"   Nome: {profile['name']}")
        print(f"   Tipo: {profile['user_type']}")
        print(f"   Localização: {profile.get('location', 'N/A')}")
        print(f"   Idiomas: {profile.get('languages', 'N/A')}")
        print(f"   Disponibilidade: {profile.get('availability', 'N/A')}")
        if profile.get('price_per_hour'):
            print(f"   Preço/hora: R$ {profile['price_per_hour']:.2f}")
        if profile.get('avg_rating'):
            print(f"   Avaliação: {profile['avg_rating']}⭐ ({profile['total_ratings']} avaliações)")
    else:
        print(f"❌ Erro: {response.json()}")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🎓 TINTIN - Teste de Fluxo Completo")
    print("="*70)
    
    # Login como estudante
    student_token, student_id, student_type = test_login("lucas@example.com", "senha123")
    
    if student_token:
        # Descobrir perfis
        profiles = test_discover(student_token)
        
        if profiles:
            # Dar swipe no primeiro perfil
            first_profile = profiles[0]
            test_get_profile(student_token, first_profile['id'])
            test_swipe(student_token, first_profile['id'], "like")
    
    print("\n" + "-"*70)
    
    # Login como professor
    teacher_token, teacher_id, teacher_type = test_login("carlos@example.com", "senha123")
    
    if teacher_token:
        # Descobrir perfis
        profiles = test_discover(teacher_token)
        
        if profiles:
            # Dar like no Lucas (student_id = 8) para criar um match
            test_swipe(teacher_token, 8, "like")
    
    print("\n" + "="*70)
    print("✅ Testes concluídos!")
    print("="*70)
