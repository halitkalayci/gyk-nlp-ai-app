# JWT Authentication Sistemi

Bu proje artık JWT (JSON Web Token) authentication sistemi ile korunmaktadır.

## 🔐 Authentication Özellikleri

- **JWT Token Authentication**: Güvenli token tabanlı kimlik doğrulama
- **In-memory User Database**: Test amaçlı bellek içi kullanıcı veritabanı
- **Password Hashing**: bcrypt ile güvenli şifre hashleme
- **Protected Endpoints**: Predict endpoint'leri JWT koruması altında

## 👤 Test Kullanıcısı

```json
{
  "username": "testuser",
  "password": "secret",
  "full_name": "Test User",
  "email": "test@example.com"
}
```

## 🚀 Kurulum

1. Gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Uygulamayı çalıştırın:
```bash
python main.py
```

## 📡 API Endpoint'leri

### 🔓 Açık Endpoint'ler (JWT gerektirmez)
- `GET /` - Ana sayfa ve endpoint listesi
- `GET /health` - API sağlık durumu
- `POST /token` - Kullanıcı girişi ve JWT token alma

### 🔒 Korumalı Endpoint'ler (JWT gerektirir)
- `POST /predict` - SMS spam sınıflandırma
- `POST /predict/batch` - Toplu SMS sınıflandırma  
- `GET /users/me` - Kullanıcı bilgileri

## 🔑 JWT Token Alma

```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "secret"
  }'
```

Yanıt:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## 🛡️ Korumalı Endpoint Kullanımı

Token aldıktan sonra, korumalı endpoint'lere erişmek için Authorization header'ı kullanın:

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "Congratulations! You won a free iPhone!"
  }'
```

## 🧪 Test Etme

Sistemi test etmek için hazırlanan test script'ini kullanabilirsiniz:

```bash
python test_jwt.py
```

Bu script şunları test eder:
- ✅ Yetkisiz erişimin engellenmesi
- ✅ Kullanıcı girişi ve token alma
- ✅ Korumalı endpoint'lere erişim
- ✅ Kullanıcı bilgileri alma

## ⚙️ Konfigürasyon

`main.py` dosyasındaki önemli ayarlar:

```python
SECRET_KEY = "gyk-ai-app-secret-key-2024-example"  # Üretimde değiştirin!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

## 🔒 Güvenlik Notları

1. **SECRET_KEY**: Üretim ortamında mutlaka değiştirin ve güvenli tutun
2. **HTTPS**: Üretimde mutlaka HTTPS kullanın
3. **Token Süresi**: Güvenlik ihtiyaçlarınıza göre ayarlayın
4. **Password Policy**: Güçlü şifre politikaları uygulayın

## 🎯 Kullanım Senaryosu

1. **Giriş**: `/token` endpoint'ine kullanıcı adı ve şifre gönderin
2. **Token Al**: Yanıtta dönen JWT token'ı saklayın
3. **API Kullan**: Token'ı Authorization header'ında Bearer token olarak gönderin
4. **SMS Analiz**: Artık `/predict` endpoint'lerini güvenle kullanabilirsiniz

## 📊 Swagger UI

API dokümantasyonunu görüntülemek için:
- http://localhost:8000/docs

Burada JWT authentication ile korumalı endpoint'leri test edebilirsiniz.
