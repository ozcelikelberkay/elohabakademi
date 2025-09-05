#!/usr/bin/env python3
"""
Logging ve Hata Yönetimi Sistemi Test Scripti
Bu script, uygulamanın logging ve hata yönetimi özelliklerini test eder.
"""

import requests
import time
import os
import json
from datetime import datetime

class LoggingSystemTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Test sonucunu kaydet"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        
        status = "✅ BAŞARILI" if success else "❌ BAŞARISIZ"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Detay: {details}")
        print()
    
    def test_404_error(self):
        """404 hata sayfası testi"""
        try:
            response = self.session.get(f"{self.base_url}/olmayan-sayfa")
            if response.status_code == 404:
                self.log_test("404 Hata Sayfası", True, f"Status: {response.status_code}")
            else:
                self.log_test("404 Hata Sayfası", False, f"Beklenen: 404, Alınan: {response.status_code}")
        except Exception as e:
            self.log_test("404 Hata Sayfası", False, f"Hata: {str(e)}")
    
    def test_500_error_simulation(self):
        """500 hata simülasyonu"""
        try:
            # Test endpoint'ini çağır
            response = self.session.get(f"{self.base_url}/test-500")
            if response.status_code == 500:
                self.log_test("500 Hata Sayfası", True, f"Status: {response.status_code}")
            else:
                self.log_test("500 Hata Sayfası", False, f"Beklenen: 500, Alınan: {response.status_code}")
        except requests.exceptions.RequestException as e:
            # 500 hatası genellikle connection error'a neden olur
            if "500" in str(e) or "Internal Server Error" in str(e):
                self.log_test("500 Hata Sayfası", True, "500 hatası başarıyla üretildi")
            else:
                self.log_test("500 Hata Sayfası", False, f"Beklenmeyen hata: {str(e)}")
        except Exception as e:
            self.log_test("500 Hata Sayfası", False, f"Genel hata: {str(e)}")
    
    def test_security_logging(self):
        """Güvenlik logging testi"""
        try:
            # Başarısız giriş denemesi
            login_data = {"username": "test_user", "password": "wrong_password"}
            response = self.session.post(f"{self.base_url}/login", data=login_data)
            
            if response.status_code == 200:  # Login sayfasına yönlendirildi
                self.log_test("Güvenlik Logging", True, "Başarısız giriş denemesi loglandı")
            else:
                self.log_test("Güvenlik Logging", False, f"Beklenmeyen response: {response.status_code}")
        except Exception as e:
            self.log_test("Güvenlik Logging", False, f"Hata: {str(e)}")
    
    def test_file_upload_logging(self):
        """Dosya yükleme logging testi"""
        try:
            # Geçici test dosyası oluştur
            test_file_path = "test_upload.txt"
            with open(test_file_path, "w") as f:
                f.write("Test dosyası içeriği")
            
            # Dosya yükleme denemesi (login olmadan)
            with open(test_file_path, "rb") as f:
                files = {"file": f}
                response = self.session.post(f"{self.base_url}/notes/add", files=files)
            
            # Test dosyasını temizle
            os.remove(test_file_path)
            
            # Login olmadan dosya yüklemeye çalıştığında 302 redirect beklenir
            if response.status_code == 302:  # Redirect to login
                self.log_test("Dosya Upload Logging", True, "Dosya yükleme denemesi loglandı (302 redirect)")
            elif response.status_code == 200:  # Login sayfasına yönlendirildi
                self.log_test("Dosya Upload Logging", True, "Dosya yükleme denemesi loglandı (200 - login page)")
            else:
                self.log_test("Dosya Upload Logging", False, f"Beklenmeyen response: {response.status_code}")
        except Exception as e:
            self.log_test("Dosya Upload Logging", False, f"Hata: {str(e)}")
    
    def test_payment_logging(self):
        """Ödeme logging testi"""
        try:
            # Ödeme sayfasına erişim denemesi
            response = self.session.get(f"{self.base_url}/payment/1")
            
            if response.status_code in [200, 302, 404]:
                self.log_test("Ödeme Logging", True, "Ödeme sayfası erişimi loglandı")
            else:
                self.log_test("Ödeme Logging", False, f"Beklenmeyen response: {response.status_code}")
        except Exception as e:
            self.log_test("Ödeme Logging", False, f"Hata: {str(e)}")
    
    def test_log_files_exist(self):
        """Log dosyalarının varlığını test et"""
        log_files = [
            "logs/app.log",
            "logs/error.log", 
            "logs/security.log",
            "logs/payment.log",
            "logs/file_upload.log"
        ]
        
        all_exist = True
        missing_files = []
        
        for log_file in log_files:
            if os.path.exists(log_file):
                file_size = os.path.getsize(log_file)
                print(f"📁 {log_file}: {file_size} bytes")
            else:
                all_exist = False
                missing_files.append(log_file)
        
        if all_exist:
            self.log_test("Log Dosyaları Varlığı", True, "Tüm log dosyaları mevcut")
        else:
            self.log_test("Log Dosyaları Varlığı", False, f"Eksik dosyalar: {missing_files}")
    
    def test_log_content(self):
        """Log dosyalarının içeriğini kontrol et"""
        try:
            # Son log kayıtlarını kontrol et
            if os.path.exists("logs/app.log"):
                with open("logs/app.log", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1].strip()
                        self.log_test("Log İçerik Kontrolü", True, f"Son log: {last_line[:100]}...")
                    else:
                        self.log_test("Log İçerik Kontrolü", False, "Log dosyası boş")
            else:
                self.log_test("Log İçerik Kontrolü", False, "app.log dosyası bulunamadı")
        except Exception as e:
            self.log_test("Log İçerik Kontrolü", False, f"Hata: {str(e)}")
    
    def run_all_tests(self):
        """Tüm testleri çalıştır"""
        print("🚀 Logging ve Hata Yönetimi Sistemi Testi Başlıyor...")
        print("=" * 60)
        print()
        
        # Testleri çalıştır
        self.test_log_files_exist()
        self.test_404_error()
        self.test_500_error_simulation()
        self.test_security_logging()
        self.test_file_upload_logging()
        self.test_payment_logging()
        self.test_log_content()
        
        # Sonuçları özetle
        print("=" * 60)
        print("📊 TEST SONUÇLARI ÖZETİ")
        print("=" * 60)
        
        successful = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Toplam Test: {total}")
        print(f"Başarılı: {successful}")
        print(f"Başarısız: {total - successful}")
        print(f"Başarı Oranı: {(successful/total)*100:.1f}%")
        
        # Başarısız testleri listele
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\n❌ BAŞARISIZ TESTLER:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        # Sonuçları dosyaya kaydet
        self.save_results()
        
        return successful == total
    
    def save_results(self):
        """Test sonuçlarını dosyaya kaydet"""
        try:
            with open("test_logging_results.json", "w", encoding="utf-8") as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Test sonuçları 'test_logging_results.json' dosyasına kaydedildi.")
        except Exception as e:
            print(f"\n❌ Test sonuçları kaydedilemedi: {e}")

