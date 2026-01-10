@echo off
setlocal EnableExtensions DisableDelayedExpansion

:: --------------------------------------------------------------------------
:: CONFIGURATION
:: --------------------------------------------------------------------------
set "WINDOW_TITLE=Valesco v1.9.1 Operations Console [LEGACY]"
set "ROOT="
for %%I in ("%~dp0", "%~dp0..", "%~dp0..\..", "%~dp0..\..\..", "%~dp0..\..\..\..") do (
    if not defined ROOT if exist "%%~fI\engine\python_runtime\python.exe" set "ROOT=%%~fI\"
)
if not defined ROOT set "ROOT=%~dp0"
set "BIN=%ROOT%bin\"
set "LOCK_FILE=%TEMP%\valesco_v1.9.lock"

:: PYTHON DISCOVERY (Engine Link)
set "PYTHON_LOCAL=%ROOT%engine\python_runtime\python.exe"

if exist "%PYTHON_LOCAL%" (
    :: Use Portable Runtime
    set "PYTHON_CMD=%PYTHON_LOCAL%"
) else (
    :: Fallback to System Python
    set "PYTHON_CMD=python"
)

:: --------------------------------------------------------------------------
:: SINGLETON CHECK (LOGIC FIX: GOTO METHOD)
:: --------------------------------------------------------------------------
if exist "%LOCK_FILE%" goto LOCK_DETECTED
goto START_SYSTEM

:LOCK_DETECTED
cls
echo.
echo  ==========================================================================
echo   [!] SYSTEM ALERT: ACTIVE LOCK DETECTED
echo  ==========================================================================
echo.
echo   A lock file was found (%LOCK_FILE%).
echo   This usually means:
echo   1. Another console is currently open.
echo   2. A previous session closed unexpectedly.
echo.
echo   [1] ABORT       (I have another window open)
echo   [2] FORCE START (Clear lock and start fresh)
echo.
set /p lock_action="  [?] SELECT ACTION > "

if "%lock_action%"=="1" exit
if "%lock_action%"=="2" (
    del "%LOCK_FILE%" >nul 2>&1
    goto START_SYSTEM
)
:: If invalid input, exit safe
exit

:START_SYSTEM
:: Create Lock to claim this session
echo Valesco Active > "%LOCK_FILE%"
title %WINDOW_TITLE%
cd /d "%ROOT%"

:MENU
cls
echo.
echo  ==========================================================================
echo   VALESCO ESTIMATING SYSTEM — LEGACY OPS (v1.9.1)
echo  ==========================================================================
echo   System Authority Version: v3.5
echo   Legacy console: non-authoritative + non-governing
echo   System Status:       ONLINE
echo  ==========================================================================
echo.
echo   [1] INSTALL OR UPDATE DEPENDENCIES   (Python Requirements)
echo   [2] VALIDATE SYSTEM INTEGRITY        (Schema + Logic Check)
echo   [3] BACKUP SYSTEM                    (Create Backup Archive)
echo   [4] EXIT CONSOLE
echo.
echo  ==========================================================================
set /p choice="  [?] SELECT MODULE > "

if "%choice%"=="1" goto OP1
if "%choice%"=="2" goto OP2
if "%choice%"=="3" goto OP3
if "%choice%"=="4" goto EXIT_CLEAN
goto MENU

:OP1
call "%BIN%install_deps.bat"
pause
goto MENU

:OP2
call "%BIN%validate.bat"
pause
goto MENU

:OP3
call "%BIN%backup_filesystem_state.bat"
pause
goto MENU

:EXIT_CLEAN
:: Remove the lock file so the next session can start cleanly
if exist "%LOCK_FILE%" del "%LOCK_FILE%" >nul 2>&1
exit
