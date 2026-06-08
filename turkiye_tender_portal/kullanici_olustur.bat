@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
if not exist ".venv\Scripts\activate.bat" (
  echo HATA: Once kurulum.bat dosyasini calistirin.
  pause & exit /b
)
call .venv\Scripts\activate
echo Veritabani hazirlaniyor...
python manage.py migrate --noinput
echo Iller yukleniyor...
python manage.py seed_provinces
echo Demo veri...
python manage.py seed_demo_data
echo Kullanicilar olusturuluyor...
python manage.py seed_users
echo.
echo ============================================
echo  Giris bilgileri (yukaridaki tabloya bakin)
echo  Ornek:  demo  /  Demo.2026!
echo ============================================
echo.
pause
