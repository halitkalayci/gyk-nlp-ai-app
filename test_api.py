import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Sağlık kontrolü testi"""
    response = requests.get(f"{BASE_URL}/health")
    print("Sağlık Kontrolü:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    print()

def test_predict_single():
    """Tek SMS tahmin testi"""
    # Spam örneği
    spam_message = {
        "message": "You have won a free iPhone 13 Pro Max! Click the link to claim your prize."
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=spam_message)
    print("Spam SMS Tahmini:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    print()
    
    # Ham örneği
    ham_message = {
        "message": "I'm sorry to hear that you're having trouble with your account. Let me know if I can help you with anything."
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=ham_message)
    print("Ham SMS Tahmini:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    print()

def test_predict_batch():
    """Toplu SMS tahmin testi"""
    messages = [
        "You have won a free iPhone 13 Pro Max! Click the link to claim your prize.",
        "I'm sorry to hear that you're having trouble with your account. Let me know if I can help you with anything.",
        "URGENT: Your account has been suspended. Call now to reactivate!",
        "Hi, how are you doing today? Would you like to grab coffee later?"
    ]
    
    response = requests.post(f"{BASE_URL}/predict/batch", json=messages)
    print("Toplu SMS Tahmini:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    print()

if __name__ == "__main__":
    print("API Test Başlatılıyor...\n")
    
    try:
        test_health()
        test_predict_single()
        test_predict_batch()
        print("Tüm testler tamamlandı!")
    except requests.exceptions.ConnectionError:
        print("Hata: API sunucusuna bağlanılamadı. Lütfen sunucunun çalıştığından emin olun.")
    except Exception as e:
        print(f"Hata: {e}")
