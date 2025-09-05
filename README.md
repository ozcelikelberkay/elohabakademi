# Elohab Akademi

Elektronik ve Haberleşme Mühendisliği öğrencileri için kapsamlı kaynak platformu. Akademi kurulu ama yardımlaşma için tasarlandı.

## 🎯 Proje Amacı

Elohab Akademi, **Hoctech** kuruluşu tarafından Elektronik ve Haberleşme Mühendisliği öğrencilerinin akademik başarılarını artırmak, bilgi paylaşımını teşvik etmek ve mühendislik eğitiminde kaliteyi yükseltmek amacıyla geliştirilmiştir.

**Hoctech**, eğitim teknolojileri alanında uzmanlaşmış, öğrencilere kaliteli eğitim içerikleri sunmayı hedefleyen bir kuruluştur.

## ✨ Özellikler

### 🎓 Sınıf Bazlı Ders Programları
- 1. Sınıf: Temel mühendislik dersleri ve hazırlık programı
- 2. Sınıf: Elektronik temelleri ve devre analizi
- 3. Sınıf: Haberleşme teorisi ve proje geliştirme
- 4. Sınıf: Bitirme projesi ve uzmanlık dersleri

### 📚 Eğitim Kaynakları
- **Ders Notları**: Tüm sınıflar için detaylı ders notları (PDF, DOCX, resim formatları)
- **Çıkmış Sorular**: Geçmiş yıllarda çıkan sınav soruları ve çözümleri
- **Projeler**: Sınıf seviyelerine uygun proje örnekleri (ZIP, RAR, kod dosyaları)
- **Mentorluk**: Uzman mentorlar ile birebir görüşme

### 💳 Paket Sistemi ve Ödeme
- **Temel Paket**: 49 ₺/ay - 150+ Ders Notu, 100+ Çıkmış Soru, 50+ Proje
- **Orta Paket**: 99 ₺/ay - 300+ Ders Notu, 250+ Çıkmış Soru, 100+ Proje
- **Pro Paket**: 199 ₺/ay - Sınırsız içerik, birebir mentorluk, staj desteği
- **Iyzico Entegrasyonu**: Güvenli ödeme sistemi, taksit seçenekleri

### 👥 Mentorlar
- **Bedirhan Durmuş**: Elektronik ve Web Geliştirme
- **Ömer Güzeller**: Haberleşme ve Yapay Zeka
- **Berkay Özçelikel**: Otomasyon ve Mikroişlemciler

### 🔐 Kullanıcı Sistemi
- Üye olma ve giriş yapma
- Kişiselleştirilmiş içerik
- Admin paneli ile platform yönetimi
- Paket bazlı erişim kontrolü

### 📁 Gelişmiş Dosya Yönetimi
- Çoklu dosya formatı desteği (PDF, DOCX, ZIP, RAR, resimler, kod dosyaları)
- Güvenli dosya yükleme ve doğrulama
- Dosya boyutu kontrolü (Notlar: 50MB, Projeler: 100MB)
- Otomatik dosya organizasyonu

### 📊 Kapsamlı Loglama Sistemi
- Uygulama logları
- Hata takibi
- Güvenlik olayları
- Ödeme işlemleri
- Dosya yükleme aktiviteleri

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- Flask 2.3.3+
- SQLAlchemy 2.0.21+

### Adımlar
1. Projeyi klonlayın:
```bash
git clone <repository-url>
cd ELOHAB-AKADEM--main
```

2. Sanal ortam oluşturun (önerilen):
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# veya
source venv/bin/activate  # Linux/Mac
```

3. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

4. Iyzico API anahtarlarını yapılandırın:
   - `payment_handler.py` dosyasında API anahtarlarını güncelleyin
   - Test için sandbox, production için gerçek API kullanın

5. Uygulamayı çalıştırın:
```bash
python app.py
```

6. Tarayıcınızda `http://localhost:5000` adresine gidin

## 🎨 Tasarım

Platform, modern ve kullanıcı dostu bir arayüze sahiptir:
- **Renk Teması**: Yeşil ve beyaz tonları
- **Responsive Design**: Mobil ve masaüstü uyumlu
- **Modern UI**: Bootstrap 5 ve Font Awesome ikonları
- **Kullanıcı Deneyimi**: Kolay navigasyon ve sezgisel tasarım
- **Footer**: "Bu akademi bir **Hoctech** kuruluşudur" bilgisi

