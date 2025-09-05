# ELOHAB Akademi Test Suite

Bu proje için kapsamlı test mühendisliği yapılmıştır. Testler farklı seviyelerde ve kategorilerde organize edilmiştir.

## 🏗️ Test Yapısı

```
tests/
├── conftest.py              # Test konfigürasyonu ve fixtures
├── unit/                    # Unit testler
│   ├── test_models.py      # Veritabanı modelleri testleri
│   └── test_routes.py      # Flask route testleri
├── integration/             # Entegrasyon testleri
│   └── test_database_integration.py
├── functional/              # Fonksiyonel testler
│   └── test_user_workflows.py
├── security/                # Güvenlik testleri
│   └── test_security.py
└── README.md               # Bu dosya
```

## 🧪 Test Kategorileri

### 1. Unit Tests (`tests/unit/`)
- **test_models.py**: Veritabanı modellerinin temel işlevselliğini test eder
  - User model: Kullanıcı oluşturma, paket yönetimi
  - Course model: Ders oluşturma, string temsili
  - Note model: Not oluşturma, dosya bilgileri
  - Question model: Soru oluşturma
  - Project model: Proje oluşturma

- **test_routes.py**: Flask route'larının işlevselliğini test eder
  - Authentication routes: Giriş, kayıt
  - Protected routes: Korumalı sayfalar
  - Admin routes: Admin yetkileri
  - Content routes: İçerik sayfaları
  - Search routes: Arama işlevselliği

### 2. Integration Tests (`tests/integration/`)
- **test_database_integration.py**: Veritabanı entegrasyonunu test eder
  - User-course ilişkileri
  - Cascade silme işlemleri
  - Paket yönetimi
  - İçerik arama entegrasyonu
  - Dosya yönetimi entegrasyonu

### 3. Functional Tests (`tests/functional/`)
- **test_user_workflows.py**: Kullanıcı iş akışlarını test eder
  - Kullanıcı kayıt iş akışı
  - Not yönetimi iş akışı
  - Proje yönetimi iş akışı
  - Arama iş akışı
  - Profil yönetimi iş akışı

### 4. Security Tests (`tests/security/`)
- **test_security.py**: Güvenlik önlemlerini test eder
  - Authentication güvenliği
  - Authorization ve erişim kontrolü
  - Input validation ve sanitization
  - Veri gizliliği koruması

## 🚀 Test Çalıştırma

### Gereksinimler
```bash
pip install -r requirements.txt
```

### Tüm Testleri Çalıştırma
```bash
python run_tests.py
```

### Kategori Bazında Test Çalıştırma
```bash
# Unit testler
python -m pytest tests/unit/ -v

# Integration testler
python -m pytest tests/integration/ -v

# Functional testler
python -m pytest tests/functional/ -v

# Security testler
python -m pytest tests/security/ -v
```

### Coverage ile Test Çalıştırma
```bash
python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing
```

## 📊 Test Coverage

Test coverage raporu `htmlcov/` dizininde oluşturulur. Bu rapor:
- Hangi kod satırlarının test edildiğini
- Hangi satırların test edilmediğini
- Genel test coverage yüzdesini gösterir

## 🔧 Test Konfigürasyonu

### conftest.py
- Test veritabanı konfigürasyonu
- Test fixtures (sample_user, sample_course, etc.)
- Flask test client konfigürasyonu
- Database session yönetimi

### pytest.ini
- Test path konfigürasyonu
- Coverage ayarları
- Test marker'ları
- Output formatı

## 📝 Test Yazma Kuralları

1. **Test İsimlendirme**: `test_` ile başlamalı
2. **Test Sınıfları**: `Test` ile başlamalı
3. **Assertion'lar**: Açık ve anlaşılır olmalı
4. **Test Verisi**: Her test için temiz veri kullanılmalı
5. **Fixture Kullanımı**: Tekrarlanan kod için fixture'lar kullanılmalı

## 🐛 Test Hatalarını Çözme

### Yaygın Hatalar
1. **Import Errors**: `app.py` import hatası
2. **Database Errors**: Test veritabanı bağlantı sorunları
3. **Route Errors**: Flask route bulunamama hatası

### Çözüm Önerileri
1. Test dizininde `__init__.py` dosyası oluşturun
2. PYTHONPATH'i proje kök dizinine ayarlayın
3. Test veritabanının doğru konumda olduğundan emin olun

## 📈 Test Geliştirme

### Yeni Test Ekleme
1. Uygun kategori dizininde test dosyası oluşturun
2. Test sınıfı ve metodları ekleyin
3. Gerekli fixture'ları kullanın
4. Test'i çalıştırın ve sonuçları kontrol edin

### Test Coverage Artırma
1. Test edilmeyen kod bloklarını belirleyin
2. Edge case'ler için testler ekleyin
3. Error handling için testler yazın
4. Performance testleri ekleyin

## 🎯 Test Hedefleri

- [x] Unit test coverage: %80+
- [x] Integration test coverage: %70+
- [x] Functional test coverage: %60+
- [x] Security test coverage: %90+
- [x] Overall test coverage: %75+

## 📚 Faydalı Kaynaklar

- [Pytest Documentation](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/en/2.3.x/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html)
- [Test Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)
