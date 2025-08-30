# JWT Authentication Sistemi (PostgreSQL)

Bu proje artık JWT (JSON Web Token) authentication sistemi ve PostgreSQL veritabanı ile korunmaktadır.

## 🔐 Authentication Özellikleri

- **JWT Token Authentication**: Güvenli token tabanlı kimlik doğrulama
- **PostgreSQL Database**: Kullanıcı bilgileri PostgreSQL veritabanında saklanır
- **Password Hashing**: bcrypt ile güvenli şifre hashleme
- **Protected Endpoints**: Predict endpoint'leri JWT koruması altında
- **SQLAlchemy ORM**: Veritabanı işlemleri için modern ORM

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

### 1. PostgreSQL Docker Container'ı Başlatın

```bash
docker run --name nlp-postgre -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=abc123 -e POSTGRES_DB=mydb -p 5434:5432 -v nlpdata:/var/lib/postgresql/data -d postgres:16
```

### 2. Gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

### 3. Veritabanını kurun:
```bash
python setup_database.py
```

### 4. Uygulamayı çalıştırın:
```bash
python main.py
```

## 📡 API Endpoint'leri

### 🔓 Açık Endpoint'ler (JWT gerektirmez)
- `GET /` - Ana sayfa ve endpoint listesi
- `GET /health` - API sağlık durumu
- `POST /register` - Yeni kullanıcı kaydı
- `POST /token` - Kullanıcı girişi ve JWT token alma

### 🔒 Korumalı Endpoint'ler (JWT gerektirir)
- `POST /predict` - SMS spam sınıflandırma
- `POST /predict/batch` - Toplu SMS sınıflandırma  
- `GET /users/me` - Kullanıcı bilgileri

## 📝 Kullanıcı Kaydı

```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "yenikullanici",
    "email": "yeni@example.com",
    "full_name": "Yeni Kullanıcı",
    "password": "güçlüşifre123"
  }'
```

Yanıt:
```json
{
  "id": 2,
  "username": "yenikullanici",
  "email": "yeni@example.com", 
  "full_name": "Yeni Kullanıcı",
  "message": "Kullanıcı başarıyla kaydedildi!"
}
```

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

## 🗄️ Veritabanı Bilgileri

**PostgreSQL Bağlantı Ayarları:**
- Host: localhost
- Port: 5434
- Database: mydb
- Username: postgres
- Password: abc123

**Kullanıcı Tablosu Şeması:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    full_name VARCHAR NOT NULL,
    hashed_password VARCHAR NOT NULL,
    disabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

## 🔒 Güvenlik Notları

1. **SECRET_KEY**: Üretim ortamında mutlaka değiştirin ve güvenli tutun
2. **HTTPS**: Üretimde mutlaka HTTPS kullanın
3. **Token Süresi**: Güvenlik ihtiyaçlarınıza göre ayarlayın
4. **Password Policy**: Güçlü şifre politikaları uygulayın
5. **Database Security**: Üretimde güçlü veritabanı şifreleri kullanın

## 🎯 Kullanım Senaryosu

1. **Giriş**: `/token` endpoint'ine kullanıcı adı ve şifre gönderin
2. **Token Al**: Yanıtta dönen JWT token'ı saklayın
3. **API Kullan**: Token'ı Authorization header'ında Bearer token olarak gönderin
4. **SMS Analiz**: Artık `/predict` endpoint'lerini güvenle kullanabilirsiniz

## 🛠️ Veritabanı Yönetimi

### Alembic ile Migration
```bash
# İlk migration oluştur
alembic revision --autogenerate -m "Initial migration"

# Migration'ları uygula
alembic upgrade head
```

### Manuel Veritabanı Bağlantısı
```bash
# PostgreSQL CLI ile bağlan
psql -h localhost -p 5434 -U postgres -d mydb
```

## 📊 Swagger UI

API dokümantasyonunu görüntülemek için:
- http://localhost:8000/docs

Burada JWT authentication ile korumalı endpoint'leri test edebilirsiniz.

## 🧪 Test Etme

### Otomatik Test
```bash
python test_jwt.py
```

### Manuel Test
```bash
# 1. Yeni kullanıcı kaydı
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser3", "email": "test3@example.com", "full_name": "Test User 3", "password": "mypassword"}'

# 2. Token al
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser3", "password": "mypassword"}'

# 3. Kullanıcı bilgilerini getir
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. SMS predict et
curl -X POST "http://localhost:8000/predict" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Free iPhone! Click now!"}'
```