## 📁 Proje Yapısı

```
ELOHAB-AKADEM--main/
├── app.py                 # Ana Flask uygulaması (ödeme rotaları dahil)
├── dersler.txt           # Ders listesi
├── file_manager.py       # Gelişmiş dosya yönetim sistemi
├── payment_handler.py    # Iyzico ödeme entegrasyonu
├── logging_config.py     # Loglama konfigürasyonu
├── requirements.txt      # Python paketleri (güncellenmiş)
├── PAYMENT_README.md     # Ödeme sistemi dokümantasyonu
├── pytest.ini           # Test konfigürasyonu
├── run_tests.py          # Test çalıştırma scripti
├── README.md             # Proje dokümantasyonu
├── instance/
│   └── elohab.db        # SQLite veritabanı
├── logs/                 # Log dosyaları
│   ├── app.log          # Uygulama logları
│   ├── error.log        # Hata logları
│   ├── security.log     # Güvenlik logları
│   ├── payment.log      # Ödeme logları
│   └── file_upload.log  # Dosya yükleme logları
├── uploads/              # Yüklenen dosyalar
│   ├── notes/           # Ders notları
│   ├── projects/        # Proje dosyaları
│   └── temp/            # Geçici dosyalar
├── templates/            # HTML şablonları
│   ├── base.html        # Ana şablon
│   ├── index.html       # Ana sayfa
│   ├── about.html       # Hakkımızda
│   ├── register.html    # Güncellenmiş üye olma
│   ├── login.html       # Giriş
│   ├── grade.html       # Sınıf sayfaları
│   ├── notes.html       # Ders notları
│   ├── questions.html   # Çıkmış sorular
│   ├── projects.html    # Projeler
│   ├── mentorship.html  # Güncellenmiş mentorluk
│   ├── payment.html     # Yeni ödeme sayfası
│   ├── admin_login.html # Admin girişi
│   ├── admin_dashboard.html # Admin paneli
│   ├── add_note.html    # Not ekleme
│   ├── add_project.html # Proje ekleme
│   ├── edit_note.html   # Not düzenleme
│   ├── edit_project.html # Proje düzenleme
│   ├── edit_profile.html # Profil düzenleme
│   ├── search_results.html # Arama sonuçları
│   └── errors/          # Hata sayfaları
│       ├── 403.html     # Yetkisiz erişim
│       ├── 404.html     # Sayfa bulunamadı
│       └── 500.html     # Sunucu hatası
└── tests/                # Kapsamlı test suite
    ├── conftest.py      # Test konfigürasyonu
    ├── unit/            # Birim testler
    ├── integration/     # Entegrasyon testleri
    ├── functional/      # Fonksiyonel testler
    └── security/        # Güvenlik testleri
```

## 🔧 Teknik Detaylar

### Backend
- **Framework**: Flask 2.3.3
- **Veritabanı**: SQLite (SQLAlchemy 2.0.21 ORM)
- **Kimlik Doğrulama**: Session-based authentication
- **Şifre Güvenliği**: Werkzeug password hashing
- **Ödeme Sistemi**: Iyzico entegrasyonu
- **Dosya Yönetimi**: Gelişmiş dosya işleme ve güvenlik

### Frontend
- **CSS Framework**: Bootstrap 5
- **İkonlar**: Font Awesome 6
- **Responsive**: Mobile-first design
- **JavaScript**: Minimal, Bootstrap bundle

### Veritabanı Modelleri
- **User**: Kullanıcı bilgileri, yetkileri ve paket bilgileri
- **Course**: Ders bilgileri ve sınıf seviyeleri
- **Note**: Ders notları ve içerikleri
- **Question**: Çıkmış sorular ve çözümleri
- **Project**: Proje örnekleri
- **Mentorship**: Mentor bilgileri

### Güvenlik Özellikleri
- Dosya türü ve boyut kontrolü
- MIME türü doğrulama
- Güvenli dosya yükleme
- XSS ve CSRF koruması
- Şifre hashleme

