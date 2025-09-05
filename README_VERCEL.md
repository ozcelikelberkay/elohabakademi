# ELOHAB Akademi - Vercel Deployment

Bu proje, ELOHAB Akademi platformunun Vercel üzerinde çalışan versiyonudur.

## 🚀 Hızlı Deployment

### 1. Vercel CLI Kurulumu
```bash
npm install -g vercel
```

### 2. Proje Klasörüne Git
```bash
cd ELOHAB-AKADEM--main
```

### 3. Vercel'e Giriş Yap
```bash
vercel login
```

### 4. Projeyi Deploy Et
```bash
vercel
```

## 📋 Özellikler

- ✅ Flask web uygulaması
- ✅ Kullanıcı kayıt ve giriş sistemi
- ✅ Not, proje ve soru yönetimi
- ✅ Admin dashboard
- ✅ Responsive tasarım
- ✅ Vercel optimizasyonu

## 🔧 Teknik Detaylar

- **Framework**: Flask 2.3.3
- **Database**: SQLAlchemy (SQLite/PostgreSQL)
- **Python Version**: 3.11
- **Deployment**: Vercel

## 📁 Dosya Yapısı

```
ELOHAB-AKADEM--main/
├── vercel_app.py          # Ana Flask uygulaması
├── vercel.json            # Vercel konfigürasyonu
├── requirements-vercel.txt # Python paketleri
├── runtime.txt            # Python runtime
├── build.sh               # Build script
├── templates/             # HTML şablonları
├── assets/                # Statik dosyalar
└── VERCEL_DEPLOYMENT.md  # Deployment rehberi
```

## ⚠️ Önemli Notlar

1. **Veritabanı**: Production'da PostgreSQL kullanın
2. **Dosya Yükleme**: External storage (AWS S3, Cloudinary) kullanın
3. **Environment Variables**: Vercel dashboard'da ayarlayın
4. **SQLite**: Sadece development için, production'da kullanmayın

## 🌐 Environment Variables

Vercel dashboard'da şunları ayarlayın:
```
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=your-postgresql-url
```

## 🔄 Güncelleme

```bash
vercel --prod
```

## 📚 Dökümantasyon

Detaylı deployment rehberi için: [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md)

## 🆘 Destek

Sorun yaşarsanız:
1. Vercel logs'u kontrol edin
2. Environment variable'ları doğrulayın
3. Requirements dosyasını kontrol edin
4. Python runtime versiyonunu kontrol edin

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.
