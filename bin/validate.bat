@echo off
setlocal
cls
echo.
echo  ==========================================================================
echo   VALESCO VALIDATOR (OPS TOOL)                               [v3.5]
echo  ==========================================================================
echo   System Authority Version: v3.5
echo   Scope: Legacy integrity check (Schema + Logic) — non-governing
echo  ==========================================================================
echo.

:: 1. RESOLVE PATHS
pushd "%~dp0.."
set "REAL_ROOT=%CD%"
popd

:: 2. DETECT ENGINE
set "PYTHON_EXE=%REAL_ROOT%\engine\python_runtime\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

set "SCRIPT=%REAL_ROOT%\engine\scripts\validate.py"

:: 3. EXECUTE
if not exist "%SCRIPT%" (
    echo [!] FATAL: Script missing: %SCRIPT%
    pause
    exit /b 1
)

echo  [*] Engine: %PYTHON_EXE%
echo  [*] Initiating Validation Sequence...
echo  --------------------------------------------------------------------------

"%PYTHON_EXE%" "%SCRIPT%"

if %errorlevel% neq 0 (
    echo.
    echo  --------------------------------------------------------------------------
    echo  [!] VALIDATION FAILED. Review errors above.
    exit /b 1
) else (
    echo.
    echo  --------------------------------------------------------------------------
    echo  [+] SYSTEM HEALTHY.
)
exit /b 0