## 💳 Ödeme Sistemi

### Paket Detayları
- **Temel Paket (49 ₺/ay)**: 150+ Ders Notu, 100+ Çıkmış Soru, 50+ Proje
- **Orta Paket (99 ₺/ay)**: 300+ Ders Notu, 250+ Çıkmış Soru, 100+ Proje, Video İçerikler
- **Pro Paket (199 ₺/ay)**: Sınırsız içerik, birebir mentorluk, staj desteği

### Ödeme Özellikleri
- Iyzico güvenli ödeme sistemi
- Kredi kartı, banka kartı desteği
- Taksit seçenekleri (1, 2, 3, 6, 9 ay)
- SSL korumalı ödeme
- Otomatik hesap aktivasyonu

## 👨‍💻 Admin Paneli

Admin kullanıcıları şu işlemleri yapabilir:
- Kullanıcı yönetimi (görüntüleme, silme)
- Ders ekleme ve silme
- Platform istatistiklerini görüntüleme
- İçerik yönetimi
- Dosya yönetimi
- Log dosyalarını görüntüleme

**Varsayılan Admin Bilgileri:**
- Kullanıcı Adı: `admin`
- Şifre: `admin123`

## 🧪 Test Sistemi

Proje kapsamlı test coverage ile gelir:
- **Birim Testler**: Model ve route testleri
- **Entegrasyon Testleri**: Veritabanı entegrasyonu
- **Fonksiyonel Testler**: Kullanıcı iş akışları
- **Güvenlik Testleri**: Güvenlik açıklarının tespiti
- **Coverage**: Test coverage raporları

Test çalıştırma:
```bash
python run_tests.py
# veya
pytest
```

## 🌟 Öne Çıkan Özellikler

1. **Sınıf Bazlı Navigasyon**: Her sınıf için özel ders programları
2. **Akıllı Filtreleme**: Ders notları ve soruları derse göre filtreleme
3. **Responsive Tasarım**: Tüm cihazlarda mükemmel görünüm
4. **Güvenli Kimlik Doğrulama**: Şifre hashleme ve session yönetimi
5. **Admin Yönetimi**: Kapsamlı platform yönetim araçları
6. **Ödeme Sistemi**: Güvenli ve kullanıcı dostu ödeme
7. **Gelişmiş Dosya Yönetimi**: Çoklu format desteği ve güvenlik
8. **Kapsamlı Loglama**: Detaylı aktivite takibi
9. **Test Coverage**: Yüksek kalite ve güvenilirlik

## 🤝 Katkıda Bulunma

Projeye katkıda bulunmak için:
1. Projeyi fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

### Test Gereksinimleri
- Tüm yeni özellikler için test yazın
- Mevcut testleri çalıştırın ve geçtiğinden emin olun
- Test coverage'ı koruyun

## 📞 İletişim

- **Genel İletişim**: hoctech@hotmail.com.tr
- **Hoctech Kuruluşu**: 
  - **E-posta**: hoctech@hotmail.com.tr
  - **Web Sitesi**: [Hoctech](https://hoctech.com.tr)
  - **Adres**: İstanbul, Türkiye
  - **Sektör**: Eğitim Teknolojileri ve Akademi Yönetimi

- **Mentorlar**: 
  - Bedirhan Durmuş: bedirhan_durmus@hotmail.com
  - Ömer Güzeller: omer.guzeller@elohab.edu.tr
  - Berkay Özçelikel: berkay.ozcelikel@elohab.edu.tr

## 📄 Lisans

Bu proje **Hoctech** kuruluşu tarafından eğitim amaçlı geliştirilmiştir. Akademi kurulu ama yardımlaşma için tasarlandı.

**Hoctech** tüm haklarını saklı tutar. Bu platform eğitim amaçlı kullanım için tasarlanmıştır.

## 🙏 Teşekkürler

- Flask geliştiricileri
- Bootstrap ekibi
- Font Awesome ekibi
- Iyzico ekibi
- Tüm katkıda bulunanlara

---

**Elohab Akademi** - Elektronik ve Haberleşme Mühendisliği öğrencileri için kapsamlı kaynak platformu 🚀

*Bu akademi bir **Hoctech** kuruluşudur* 