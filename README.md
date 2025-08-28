# SMS Spam Sınıflandırma API

Bu proje, SMS mesajlarını spam veya ham olarak sınıflandıran bir FastAPI uygulamasıdır. TensorFlow/Keras ile eğitilmiş bir model kullanarak gerçek zamanlı tahmin yapar.

## Özellikler

- 🚀 FastAPI ile yüksek performanslı REST API
- 🤖 TensorFlow/Keras modeli entegrasyonu
- 📊 Tek SMS ve toplu SMS sınıflandırma
- 🔍 Otomatik API dokümantasyonu (Swagger UI)
- 💾 Model ve tokenizer dosya yönetimi
- 🏥 Sağlık kontrolü endpoint'i

## Kurulum

### Otomatik Kurulum (Önerilen)

```bash
# 1. Uyumluluk testi (opsiyonel)
python test_compatibility.py

# 2. Kurulum scriptini çalıştır
python setup.py
```

### Manuel Kurulum

#### 1. Sanal Ortam Oluşturma

```bash
# Sanal ortam oluştur
python -m venv be-env

# Sanal ortamı aktifleştir (Windows)
be-env\Scripts\activate

# Sanal ortamı aktifleştir (Linux/Mac)
source be-env/bin/activate
```

#### 2. Bağımlılıkları Yükleme

```bash
# Önce pip'i güncelle
pip install --upgrade pip setuptools wheel

# Paketleri tek tek yükle (çakışma önleme)
pip install numpy==1.23.5
pip install typing-extensions==4.4.0
pip install tensorflow==2.10.1
pip install pydantic==1.10.2
pip install fastapi==0.88.0
pip install uvicorn[standard]==0.20.0
pip install python-multipart==0.0.5
pip install requests==2.28.2
```

**Alternatif (hızlı kurulum):**
```bash
pip install -r requirements.txt
```

#### 3. Model Dosyalarını Kontrol Etme

`model/` klasöründe aşağıdaki dosyaların bulunduğundan emin olun:
- `sms_model.h5` - Eğitilmiş model
- `tokenizer.pkl` - Metin tokenizer'ı

## Kullanım

### API'yi Başlatma

```bash
python main.py
```

veya

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### API Endpoint'leri

#### 1. Ana Sayfa
```
GET /
```
API hakkında genel bilgi ve mevcut endpoint'leri döner.

#### 2. Sağlık Kontrolü
```
GET /health
```
API'nin sağlık durumunu ve model yükleme durumunu kontrol eder.

#### 3. Tek SMS Sınıflandırma
```
POST /predict
```

**İstek Gövdesi:**
```json
{
    "message": "You have won a free iPhone 13 Pro Max!"
}
```

**Yanıt:**
```json
{
    "message": "You have won a free iPhone 13 Pro Max!",
    "prediction": 0.9876,
    "is_spam": true,
    "classification": "Spam"
}
```

#### 4. Toplu SMS Sınıflandırma
```
POST /predict/batch
```

**İstek Gövdesi:**
```json
[
    "You have won a free iPhone 13 Pro Max!",
    "Hi, how are you doing today?"
]
```

**Yanıt:**
```json
{
    "results": [
        {
            "message": "You have won a free iPhone 13 Pro Max!",
            "prediction": 0.9876,
            "is_spam": true,
            "classification": "Spam"
        },
        {
            "message": "Hi, how are you doing today?",
            "prediction": 0.1234,
            "is_spam": false,
            "classification": "Ham"
        }
    ]
}
```

## API Dokümantasyonu

API başlatıldıktan sonra aşağıdaki URL'lerden dokümantasyona erişebilirsiniz:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Test Etme

API'yi test etmek için:

```bash
python test_api.py
```

Bu script:
- API sağlık durumunu kontrol eder
- Spam ve ham SMS örnekleri ile tahmin yapar
- Toplu tahmin işlevini test eder

## Sorun Giderme

### Bağımlılık Çakışması

Eğer paket yükleme sırasında çakışma hatası alırsanız:

```bash
# Tüm paketleri temizle
pip uninstall tensorflow tensorflow-intel fastapi uvicorn pydantic pydantic-core typing-extensions -y

# Yeniden yükle
pip install -r requirements.txt
```

### Model Yükleme Hatası

Model yükleme hatası alırsanız:

```bash
# Model uyumluluğunu kontrol et
python check_tensorflow.py

# Gerekirse modeli dönüştür
python convert_model.py
```

## Model Bilgileri

- **Model Türü:** TensorFlow/Keras Sequential Model
- **Giriş:** Metin (maksimum 100 token)
- **Çıkış:** Spam olasılığı (0-1 arası)
- **Eşik Değeri:** 0.5 (0.5'ten büyük = Spam)

## Metin Ön İşleme

Model, gelen metinleri şu şekilde ön işler:
1. Küçük harfe çevirme
2. Sayıları kaldırma
3. Noktalama işaretlerini kaldırma
4. Tokenization ve padding (maksimum 100 token)

## Hata Yönetimi

API aşağıdaki hata durumlarını yönetir:
- Model dosyaları bulunamadığında
- Geçersiz istek formatında
- Model yükleme hatalarında
- Tahmin sırasında oluşan hatalarda

## Geliştirme

### Yeni Özellik Ekleme

1. `main.py` dosyasında yeni endpoint'ler ekleyin
2. Gerekirse yeni Pydantic modelleri tanımlayın
3. Test dosyasını güncelleyin
4. README'yi güncelleyin

### Model Güncelleme

1. Yeni model dosyasını `model/` klasörüne koyun
2. Gerekirse `MODEL_PATH` değişkenini güncelleyin
3. Model yapısı değiştiyse `predict_sms` fonksiyonunu güncelleyin

## Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

## İletişim

Sorularınız için lütfen issue açın veya iletişime geçin.
