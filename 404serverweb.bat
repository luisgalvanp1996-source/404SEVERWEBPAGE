@echo off

echo Iniciando Flask...
start "WebApp" "C:\Users\Administrador\AppData\Local\Programs\Python\Python314\python.exe" -u "C:\Python\404SEVERWEBPAGE\app.py"

echo Esperando 5 segundos para que Flask levante...
timeout /t 5 /nobreak > nul

echo Iniciando Telegram Bot...
start "TelegramBot" "C:\Users\Administrador\AppData\Local\Programs\Python\Python314\python.exe" -u "C:\Python\404SEVERWEBPAGE\bot.py"

echo Esperando 5 segundos para iniciar Minecraft...
timeout /t 5 /nobreak > nul

echo Iniciando servidor Minecraft...
start "MinecraftServer" "C:\Users\Administrador\AppData\Local\Programs\Python\Python314\python.exe" "F:\Minecraft\Server\start.py"

exit
