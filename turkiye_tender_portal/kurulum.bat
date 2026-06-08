@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
echo ============================================
echo   Turkiye Ihale Takip - Kurulum
echo ============================================
echo.
echo [1/6] Sanal ortam olusturuluyor...
python -m venv .venv
call .venv\Scripts\activate
echo [2/6] pip guncelleniyor...
python -m pip install --upgrade pip
echo [3/6] Bagimliliklar yukleniyor (birkac dakika surebilir)...
pip install -r requirements.txt
echo [4/6] Veritabani hazirlaniyor...
python manage.py migrate
echo [5/6] Iller / demo veri / kullanicilar yukleniyor...
python manage.py seed_provinces
python manage.py seed_demo_data
python manage.py seed_users
echo [6/6] Kurulum tamamlandi.
echo.
echo Sunucuyu baslatmak icin: baslat.bat
echo Giris: http://127.0.0.1:8000/login/  ( demo / Demo.2026! )
echo.
pause
