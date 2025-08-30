#!/usr/bin/env python3
"""
JWT Authentication Test Script
Bu script JWT authentication sistemini test eder.
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_login():
    """Login testi"""
    print("🔐 Login testi başlıyor...")
    
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
    
    # 1. Yetkisiz erişim testi
    test_unauthorized_access()
    
    # 2. Login testi
    token = test_login()
    
    if token:
        # 3. Korumalı endpoint testi
        test_protected_endpoint(token)
        
        # 4. Kullanıcı bilgileri testi
        test_user_info(token)
    
    print("\n✨ Test tamamlandı!")
    print("\n📝 Test Özeti:")
    print("- Kullanıcı adı: testuser")
    print("- Şifre: secret")
    print("- JWT token süresi: 30 dakika")
    print("- Korumalı endpoint'ler: /predict, /predict/batch, /users/me")

if __name__ == "__main__":
    main()
