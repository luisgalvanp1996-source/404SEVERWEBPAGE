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

echo Esperando 5 segundos para iniciar Minecraft...
timeout /t 5 /nobreak > nul


REM === MINECRAFT SERVER ===
echo Iniciando servidor Minecraft...
tasklist | findstr /i "start.py" > nul
if %errorlevel%==0 (
    echo [Servidor Minecraft ya se esta ejecutando]
) else (
    start "MinecraftServer" "C:\Users\Administrador\AppData\Local\Programs\Python\Python314\python.exe" "F:\Minecraft\Server\start.py"
)

exit
