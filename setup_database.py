#!/usr/bin/env python3
"""
PostgreSQL Database Setup Script
Bu script veritabanını kurar ve test kullanıcısını oluşturur.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import time

# Database ayarları
DATABASE_URL = "postgresql://postgres:abc123@localhost:5434/mydb"
ADMIN_URL = "postgresql://postgres:abc123@localhost:5434/postgres"  # Admin bağlantısı

def wait_for_postgres(max_retries=30, delay=2):
    """PostgreSQL'in hazır olmasını bekle"""
    print("🔄 PostgreSQL bağlantısı kontrol ediliyor...")
    
    for i in range(max_retries):
        try:
            engine = create_engine(ADMIN_URL)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ PostgreSQL hazır!")
            return True
        except OperationalError:
            if i == max_retries - 1:
                print(f"❌ PostgreSQL {max_retries * delay} saniye sonra hala hazır değil!")
                return False
            print(f"⏳ PostgreSQL henüz hazır değil... ({i+1}/{max_retries})")
            time.sleep(delay)
    
    return False

def create_database():
    """Veritabanını oluştur"""
    print("🗄️ Veritabanı oluşturuluyor...")
    
    try:
        # Admin bağlantısı ile veritabanını kontrol et/oluştur
        admin_engine = create_engine(ADMIN_URL)
        
        with admin_engine.connect() as conn:
            # Autocommit modunda çalış
            conn.execute(text("COMMIT"))
            
            # Veritabanının var olup olmadığını kontrol et
            result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'mydb'"))
            
            if result.fetchone():
                print("✅ 'mydb' veritabanı zaten mevcut!")
            else:
                # Veritabanını oluştur
                conn.execute(text("CREATE DATABASE mydb"))
                print("✅ 'mydb' veritabanı başarıyla oluşturuldu!")
                
    except Exception as e:
        print(f"❌ Veritabanı oluşturma hatası: {e}")
        return False
    
    return True

def test_connection():
    """Veritabanı bağlantısını test et"""
    print("🧪 Veritabanı bağlantısı test ediliyor...")
    
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Bağlantı başarılı! PostgreSQL versiyonu: {version.split(',')[0]}")
            return True
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return False

def setup_tables():
    """Tabloları oluştur"""
    print("📋 Tablolar oluşturuluyor...")
    
    try:
        # main.py'den modelleri import et
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from main import Base, engine, create_user, SessionLocal
        
        # Tabloları oluştur
        Base.metadata.create_all(bind=engine)
        print("✅ Tablolar başarıyla oluşturuldu!")
        
        # Test kullanıcısını oluştur
        print("👤 Test kullanıcısı oluşturuluyor...")
        db = SessionLocal()
        try:
            from main import get_user
            existing_user = get_user(db, "testuser")
            if not existing_user:
                create_user(
                    db=db,
                    username="testuser",
                    email="test@example.com",
                    full_name="Test User",
                    password="secret"
                )
                print("✅ Test kullanıcısı başarıyla oluşturuldu!")
                print("   - Kullanıcı adı: testuser")
                print("   - Şifre: secret")
                print("   - Email: test@example.com")
            else:
                print("✅ Test kullanıcısı zaten mevcut!")
        finally:
            db.close()
            
        return True
        
    except Exception as e:
        print(f"❌ Tablo oluşturma hatası: {e}")
        return False

def main():
    """Ana setup fonksiyonu"""
    print("🚀 PostgreSQL Database Setup Başlıyor...\n")
    
    # 1. PostgreSQL'in hazır olmasını bekle
    if not wait_for_postgres():
        print("\n❌ PostgreSQL bağlantısı kurulamadı!")
        print("Docker container'ın çalıştığından emin olun:")
        print("docker run --name nlp-postgre -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=abc123 -e POSTGRES_DB=mydb -p 5434:5432 -v nlpdata:/var/lib/postgresql/data -d postgres:16")
        sys.exit(1)
    
    # 2. Veritabanını oluştur
    if not create_database():
        print("\n❌ Veritabanı oluşturulamadı!")
        sys.exit(1)
    
    # 3. Bağlantıyı test et
    if not test_connection():
        print("\n❌ Veritabanı bağlantısı test edilemedi!")
        sys.exit(1)
    
    # 4. Tabloları oluştur
    if not setup_tables():
        print("\n❌ Tablolar oluşturulamadı!")
        sys.exit(1)
    
    print("\n✨ Database setup tamamlandı!")
    print("\n📝 Bağlantı Bilgileri:")
    print("- Host: localhost")
    print("- Port: 5434")
    print("- Database: mydb")
    print("- Username: postgres")
    print("- Password: abc123")
    print("\n👤 Test Kullanıcısı:")
    print("- Username: testuser")
    print("- Password: secret")
    print("- Email: test@example.com")
    
    print("\n🎯 Sonraki Adımlar:")
    print("1. API'yi başlatın: python main.py")
    print("2. Test edin: python test_jwt.py")
    print("3. Swagger UI: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
