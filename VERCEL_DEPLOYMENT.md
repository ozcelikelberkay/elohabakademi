# Vercel Deployment Rehberi

Bu proje Vercel platformunda deploy edilmek üzere hazırlanmıştır.

## 🚀 Hızlı Başlangıç

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

## 📁 Gerekli Dosyalar

- `vercel.json` - Vercel konfigürasyonu
- `vercel_app.py` - Vercel için optimize edilmiş Flask uygulaması
- `requirements-vercel.txt` - Gerekli Python paketleri
- `runtime.txt` - Python runtime versiyonu
- `build.sh` - Build script

## ⚠️ Önemli Notlar

### Veritabanı
- **SQLite yerine PostgreSQL kullanın**: Vercel'de SQLite dosya sistemi kalıcı değildir
- **Environment Variables**: Veritabanı bağlantı bilgilerini Vercel dashboard'da ayarlayın

### Dosya Yükleme
- **Statik dosyalar**: `assets/` klasörü otomatik olarak serve edilir
- **Upload klasörü**: Vercel'de dosya yükleme için external storage (AWS S3, Cloudinary) kullanın

### Environment Variables
Vercel dashboard'da şu environment variable'ları ayarlayın:
```
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=your-postgresql-connection-string
```

## 🔧 Konfigürasyon

### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "vercel_app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "vercel_app.py"
    }
  ]
}
```

## 📊 Deployment Sonrası

1. **Domain**: Vercel otomatik olarak bir domain verir
2. **Custom Domain**: Kendi domain'inizi ekleyebilirsiniz
3. **HTTPS**: Otomatik olarak SSL sertifikası verilir
4. **CDN**: Global CDN ile hızlı erişim

## 🐛 Sorun Giderme

### Build Hataları
- Python versiyonunu kontrol edin (`runtime.txt`)
- Requirements dosyasındaki paket versiyonlarını kontrol edin
- Vercel logs'u inceleyin

### Runtime Hataları
- Environment variable'ları kontrol edin
- Veritabanı bağlantısını test edin
- Flask debug mode'u kapatın

## 🔄 Güncelleme

Projeyi güncellemek için:
```bash
vercel --prod
```

## 📚 Ek Kaynaklar

- [Vercel Python Documentation](https://vercel.com/docs/runtimes/python)
- [Flask on Vercel](https://vercel.com/guides/deploying-flask-with-vercel)
- [Vercel Environment Variables](https://vercel.com/docs/environment-variables)
