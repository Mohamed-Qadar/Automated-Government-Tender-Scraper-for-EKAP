@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
if not exist ".venv\Scripts\activate.bat" (
  echo Once kurulum.bat dosyasini calistirin.
  pause & exit /b
)
call .venv\Scripts\activate
echo ============================================
echo   EKAP'tan GERCEK ihale verisi cekiliyor
echo ============================================
echo.
echo EKAP'tan en yeni ilanlar cekiliyor...
python manage.py sync_ekap_tenders --all-turkiye --limit 100
echo.
echo Birkac ile ozel cekim (Elazig, Istanbul, Ankara, Izmir)...
python manage.py sync_ekap_tenders --province "Elazığ"  --limit 50
python manage.py sync_ekap_tenders --province "İstanbul" --limit 50
python manage.py sync_ekap_tenders --province "Ankara"   --limit 50
python manage.py sync_ekap_tenders --province "İzmir"    --limit 50
echo.
echo Tamamlandi. Siteyi yenileyin: http://127.0.0.1:8000/tenders/
pause
