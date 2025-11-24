@echo off
setlocal

REM ==========================
REM CONFIGURACIÓN
REM ==========================
set "APP_DIR=C:\Python\404SEVERWEBPAGE"
set "APP_FILE=app.py"
set "PYTHON_EXE=C:\Users\Administrador\AppData\Local\Programs\Python\Python314\python.exe"
set "LOG=%APP_DIR%\server_log.txt"
set "SQL_SERVICE=MSSQL$SERVERHOME"

echo. >> "%LOG%"
echo ============================================================ >> "%LOG%"
echo [%date% %time%] Inicio del script >> "%LOG%"

REM ==========================
REM VERIFICAR SQL SERVER
REM ==========================
echo [%date% %time%] Verificando servicio SQL Server... >> "%LOG%"
sc query "%SQL_SERVICE%" | find "RUNNING" >nul

if %errorlevel% neq 0 (
    echo [%date% %time%] SQL Server no está iniciado. Iniciando... >> "%LOG%"
    net start "%SQL_SERVICE%" >> "%LOG%" 2>&1
    if %errorlevel% neq 0 (
        echo [%date% %time%] ERROR: No se pudo iniciar SQL Server >> "%LOG%"
        echo No se pudo iniciar SQL Server. Revisa server_log.txt
        pause
        exit /b 1
    )
    echo [%date% %time%] SQL Server iniciado correctamente. >> "%LOG%"
) else (
    echo [%date% %time%] SQL Server ya estaba en ejecución. >> "%LOG%"
)

REM ==========================
REM INICIAR APLICACIÓN
REM ==========================
cd /d "%APP_DIR%"
echo [%date% %time%] Iniciando aplicación... >> "%LOG%"

"%PYTHON_EXE%" "%APP_DIR%\%APP_FILE%" --host=0.0.0.0 --port=5001 >> "%LOG%" 2>&1

echo [%date% %time%] La aplicación terminó su ejecución. >> "%LOG%"
echo La aplicación finalizó. Revisa el log: %LOG%
pause
endlocal
