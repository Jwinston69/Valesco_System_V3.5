@echo off
setlocal EnableExtensions DisableDelayedExpansion
cls

echo.
echo  ======================================================================
echo   VALESCO RUNTIME ENTRY (v3.5)
echo  ======================================================================
echo   System Authority Version: v3.5
echo.

:: Resolve root
pushd "%~dp0.."
set "REAL_ROOT=%CD%"
popd

:: Prefer portable Python
set "PYTHON_EXE=%REAL_ROOT%\engine\python_runtime\python.exe"
if exist "%PYTHON_EXE%" (
    echo  [INFO] Using bundled portable Python.
) else (
    set "PYTHON_EXE=python"
    echo  [WARN] Portable Python not found. Falling back to system Python.
)

set "SCRIPT=%REAL_ROOT%\run_valesco.py"

if not exist "%SCRIPT%" (
    echo [FATAL] Script missing: %SCRIPT%
    pause
    exit /b 1
)

echo.
"%PYTHON_EXE%" "%SCRIPT%"
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo  [!] Runtime failed with exit code %EXIT_CODE%.
    if not defined VALESCO_NO_PAUSE pause
    exit /b %EXIT_CODE%
)

if not defined VALESCO_NO_PAUSE pause
exit /b 0
