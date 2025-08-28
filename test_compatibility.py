#!/usr/bin/env python3
"""
Paket uyumluluk testi scripti
Tüm paketlerin doğru yüklendiğini ve uyumlu olduğunu kontrol eder
"""

import sys
import importlib
import traceback

def test_import(package_name, alias=None):
    """Paketi import etmeyi dener"""
    try:
        if alias:
            module = importlib.import_module(package_name)
            return True, getattr(module, '__version__', 'Sürüm bilgisi yok')
        else:
            module = importlib.import_module(package_name)
            return True, getattr(module, '__version__', 'Sürüm bilgisi yok')
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Beklenmeyen hata: {str(e)}"

def main():
    print("🔍 Paket Uyumluluk Testi")
    print("=" * 50)
    
    # Test edilecek paketler
    packages = {
        'numpy': 'numpy',
        'tensorflow': 'tensorflow',
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'pydantic': 'pydantic',
        'requests': 'requests',
        'typing_extensions': 'typing_extensions'
    }
    
    results = {}
    all_passed = True
    
    for display_name, package_name in packages.items():
        print(f"\n📦 Test ediliyor: {display_name}")
        success, version_or_error = test_import(package_name)
        
        if success:
            print(f"✅ {display_name}: {version_or_error}")
            results[display_name] = {'status': 'OK', 'version': version_or_error}
        else:
            print(f"❌ {display_name}: {version_or_error}")
            results[display_name] = {'status': 'FAIL', 'error': version_or_error}
            all_passed = False
    
    # TensorFlow özel testleri
    print(f"\n🧪 TensorFlow Özel Testleri")
    try:
        import tensorflow as tf
        print(f"✅ TensorFlow sürümü: {tf.__version__}")
        print(f"✅ Keras sürümü: {tf.keras.__version__}")
        
        # GPU kontrolü
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            print(f"✅ GPU bulundu: {len(gpus)} adet")
        else:
            print("ℹ️  GPU bulunamadı (CPU modunda çalışacak)")
            
        # Basit model testi
        print("🧪 Basit model testi...")
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(1, input_shape=(1,))
        ])
        model.compile(optimizer='adam', loss='mse')
        print("✅ Model oluşturma ve derleme başarılı")
        
    except Exception as e:
        print(f"❌ TensorFlow testi başarısız: {e}")
        all_passed = False
    
    # FastAPI testi
    print(f"\n🧪 FastAPI Testi")
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel
        
        app = FastAPI()
        
        class TestModel(BaseModel):
            message: str
            
        @app.get("/")
        def root():
            return {"message": "Test"}
            
        print("✅ FastAPI uygulaması oluşturma başarılı")
        
    except Exception as e:
        print(f"❌ FastAPI testi başarısız: {e}")
        all_passed = False
    
    # Model dosyalarını kontrol et
    print(f"\n📁 Model Dosyalarını Kontrol")
    import os
    
    model_files = {
        'SMS Model': 'model/sms_model.h5',
        'Tokenizer': 'model/tokenizer.pkl'
    }
    
    for name, path in model_files.items():
        if os.path.exists(path):
            size = os.path.getsize(path) / (1024 * 1024)  # MB
            print(f"✅ {name}: {path} ({size:.2f} MB)")
        else:
            print(f"❌ {name}: {path} bulunamadı")
            all_passed = False
    
    # Özet
    print(f"\n📊 Test Özeti")
    print("=" * 30)
    
    passed = sum(1 for r in results.values() if r['status'] == 'OK')
    total = len(results)
    
    print(f"Başarılı: {passed}/{total}")
    
    if all_passed:
        print("🎉 Tüm testler başarılı! API çalıştırılmaya hazır.")
        print("\n📋 Sonraki adımlar:")
        print("1. python main.py")
        print("2. http://localhost:8000/docs")
    else:
        print("⚠️  Bazı testler başarısız. Kurulumu kontrol edin.")
        print("\n🔧 Önerilen çözüm:")
        print("python setup.py")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
