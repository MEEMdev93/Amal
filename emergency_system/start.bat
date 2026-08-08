@echo off
chcp 65001 >nul 2>nul
title نظام جاهزية الأقسام الحيوية اليومية
color 1F

:: الانتقال إلى مجلد الملف تلقائياً (مهم جداً)
cd /d "%~dp0"

echo.
echo =======================================================
echo    نظام قياس جاهزية الاقسام الحيوية اليومية
echo    مستشفى الولادة والاطفال - المدينة المنورة
echo =======================================================
echo.

:: التحقق من Python
python --version >nul 2>nul
if %errorlevel% neq 0 (
    py --version >nul 2>nul
    if %errorlevel% neq 0 (
        echo [خطا] Python غير مثبت.
        echo يرجى تثبيت Python 3.10 او احدث من: https://python.org
        echo تاكد من تفعيل خيار "Add to PATH" عند التثبيت
        pause
        exit /b 1
    )
    set PYTHON=py
) else (
    set PYTHON=python
)

echo [OK] Python موجود

:: إنشاء المجلدات اللازمة (بشكل متسلسل لتجنب الأخطاء)
if not exist "data"              mkdir "data"
if not exist "static"            mkdir "static"
if not exist "static\logos"      mkdir "static\logos"
if not exist "static\backups"    mkdir "static\backups"
if not exist "static\js"         mkdir "static\js"
if not exist "static\css"        mkdir "static\css"
if not exist "static\fonts"      mkdir "static\fonts"
echo [OK] المجلدات جاهزة

:: تثبيت المكتبات (عند أول تشغيل أو إذا كانت ناقصة)
%PYTHON% -c "import fastapi" >nul 2>nul
if %errorlevel% neq 0 (
    echo [معلومة] جاري تثبيت المكتبات - قد يستغرق بضع دقائق...
    %PYTHON% -m pip install --upgrade pip --quiet
    %PYTHON% -m pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo [خطا] فشل تثبيت المكتبات. تحقق من اتصال الانترنت.
        pause
        exit /b 1
    )
    echo [OK] تم تثبيت المكتبات بنجاح
)

:: تنزيل Chart.js (مرة واحدة فقط)
if not exist "static\js\chart.min.js" (
    echo [معلومة] جاري تنزيل Chart.js...
    %PYTHON% -c "import urllib.request; urllib.request.urlretrieve('https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js', 'static/js/chart.min.js'); print('[OK] تم تنزيل Chart.js')" 2>nul
    if not exist "static\js\chart.min.js" (
        echo [تحذير] لم يتم تنزيل Chart.js - الرسوم البيانية لن تعمل
        echo. > "static\js\chart.min.js"
    )
)

:: فتح المتصفح بعد 3 ثواني
echo [معلومة] جاري تشغيل الخادم على: http://127.0.0.1:8000
echo.
echo للايقاف: اضغط Ctrl+C
echo.

start "" /B cmd /c "ping 127.0.0.1 -n 4 >nul && start http://127.0.0.1:8000"

:: تشغيل الخادم
%PYTHON% -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload

pause
