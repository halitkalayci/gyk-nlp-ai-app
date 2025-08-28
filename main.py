from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import string 
import re
import os
import warnings

# TensorFlow uyarılarını bastır
warnings.filterwarnings('ignore', category=UserWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# FastAPI uygulamasını oluştur
app = FastAPI(
    title="SMS Spam Sınıflandırma API",
    description="SMS mesajlarını spam veya ham olarak sınıflandıran API",
    version="1.0.0"
)

# Model ve tokenizer yolları
MODEL_PATH = "model/sms_model.h5"
TOKENIZER_PATH = "model/tokenizer.pkl"

# Global değişkenler
model = None
tokenizer = None

# Pydantic modeli - API istekleri için (v1 syntax)
class SMSRequest(BaseModel):
    message: str

    class Config:
        schema_extra = {
            "example": {
                "message": "You have won a free iPhone 13 Pro Max!"
            }
        }

class SMSResponse(BaseModel):
    message: str
    prediction: float
    is_spam: bool
    classification: str

    class Config:
        schema_extra = {
            "example": {
                "message": "You have won a free iPhone 13 Pro Max!",
                "prediction": 0.9876,
                "is_spam": True,
                "classification": "Spam"
            }
        }

def load_models():
    """Model ve tokenizer'ı yükle"""
    global model, tokenizer
    
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model dosyası bulunamadı: {MODEL_PATH}")
    
    if not os.path.exists(TOKENIZER_PATH):
        raise FileNotFoundError(f"Tokenizer dosyası bulunamadı: {TOKENIZER_PATH}")
    
    try:
        # Modeli yükle - custom_objects parametresi ile uyumluluk sağla
        model = load_model(MODEL_PATH, compile=False)
        print("Model başarıyla yüklendi!")
    except Exception as e:
        print(f"Model yükleme hatası: {e}")
        # Alternatif yükleme yöntemi
        try:
            import tensorflow as tf
            model = tf.keras.models.load_model(MODEL_PATH, compile=False)
            print("Model alternatif yöntemle yüklendi!")
        except Exception as e2:
            print(f"Alternatif yükleme de başarısız: {e2}")
            raise e
    
    # Tokenizer'ı yükle
    try:
        with open(TOKENIZER_PATH, 'rb') as f:
            tokenizer = pickle.load(f)
        print("Tokenizer başarıyla yüklendi!")
    except Exception as e:
        print(f"Tokenizer yükleme hatası: {e}")
        raise e

def clean_text(text):
    """Metni temizle"""
    text = text.lower()
    text = re.sub(r'\d+', '', text)  # sayıları temizle
    text = text.translate(str.maketrans('','', string.punctuation))  # noktalama işaretlerini temizle
    return text

def predict_sms(message: str) -> dict:
    """SMS mesajını sınıflandır"""
    if model is None or tokenizer is None:
        raise HTTPException(status_code=500, detail="Model yüklenemedi")
    
    try:
        # Metni temizle
        cleaned_message = clean_text(message)
        
        # Metni tokenize et
        seq = tokenizer.texts_to_sequences([cleaned_message])
        pad = pad_sequences(seq, maxlen=100, padding='post')
        
        # Tahmin yap
        prediction = model.predict(pad, verbose=0)
        prediction_value = float(prediction[0][0])
        
        # Sonucu belirle
        is_spam = prediction_value > 0.5
        classification = "Spam" if is_spam else "Ham"
        
        return {
            "message": message,
            "prediction": prediction_value,
            "is_spam": is_spam,
            "classification": classification
        }
    except Exception as e:
        print(f"Tahmin hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Tahmin işlemi başarısız: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Uygulama başlatılırken model ve tokenizer'ı yükle"""
    try:
        load_models()
        print("Model ve tokenizer başarıyla yüklendi!")
    except Exception as e:
        print(f"Model yükleme hatası: {e}")
        # Uygulamayı durdurmak yerine sadece uyarı ver
        print("Uyarı: Model yüklenemedi. API çalışmaya devam edecek ancak tahmin endpoint'leri çalışmayacak.")

@app.get("/")
async def root():
    """Ana sayfa"""
    return {
        "message": "SMS Spam Sınıflandırma API'sine Hoş Geldiniz!",
        "endpoints": {
            "/predict": "POST - SMS mesajını sınıflandır",
            "/health": "GET - API sağlık durumu"
        }
    }

@app.get("/health")
async def health_check():
    """API sağlık durumu kontrolü"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "tokenizer_loaded": tokenizer is not None
    }

@app.post("/predict", response_model=SMSResponse)
async def predict_endpoint(request: SMSRequest):
    """SMS mesajını sınıflandır"""
    try:
        result = predict_sms(request.message)
        return SMSResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tahmin hatası: {str(e)}")

@app.post("/predict/batch")
async def predict_batch(messages: list[str]):
    """Birden fazla SMS mesajını toplu olarak sınıflandır"""
    try:
        results = []
        for message in messages:
            result = predict_sms(message)
            results.append(result)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Toplu tahmin hatası: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
