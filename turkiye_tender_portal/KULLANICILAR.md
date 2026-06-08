# Test Kullanıcıları — Türkiye İhale Takip Sistemi

Aşağıdaki kullanıcılar `python manage.py seed_users` komutuyla oluşturulur.
Komut tekrar çalıştırılabilir (şifre/abonelik günceller, kopya oluşturmaz).

| Kullanıcı Adı  | Şifre          | Rol              | Abonelik       | Amaç |
|----------------|----------------|------------------|----------------|------|
| `admin`        | `Admin.2026!`  | Süper Kullanıcı  | Aktif (10 yıl) | Yönetim paneli `/admin/` + her şeye erişim |
| `demo`         | `Demo.2026!`   | Normal Kullanıcı | Aktif (1 yıl)  | Ana demo hesabı (Elazığ firması) |
| `elazig`       | `Elazig.2026!` | Normal Kullanıcı | Aktif (30 gün) | Aylık abonelik örneği |
| `istanbul`     | `Istanbul.2026!`| Normal Kullanıcı| Aktif (30 gün) | Farklı il örneği |
| `deneme`       | `Deneme.2026!` | Normal Kullanıcı | Deneme (14 gün)| Trial abonelik testi |
| `suresidolmus` | `Suresi.2026!` | Normal Kullanıcı | Süresi Dolmuş  | Erişim engeli testi (panele giremez) |

## Nasıl oluşturulur (kendi makinende)
```bash
cd turkiye_tender_portal
python manage.py migrate
python manage.py seed_provinces
python manage.py seed_demo_data     # demo ihale verisi (opsiyonel ama önerilir)
python manage.py seed_users         # yukarıdaki kullanıcılar
python manage.py runserver
```
Sonra tarayıcıda: http://127.0.0.1:8000/login/

## Doğrulanan davranışlar
- Giriş yapmamış kullanıcı → `/login/`'e yönlendirilir.
- `demo` (aktif) → panel, ihale listesi ve Excel indirme çalışır.
- `suresidolmus` (dolmuş) → giriş yapar ama panel/Excel `/subscription-expired/`'e yönlendirir.
- `admin` → `/admin/` üzerinden aboneialık açma/uzatma yapabilir.

> Güvenlik notu: Bu şifreler yalnızca yerel test içindir. Canlıya geçerken
> `seed_users.py` içindeki şifreleri değiştirin veya bu komutu hiç kullanmayın.
