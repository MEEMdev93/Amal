@echo off
chcp 65001 >/dev/null
title نظام جاهزية الأقسام الحيوية اليومية
color 1F

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║   نظام قياس جاهزية الأقسام الحيوية اليومية          ║
echo ║   مستشفى الولادة والأطفال - المدينة المنورة          ║
echo ╚══════════════════════════════════════════════════════╝
echo.

:: التحقق من Python
python --version >/dev/null 2>&1
if %errorlevel% neq 0 (
    echo [خطأ] Python غير مثبت. يرجى تثبيت Python 3.10 أو أحدث من python.org
    pause
    exit /b 1
)

:: إنشاء المجلدات اللازمة
if not exist "data" mkdir data
if not exist "static\logos" mkdir static\logos
if not exist "static\backups" mkdir static\backups
if not exist "static\js" mkdir static\js

:: تثبيت المكتبات عند أول تشغيل
if not exist "static\js\chart.min.js" (
    echo [معلومة] جاري التثبيت الأولي...
    python -m pip install --upgrade pip -q
    python -m pip install -r requirements.txt -q
    if %errorlevel% neq 0 (
        echo [خطأ] فشل تثبيت المكتبات. تحقق من اتصال الإنترنت.
        pause
        exit /b 1
    )
    :: تنزيل Chart.js
    echo [معلومة] جاري تنزيل Chart.js...
    python -c "import urllib.request; urllib.request.urlretrieve('https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js', 'static/js/chart.min.js'); print('[نجاح] تم تنزيل Chart.js')" 2>/dev/null
    if not exist "static\js\chart.min.js" (
        echo [تحذير] لم يتم تنزيل Chart.js - الرسوم البيانية لن تعمل بدون إنترنت
        echo. > static\js\chart.min.js
    )
    echo [نجاح] تم الانتهاء من التثبيت
)

:: فتح المتصفح بعد ثانيتين
echo [معلومة] جاري تشغيل الخادم...
start "" /B timeout /t 2 /nobreak >/dev/null
start "" "http://127.0.0.1:8000"

:: تشغيل الخادم
python app.py

pause
