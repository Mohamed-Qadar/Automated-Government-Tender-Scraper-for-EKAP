# Türkiye İhale Takip Sistemi

Giriş zorunlu (login-only), ticari kullanım için tasarlanmış bir **Türkiye geneli
kamu ihale takip** web uygulaması. Kullanıcılar EKAP'ı manuel ziyaret etmeden;
il, ilçe, kategori, ihale türü, tarih aralığı veya anahtar kelimeye göre kamu
ihalelerini filtreler ve temiz bir **Excel raporu** olarak indirir.

> **Not:** Sistem yalnızca herkese açık, resmî kamu verilerini kullanacak şekilde
> tasarlanmıştır. Elazığ yalnızca varsayılan/demo ildir; **81 ilin tamamı** ve
> "Tüm Türkiye" araması desteklenir.

## Yasal Not
- Yalnızca **herkese açık resmî kaynaklardan** (öncelikle EKAP) veri çekilir.
- Giriş, e-imza, mobil imza, CAPTCHA, ödeme duvarı veya güvenlik korumaları
  **hiçbir şekilde aşılmaz**.
- Rakip sitelerin (ör. ihalesitesi.com) tasarımı, veritabanı, korumalı içeriği,
  logosu veya metni **kopyalanmaz**; bu proje özgün bir tasarıma sahiptir.
- Kaynak siteler yüklenmez; **kontrollü istekler** (gecikme, yeniden deneme
  limiti, zaman aşımı, loglama) kullanılır.
- MVP, canlı çekim yerine **mock (demo) veri adaptörü** ile çalışır. Gerçek EKAP
  adaptörü ayrı bir adım olarak, yalnızca giriş gerektirmeyen resmî kaynaklarla
  doldurulmalıdır.

## Teknoloji
Python · Django · Django Templates · Bootstrap 5 · SQLite (MVP) ·
PostgreSQL-ready · openpyxl · requests/httpx · Playwright (gerekirse) ·
django-environ.

## Kurulum

### 1. Sanal ortam oluşturma
```bash
cd turkiye_tender_portal
python -m venv .venv
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

### 2. Bağımlılıkları yükleme
```bash
pip install -r requirements.txt
```

### 3. Ortam değişkenleri
```bash
cp .env.example .env
# .env içindeki SECRET_KEY ve diğer değerleri düzenleyin.
```

### 4. Veritabanı migrasyonları
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. 81 ili yükleme
```bash
python manage.py seed_provinces
```

### 6. Admin kullanıcısı oluşturma
```bash
python manage.py createsuperuser
```

### 7. (Opsiyonel) Demo veri üretme
```bash
python manage.py seed_demo_data
```

### 8. Sunucuyu çalıştırma
```bash
python manage.py runserver
```
- Uygulama: http://127.0.0.1:8000/  (giriş zorunlu)
- Yönetim: http://127.0.0.1:8000/admin/

## İhale Çekme (il bazında / Türkiye geneli)
```bash
python manage.py fetch_tenders --province "Elazığ"
python manage.py fetch_tenders --province "İstanbul"
python manage.py fetch_tenders --all-turkiye
# İsteğe bağlı: --category, --keyword, --date-from 2026-01-01 --date-to 2026-06-01
```


## Gerçek EKAP Verisi (Canlı)

Sistem artık **gerçek EKAP v2 public ihale arama** verisini çekebilir. Kaynak,
giriş gerektirmeyen herkese açık arama servisidir
(`https://ekapv2.kik.gov.tr/ekap/search` sayfasının kullandığı API).

- Kaynak seçimi `.env` içindeki `USE_MOCK_TENDER_SOURCE` ile yapılır:
  - `True`  → demo (mock) veri
  - `False` → **gerçek EKAP verisi** (varsayılan ayar artık budur)
- Sıralama: API'den `orderBy=ihaleTarihi`, `desc` ile **en yeni en üstte** gelir;
  site listesinde de ilan tarihine göre yeni→eski sıralanır.
- Çekim kontrollü yapılır (gecikme, yeniden deneme, zaman aşımı, loglama) ve
  hiçbir giriş/e-imza/CAPTCHA/ödeme duvarı aşılmaz.

### Gerçek veri çekme komutları
```bash
# Tüm Türkiye, en yeni 100 ilan (önce demo kayıtları temizler)
python manage.py fetch_tenders --all-turkiye --limit 100 --clear-mock

# Tek il
python manage.py fetch_tenders --province "Elazığ" --limit 50
python manage.py fetch_tenders --province "İstanbul" --limit 50

# Tarih aralığı / tür / anahtar kelime
python manage.py fetch_tenders --province "Ankara" --date-from 2026-06-01 --keyword "yapım"
```
Windows'ta `ekap_veri_cek.bat` dosyasına çift tıklayarak da gerçek veriyi
çekebilirsiniz. Uygulama içindeki **"Yeni İlanları Çek"** butonu da artık doğrudan
EKAP'tan çeker.

