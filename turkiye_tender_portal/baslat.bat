@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
if not exist ".venv\Scripts\activate.bat" (
  echo Once kurulum.bat dosyasini calistirin.
  pause & exit /b
)
call .venv\Scripts\activate
echo Veritabani / kullanicilar kontrol ediliyor (ilk acilista biraz surebilir)...
python manage.py migrate --noinput >nul 2>&1
python manage.py seed_provinces >nul 2>&1
python manage.py seed_users
echo.
echo Sunucu baslatiliyor... Tarayici aciliyor.
echo Giris:  demo  /  Demo.2026!
start "" http://127.0.0.1:8000/login/
python manage.py runserver
pause
