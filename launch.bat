@echo off

:: Ruta donde está el BAT
set "BASE_DIR=%~dp0"

:: Carpeta DATA\logs junto al BAT
set "LOG_DIR=%BASE_DIR%DATA\logs"
set "LOG=%LOG_DIR%\server.log"

:: Crear carpeta DATA\logs si no existe
if not exist "%LOG_DIR%" (
    mkdir "%LOG_DIR%"
)

echo =============================== >> "%LOG%"
echo Inicio: %date% %time% >> "%LOG%"
echo =============================== >> "%LOG%"

"C:\Users\Administrador\AppData\Local\Programs\Python\Python314\python.exe" ^
 "%BASE_DIR%app.py" --host=0.0.0.0 --port=5001 >> "%LOG%" 2>&1

echo Servidor finalizado: %date% %time% >> "%LOG%"
pause
