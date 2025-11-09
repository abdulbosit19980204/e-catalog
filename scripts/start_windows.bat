@echo off
setlocal enabledelayedexpansion

cd /d %~dp0\..

if "%DJANGO_SETTINGS_MODULE%"=="" set DJANGO_SETTINGS_MODULE=config.settings
if "%DEBUG%"=="" set DEBUG=False
if "%ALLOWED_HOSTS%"=="" set ALLOWED_HOSTS=178.218.200.120,localhost,127.0.0.1
if "%CORS_ALLOWED_ORIGINS%"=="" set CORS_ALLOWED_ORIGINS=http://178.218.200.120:1596,http://localhost:3000
if "%CSRF_TRUSTED_ORIGINS%"=="" set CSRF_TRUSTED_ORIGINS=http://178.218.200.120:1596,http://localhost:3000
if "%PORT%"=="" set PORT=1596

python manage.py migrate --noinput || goto :error
python manage.py collectstatic --noinput || goto :error

echo Starting Django development server on port %PORT%
python manage.py runserver 0.0.0.0:%PORT%
exit /b %errorlevel%

:error
echo Start script failed with error code %errorlevel%
exit /b %errorlevel%
