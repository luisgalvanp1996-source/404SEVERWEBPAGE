@echo off
setlocal enabledelayedexpansion

:: Ruta donde está el BAT
set "BASE_DIR=%~dp0"

:: Carpeta DATA\logs
set "LOG_DIR=%BASE_DIR%DATA\logs"
set "LOG=%LOG_DIR%\server.log"

:: Crear carpeta DATA\logs si no existe
if not exist "%LOG_DIR%" (
    mkdir "%LOG_DIR%"
)

:: Nombre del servicio SQL Server
set "SQLSERVICE=MSSQL$SERVERHOME"

echo ================================================= >> "%LOG%"
echo Inicio: %date% %time% >> "%LOG%"
echo ================================================= >> "%LOG%"
echo Verificando estado del servicio %SQLSERVICE%... >> "%LOG%"

:: Revisar estado del servicio SQL
sc query "%SQLSERVICE%" | find "RUNNING" >nul

if %errorlevel%==0 (
    echo SQL Server ya está en ejecución. >> "%LOG%"
) else (
    echo SQL Server NO está en ejecución. Intentando iniciar... >> "%LOG%"
    net start "%SQLSERVICE%" >> "%LOG%" 2>&1
    if %errorlevel%==0 (
        echo SQL Server iniciado correctamente. >> "%LOG%"
    ) else (
        echo ERROR: No se pudo iniciar SQL Server. >> "%LOG%"
        echo Revisar permisos o configuración. >> "%LOG%"
    )
)

echo Obteniendo IP pública... >> "%LOG%"

:: Obtener IP pública con curl (sin PowerShell)
for /f "delims=" %%i in ('curl -s https://api.ipify.org') do set "PUBLIC_IP=%%i"

if defined PUBLIC_IP (
    echo IP Pública: %PUBLIC_IP% >> "%LOG%"
) else (
    echo ERROR: No se pudo obtener la IP pública. >> "%LOG%"
)

echo Iniciando servidor Python... >> "%LOG%"

"C:\Users\Administrador\AppData\Local\Programs\Python\Python314\python.exe" ^
"%BASE_DIR%app.py" --host=0.0.0.0 --port=5001 >> "%LOG%" 2>&1

echo Servidor finalizado: %date% %time% >> "%LOG%"
pause
endlocal