> Not: EKAP public servisi zaman zaman erişim/biçim değiştirebilir. Çekim
> başarısız olursa panelde "son çekim: başarısız" görünür ve mevcut kayıtlar
> korunur; `USE_MOCK_TENDER_SOURCE=True` ile demo moda dönülebilir.
> Gerçek çekim, ağ erişimi olan kendi makinenizde çalıştırılmalıdır.

## Excel Dışa Aktarma
```bash
python manage.py export_tenders_excel --province "Elazığ"
python manage.py export_tenders_excel --all-turkiye
```
Dosyalar `exports/excel/` altına kaydedilir. Uygulama içinden "Excel İndir"
butonu da aynı raporu mevcut filtrelerle üretip indirir.

## Abonelik Aktivasyonu (manuel)
MVP'de online ödeme yoktur. Ödeme önce manuel alınır, abonelik admin panelinden
açılır/uzatılır:
1. `/admin/` → **Kullanıcı Profilleri**.
2. İlgili kullanıcıyı seçin.
3. Durumu **Aktif** yapın ve **Abonelik Bitiş** tarihini girin; veya listeden
   kullanıcıları seçip "Aboneliği 30/365 gün uzat" toplu işlemini kullanın.

Yeni kullanıcılar otomatik olarak **deneme (trial)** aboneliğiyle başlar
(`DEFAULT_TRIAL_DAYS`).

## Erişim Kuralları
- Giriş yapmamış kullanıcı → `/login/`'e yönlendirilir.
- Aboneliği pasif/dolmuş kullanıcı → `/subscription-expired/`'e yönlendirilir.
- Süper kullanıcı her şeye erişebilir.
- Panel, ihale listesi/detayı ve Excel yalnızca aktif abonelikle açılır.

## Testler
```bash
python manage.py test tests
```
Kapsam: yetkisiz erişim engeli, süresi dolmuş kullanıcı Excel alamaz, aktif
kullanıcı listeye erişir, il filtresi, "Tüm Türkiye" filtresi, mükerrer kayıt
engeli, Excel üretimi, çekim sonrası log oluşumu.

## Proje Yapısı
```
turkiye_tender_portal/
├── config/            # ayarlar, url, wsgi/asgi
├── accounts/          # auth + abonelik (UserProfile, paketler, decorator)
├── tenders/           # iller, ilçeler, ihaleler, servis katmanı, sayfalar
│   ├── services/      # adapter, parser, cleaner, duplicate, filter, excel
│   └── management/    # seed_provinces, seed_demo_data, fetch, export
├── templates/         # base + login
├── exports/excel/     # üretilen raporlar
├── logs/              # uygulama logları
└── tests/             # test paketi
```

## Zamanlanmış Çekim (Scheduled Synchronization)

Sistemin arka planda sürekli ve güncel kalması için `sync_ekap_tenders` yönetim komutu düzenli aralıklarla (ör. 5-10 dakikada bir) çalıştırılmalıdır.

### Windows (Task Scheduler) Kurulumu
1. **Görev Zamanlayıcı'yı** (Task Scheduler) açın ve **Yeni Temel Görev** oluşturun.
2. Tetikleyici olarak **Günlük** seçin ve görevi her 5 ya da 10 dakikada bir tekrarlayacak şekilde ayarlayın.
3. Eylem olarak **Program Başlat** seçin.
4. Program/Komut kutusuna doğrudan python komutunu tetikleyecek parametreleri girin:
   - **Program/kod:** `C:\Users\Moha-qadar\OneDrive\Desktop\ihale\turkiye_tender_portal\.venv\Scripts\python.exe`
   - **Bağımsız değişkenler ekle:** `manage.py sync_ekap_tenders --all-turkiye --limit 50 --days 1`
   - **Başlama yeri:** `C:\Users\Moha-qadar\OneDrive\Desktop\ihale\turkiye_tender_portal`

### Linux (Crontab) Kurulumu
Her 10 dakikada bir çalışacak şekilde crontab kaydı ekleyin:
```bash
*/10 * * * * cd /path/to/turkiye_tender_portal && /path/to/turkiye_tender_portal/.venv/bin/python manage.py sync_ekap_tenders --all-turkiye --limit 50 --days 1 >> /path/to/turkiye_tender_portal/logs/cron.log 2>&1
```

## Gelecek Dağıtım Planı (Deployment)
- **Veritabanı:** `DATABASE_URL` ortam değişkeni ile PostgreSQL'e geçiş (kod hazır).
- **Statik dosyalar:** `collectstatic` + WhiteNoise/CDN.
- **Sunucu:** Gunicorn/Uvicorn + Nginx; `DEBUG=False`, gerçek `ALLOWED_HOSTS`.
- **Zamanlanmış çekim:** Yukarıda detaylandırıldığı gibi `sync_ekap_tenders` cron görevi.
- **Ödeme:** iyzico / Stripe / havale onayı (ikinci faz).