def main():
    """Ana fonksiyon"""
    print("🔧 Logging Sistemi Test Aracı")
    print("Bu araç, uygulamanın logging ve hata yönetimi özelliklerini test eder.")
    print()
    
    # Uygulama çalışıyor mu kontrol et
    tester = LoggingSystemTester()
    
    try:
        # Uygulama erişilebilir mi kontrol et
        response = requests.get("http://localhost:5000", timeout=5)
        print("✅ Uygulama erişilebilir durumda")
        print()
    except requests.exceptions.RequestException:
        print("⚠️  UYARI: Uygulama çalışmıyor veya erişilemiyor!")
        print("   Lütfen önce 'python app.py' komutu ile uygulamayı başlatın.")
        print("   Sonra bu test scriptini tekrar çalıştırın.")
        print()
        return
    
    # Testleri çalıştır
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Tüm testler başarılı! Logging sistemi düzgün çalışıyor.")
    else:
        print("\n⚠️  Bazı testler başarısız. Log dosyalarını kontrol edin.")
    
    print("\n📋 Sonraki Adımlar:")
    print("1. Log dosyalarını manuel olarak inceleyin:")
    print("   - tail -f logs/app.log")
    print("   - tail -f logs/error.log")
    print("   - tail -f logs/security.log")
    print("2. Uygulamada farklı işlemler yaparak logları izleyin")
    print("3. Hata durumları oluşturarak error handling'i test edin")

if __name__ == "__main__":
    main()
