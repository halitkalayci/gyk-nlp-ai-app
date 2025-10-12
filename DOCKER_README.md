# SMS Spam API - Docker Kullanım Kılavuzu

Bu kılavuz, SMS Spam API'sini Docker ile nasıl çalıştıracağınızı gösterir.

## Gereksinimler

- Docker
- Docker Compose
- Model dosyaları (`model/sms_model.h5` ve `model/tokenizer.pkl`)

## Hızlı Başlangıç

### 1. Docker Compose ile Çalıştırma (Önerilen)

```bash
# Uygulamayı ve veritabanını başlat
docker-compose up -d

# Logları izle
docker-compose logs -f

# Uygulamayı durdur
docker-compose down
```

### 2. Sadece Uygulamayı Docker ile Çalıştırma

```bash
# Docker image'ını build et
docker build -t sms-spam-api .

# Uygulamayı çalıştır (harici PostgreSQL gerekli)
docker run -d \
  --name sms-spam-api \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://postgres:password@host.docker.internal:5432/sms_spam_db" \
  -v $(pwd)/model:/app/model:ro \
  sms-spam-api
```

## Environment Değişkenleri

Aşağıdaki environment değişkenlerini `env.example` dosyasından kopyalayarak `.env` dosyası oluşturabilir veya docker-compose.yml içinde düzenleyebilirsiniz:

### Veritabanı Konfigürasyonu
- `DATABASE_URL`: PostgreSQL bağlantı URL'i
  - Varsayılan: `postgresql://postgres:abc123@localhost:5434/mydb`

### JWT Konfigürasyonu
- `SECRET_KEY`: JWT için gizli anahtar
  - Varsayılan: `gyk-ai-app-secret-key-2024-example`
- `ALGORITHM`: JWT algoritması
  - Varsayılan: `HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token geçerlilik süresi (dakika)
  - Varsayılan: `30`

### Uygulama Konfigürasyonu
- `APP_HOST`: Uygulama host adresi
  - Varsayılan: `0.0.0.0`
- `APP_PORT`: Uygulama port numarası
  - Varsayılan: `8000`

### Model Konfigürasyonu
- `MODEL_PATH`: Model dosya yolu
  - Varsayılan: `model/sms_model.h5`
- `TOKENIZER_PATH`: Tokenizer dosya yolu
  - Varsayılan: `model/tokenizer.pkl`

### Diğer Konfigürasyonlar
- `TF_CPP_MIN_LOG_LEVEL`: TensorFlow log seviyesi
  - Varsayılan: `2`
- `DEFAULT_USER_USERNAME`: Varsayılan kullanıcı adı
  - Varsayılan: `testuser`
- `DEFAULT_USER_EMAIL`: Varsayılan kullanıcı email'i
  - Varsayılan: `test@example.com`
- `DEFAULT_USER_FULLNAME`: Varsayılan kullanıcı tam adı
  - Varsayılan: `Test User`
- `DEFAULT_USER_PASSWORD`: Varsayılan kullanıcı şifresi
  - Varsayılan: `secret`

## API Endpoints

Uygulama çalıştıktan sonra şu endpoint'lere erişebilirsiniz:

- **API Dokümantasyonu**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Ana Sayfa**: http://localhost:8000/

## Test Etme

```bash
# Container içinde test çalıştır
docker-compose exec app python test_api.py

# Veya host'tan test et
python test_api.py
```

## Önemli Notlar

1. **Model Dosyaları**: `model/` dizininde `sms_model.h5` ve `tokenizer.pkl` dosyalarının bulunması gerekir.

2. **Veritabanı**: İlk çalıştırmada veritabanı tabloları otomatik olarak oluşturulur.

3. **Güvenlik**: Production ortamında mutlaka `SECRET_KEY` değişkenini değiştirin.

4. **Port**: Varsayılan olarak 8000 portunu kullanır. Değiştirmek için `APP_PORT` environment değişkenini kullanın.

5. **Volumes**: Model dosyaları read-only olarak mount edilir.

## Sorun Giderme

### Container loglarını kontrol etme:
```bash
docker-compose logs app
```

### Container içine girme:
```bash
docker-compose exec app bash
```

### Veritabanı bağlantısını kontrol etme:
```bash
docker-compose exec postgres psql -U postgres -d sms_spam_db
```

### Container'ları yeniden başlatma:
```bash
docker-compose restart
```

## Temizlik

```bash
# Container'ları ve network'ü kaldır
docker-compose down

# Volume'ları da kaldır (veritabanı verisi silinir!)
docker-compose down -v

# Image'ları kaldır
docker rmi sms-spam-api postgres:15-alpine
```
