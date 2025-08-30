from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import string 
import re
import os
import warnings
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func

# TensorFlow uyarılarını bastır
warnings.filterwarnings('ignore', category=UserWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# JWT ayarları
SECRET_KEY = "gyk-ai-app-secret-key-2024-example"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database ayarları
DATABASE_URL = "postgresql://postgres:abc123@localhost:5434/mydb"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

# Authentication modelleri
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    
    class Config:
        schema_extra = {
            "example": {
                "username": "newuser",
                "email": "newuser@example.com",
                "full_name": "New User",
                "password": "strongpassword123"
            }
        }

class UserRegisterResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    message: str
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "username": "newuser",
                "email": "newuser@example.com",
                "full_name": "New User",
                "message": "Kullanıcı başarıyla kaydedildi!"
            }
        }

# SQLAlchemy User modeli
class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    disabled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

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

# Authentication fonksiyonları
def verify_password(plain_password, hashed_password):
    """Şifreyi doğrula"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Şifreyi hash'le"""
    return pwd_context.hash(password)

def get_user(db: Session, username: str):
    """Kullanıcıyı veritabanından getir"""
    return db.query(UserDB).filter(UserDB.username == username).first()

def get_user_by_email(db: Session, email: str):
    """Email ile kullanıcıyı getir"""
    return db.query(UserDB).filter(UserDB.email == email).first()

def create_user(db: Session, username: str, email: str, full_name: str, password: str):
    """Yeni kullanıcı oluştur"""
    hashed_password = get_password_hash(password)
    db_user = UserDB(
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    """Kullanıcıyı doğrula"""
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Access token oluştur"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Mevcut kullanıcıyı getir"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token doğrulanamadı",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: UserDB = Depends(get_current_user)):
    """Aktif kullanıcıyı getir"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="İnaktif kullanıcı")
    return current_user

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

def init_db():
    """Veritabanını başlat ve tabloları oluştur"""
    try:
        Base.metadata.create_all(bind=engine)
        print("Veritabanı tabloları başarıyla oluşturuldu!")
        
        # İlk kullanıcıyı oluştur
        db = SessionLocal()
        try:
            # Kullanıcı zaten var mı kontrol et
            existing_user = get_user(db, "testuser")
            if not existing_user:
                create_user(
                    db=db,
                    username="testuser",
                    email="test@example.com",
                    full_name="Test User",
                    password="secret"
                )
                print("Test kullanıcısı başarıyla oluşturuldu!")
            else:
                print("Test kullanıcısı zaten mevcut.")
        finally:
            db.close()
            
    except Exception as e:
        print(f"Veritabanı başlatma hatası: {e}")
        raise e

@app.on_event("startup")
async def startup_event():
    """Uygulama başlatılırken model, tokenizer ve veritabanını yükle"""
    try:
        # Veritabanını başlat
        init_db()
        
        # Model ve tokenizer'ı yükle
        load_models()
        print("Model ve tokenizer başarıyla yüklendi!")
    except Exception as e:
        print(f"Başlatma hatası: {e}")
        # Uygulamayı durdurmak yerine sadece uyarı ver
        print("Uyarı: Başlatma sırasında hata oluştu. Bazı özellikler çalışmayabilir.")

@app.post("/register", response_model=UserRegisterResponse)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """Yeni kullanıcı kaydı"""
    # Kullanıcı adı kontrolü
    existing_user = get_user(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kullanıcı adı zaten kullanılıyor"
        )
    
    # Email kontrolü
    existing_email = get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email adresi zaten kullanılıyor"
        )
    
    # Şifre uzunluk kontrolü
    if len(user_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Şifre en az 6 karakter olmalıdır"
        )
    
    try:
        # Yeni kullanıcı oluştur
        new_user = create_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            password=user_data.password
        )
        
        return UserRegisterResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            full_name=new_user.full_name,
            message="Kullanıcı başarıyla kaydedildi!"
        )
        
    except Exception as e:
        print(f"Kullanıcı kaydetme hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kullanıcı kaydedilirken bir hata oluştu"
        )

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: UserLogin, db: Session = Depends(get_db)):
    """Kullanıcı girişi ve token oluşturma"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yanlış kullanıcı adı veya şifre",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
async def root():
    """Ana sayfa"""
    return {
        "message": "SMS Spam Sınıflandırma API'sine Hoş Geldiniz!",
        "endpoints": {
            "/register": "POST - Yeni kullanıcı kaydı",
            "/token": "POST - Kullanıcı girişi (username: testuser, password: secret)",
            "/predict": "POST - SMS mesajını sınıflandır (JWT gerekli)",
            "/predict/batch": "POST - Toplu SMS sınıflandırma (JWT gerekli)",
            "/health": "GET - API sağlık durumu",
            "/users/me": "GET - Kullanıcı bilgileri (JWT gerekli)"
        },
        "example_registration": {
            "username": "yenikullanici",
            "email": "yeni@example.com",
            "full_name": "Yeni Kullanıcı",
            "password": "güçlüşifre123"
        }
    }

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: UserDB = Depends(get_current_active_user)):
    """Mevcut kullanıcı bilgilerini getir"""
    return User(
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        disabled=current_user.disabled
    )

@app.get("/health")
async def health_check():
    """API sağlık durumu kontrolü"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "tokenizer_loaded": tokenizer is not None
    }

@app.post("/predict", response_model=SMSResponse)
async def predict_endpoint(request: SMSRequest, current_user: UserDB = Depends(get_current_active_user)):
    """SMS mesajını sınıflandır (JWT gerekli)"""
    try:
        result = predict_sms(request.message)
        return SMSResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tahmin hatası: {str(e)}")

@app.post("/predict/batch")
async def predict_batch(messages: list[str], current_user: UserDB = Depends(get_current_active_user)):
    """Birden fazla SMS mesajını toplu olarak sınıflandır (JWT gerekli)"""
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
