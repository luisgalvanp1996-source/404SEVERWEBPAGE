@echo off

REM === FLASK ===
echo Iniciando Flask...
tasklist | findstr /i "app.py" > nul
if %errorlevel%==0 (
    echo [Flask ya se esta ejecutando]
) else (
    start "WebApp" "C:\Users\Administrador\AppData\Local\Programs\Python\Python314\python.exe" -u "C:\Python\404SEVERWEBPAGE\app.py"
)

echo Esperando 5 segundos para que Flask levante...
timeout /t 5 /nobreak > nul


REM === TELEGRAM BOT ===
echo Iniciando Telegram Bot...
tasklist | findstr /i "bot.py" > nul
if %errorlevel%==0 (
    echo [Telegram Bot ya se esta ejecutando]
) else (
    start "TelegramBot" "C:\Users\Administrador\AppData\Local\Programs\Python\Python314\python.exe" -u "C:\Python\404SEVERWEBPAGE\bot.py"
)


exit
