#!/usr/bin/env python3
"""
JWT Authentication Test Script (PostgreSQL Version)
Bu script JWT authentication sistemini PostgreSQL veritabanı ile test eder.
Kullanıcı kaydı, login, duplikasyon kontrolü ve korumalı endpoint'leri test eder.
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_registration():
    """Kullanıcı kayıt testi"""
    print("📝 Kullanıcı kayıt testi başlıyor...")
    
    # Yeni kullanıcı bilgileri
    register_data = {
        "username": "testuser2",
        "email": "testuser2@example.com",
        "full_name": "Test User 2",
        "password": "strongpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=register_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Kullanıcı kaydı başarılı!")
            print(f"ID: {result['id']}")
            print(f"Kullanıcı adı: {result['username']}")
            print(f"Email: {result['email']}")
            print(f"Tam ad: {result['full_name']}")
            print(f"Mesaj: {result['message']}")
            return True
        else:
            print(f"❌ Kullanıcı kaydı başarısız: {response.status_code}")
            print(f"Hata: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Kullanıcı kaydı hatası: {e}")
        return False

def test_duplicate_registration():
    """Duplikasyon testi"""
    print("\n🚫 Duplikasyon testi başlıyor...")
    
    # Aynı kullanıcı adı ile tekrar kayıt denemesi
    register_data = {
        "username": "testuser",  # Zaten var olan kullanıcı
        "email": "different@example.com",
        "full_name": "Different User",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=register_data)
        
        if response.status_code == 400:
            print("✅ Duplikasyon başarıyla engellendi!")
            error_detail = response.json().get('detail', 'Bilinmeyen hata')
            print(f"Hata mesajı: {error_detail}")
        else:
            print(f"❌ Duplikasyon engellenmedi: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Duplikasyon testi hatası: {e}")

def test_login():
    """Login testi"""
    print("\n🔐 Login testi başlıyor...")
    
    # Login bilgileri
    login_data = {
        "username": "testuser",
        "password": "secret"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/token", json=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login başarılı!")
            print(f"Token: {token_data['access_token'][:50]}...")
            return token_data['access_token']
        else:
            print(f"❌ Login başarısız: {response.status_code}")
            print(f"Hata: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login hatası: {e}")
        return None

def test_protected_endpoint(token):
    """Korumalı endpoint testi"""
    print("\n🛡️ Korumalı endpoint testi başlıyor...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # SMS prediction testi
    sms_data = {
        "message": "Congratulations! You have won a free iPhone 13 Pro Max! Click here to claim your prize now!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict", json=sms_data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SMS prediction başarılı!")
            print(f"Mesaj: {result['message']}")
            print(f"Tahmin: {result['prediction']:.4f}")
            print(f"Spam: {result['is_spam']}")
            print(f"Sınıflandırma: {result['classification']}")
        else:
            print(f"❌ SMS prediction başarısız: {response.status_code}")
            print(f"Hata: {response.text}")
            
    except Exception as e:
        print(f"❌ SMS prediction hatası: {e}")

def test_user_info(token):
    """Kullanıcı bilgileri testi"""
    print("\n👤 Kullanıcı bilgileri testi başlıyor...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print("✅ Kullanıcı bilgileri alındı!")
            print(f"Kullanıcı adı: {user_info['username']}")
            print(f"Tam ad: {user_info['full_name']}")
            print(f"Email: {user_info['email']}")
        else:
            print(f"❌ Kullanıcı bilgileri alınamadı: {response.status_code}")
            print(f"Hata: {response.text}")
            
    except Exception as e:
        print(f"❌ Kullanıcı bilgileri hatası: {e}")

def test_unauthorized_access():
    """Yetkisiz erişim testi"""
    print("\n🚫 Yetkisiz erişim testi başlıyor...")
    
    sms_data = {
        "message": "Test message"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict", json=sms_data)
        
        if response.status_code == 401 or response.status_code == 403:
            print("✅ Yetkisiz erişim başarıyla engellendi!")
            print(f"Status code: {response.status_code}")
        else:
            print(f"❌ Yetkisiz erişim engellenmedi: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Yetkisiz erişim testi hatası: {e}")

def main():
    """Ana test fonksiyonu"""
    print("🚀 JWT Authentication Test Başlıyor...\n")
    
    # 1. Kullanıcı kayıt testi
    registration_success = test_registration()
    
    # 2. Duplikasyon testi
    test_duplicate_registration()
    
    # 3. Yetkisiz erişim testi
    test_unauthorized_access()
    
    # 4. Login testi (mevcut kullanıcı ile)
    token = test_login()
    
    if token:
        # 5. Korumalı endpoint testi
        test_protected_endpoint(token)
        
        # 6. Kullanıcı bilgileri testi
        test_user_info(token)
    
    # 7. Yeni kayıtlı kullanıcı ile login testi
    if registration_success:
        print("\n🔐 Yeni kullanıcı ile login testi...")
        new_login_data = {
            "username": "testuser2",
            "password": "strongpass123"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/token", json=new_login_data)
            if response.status_code == 200:
                print("✅ Yeni kullanıcı ile login başarılı!")
            else:
                print(f"❌ Yeni kullanıcı ile login başarısız: {response.status_code}")
        except Exception as e:
            print(f"❌ Yeni kullanıcı login hatası: {e}")
    
    print("\n✨ Test tamamlandı!")
    print("\n📝 Test Özeti:")
    print("- Mevcut kullanıcı: testuser / secret")
    print("- Yeni kullanıcı: testuser2 / strongpass123")
    print("- JWT token süresi: 30 dakika")
    print("- Endpoint'ler: /register, /token, /predict, /predict/batch, /users/me")
    print("- Veritabanı: PostgreSQL (localhost:5434/mydb)")
    print("- Kullanıcı bilgileri artık veritabanında saklanıyor!")
    print("- Kullanıcı kaydı ve duplikasyon kontrolü aktif!")

if __name__ == "__main__":
    main()
