import subprocess
import sys
import os

def run_command(command):
    """Komutu çalıştır ve sonucu döndür"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def clean_environment():
    """Sanal ortamı temizle"""
    print("🧹 Sanal ortam temizleniyor...")
    
    # Tüm paketleri listele ve kaldır
    success, output = run_command("pip freeze")
    if success and output.strip():
        packages = [line.split('==')[0] for line in output.strip().split('\n') if '==' in line]
        # Temel paketleri koruma
        protected_packages = ['pip', 'setuptools', 'wheel']
        packages_to_remove = [pkg for pkg in packages if pkg not in protected_packages]
        
        if packages_to_remove:
            packages_str = ' '.join(packages_to_remove)
            run_command(f"pip uninstall {packages_str} -y")
            print("✓ Mevcut paketler temizlendi")
    
    # Cache temizle
    run_command("pip cache purge")
    print("✓ Pip cache temizlendi")

def install_packages():
    """Paketleri sırasıyla yükle"""
    print("📦 Paketler yükleniyor...")
    
    # Önce temel paketleri güncelleyelim
    run_command("pip install --upgrade pip setuptools wheel")
    
    # Paketleri tek tek yükle (çakışma önleme)
    packages = [
        "numpy==1.23.5",
        "typing-extensions==4.4.0", 
        "tensorflow==2.10.1",
        "pydantic==1.10.2",
        "fastapi==0.88.0",
        "uvicorn[standard]==0.20.0",
        "python-multipart==0.0.5",
        "requests==2.28.2"
    ]
    
    for package in packages:
        print(f"Yükleniyor: {package}")
        success, output = run_command(f"pip install {package}")
        if success:
            print(f"✓ {package} yüklendi")
        else:
            print(f"❌ {package} yüklenemedi: {output}")
            return False
    
    return True

def main():
    print("🚀 SMS Spam API Kurulum Scripti")
    print("=" * 50)
    
    # 1. Ortamı temizle
    clean_environment()
    
    # 2. Paketleri yükle
    if install_packages():
        print("\n✅ Tüm paketler başarıyla yüklendi!")
        
        # 3. Model kontrolü
        print("\n🔍 Model kontrolü yapılıyor...")
        if os.path.exists("model/sms_model.h5") and os.path.exists("model/tokenizer.pkl"):
            print("✓ Model dosyaları mevcut")
            
            try:
                import tensorflow as tf
                print(f"✓ TensorFlow {tf.__version__} yüklendi")
                
                # Model yükleme testi
                print("🧪 Model yükleme testi...")
                model = tf.keras.models.load_model("model/sms_model.h5", compile=False)
                print("✓ Model başarıyla yüklendi!")
                print(f"  - Giriş şekli: {model.input_shape}")
                print(f"  - Çıkış şekli: {model.output_shape}")
                
            except Exception as e:
                print(f"⚠ Model yükleme hatası: {e}")
        else:
            print("⚠ Model dosyaları bulunamadı!")
        
        print("\n🎉 Kurulum tamamlandı!")
        print("\n📋 Sonraki adımlar:")
        print("1. API'yi başlat: python main.py")
        print("2. Test et: python test_api.py")
        print("3. Dokümantasyon: http://localhost:8000/docs")
        
    else:
        print("\n❌ Kurulum başarısız!")
        print("\n🔧 Manuel kurulum deneyin:")
        print("pip install --upgrade pip")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()
