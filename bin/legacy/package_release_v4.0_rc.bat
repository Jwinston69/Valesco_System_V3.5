:: cd C:\Valesco_System_V3.5 && bin\package_release_v4.0_rc.bat C:\VALESCO_RELEASE_TEST

@echo off
setlocal EnableExtensions DisableDelayedExpansion
cls

echo.
echo  ======================================================================
echo   VALESCO RELEASE PACKAGER (v4.0-RC)
echo  ======================================================================
echo   PURPOSE: Build a deterministic, deployable system bundle
echo   WARNING: Target directory will be deleted if it exists
echo  ======================================================================
echo.

:: ----------------------------------------------------------------------
:: Resolve system root (script lives in /bin)
:: ----------------------------------------------------------------------
pushd "%~dp0.."
set "REAL_ROOT=%CD%"
popd

:: ----------------------------------------------------------------------
:: Validate arguments
:: ----------------------------------------------------------------------
if "%~1"=="" (
    echo  [FATAL] No output directory specified.
    echo.
    echo  USAGE:
    echo    package_release_v4.0_rc.bat ^<output_directory^>
    echo.
    echo  EXAMPLE:
    echo    package_release_v4.0_rc.bat C:\Valesco_Releases\v4.0-rc
    echo.
    if not defined VALESCO_NO_PAUSE pause
    exit /b 1
)

set "OUTPUT_DIR=%~f1"

:: ----------------------------------------------------------------------
:: Resolve Python (prefer portable)
:: ----------------------------------------------------------------------
set "PYTHON_EXE=%REAL_ROOT%\engine\python_runtime\python.exe"
if exist "%PYTHON_EXE%" (
    echo  [INFO] Using bundled portable Python.
) else (
    set "PYTHON_EXE=python"
    echo  [WARN] Portable Python not found. Falling back to system Python.
)

:: ----------------------------------------------------------------------
:: Resolve script
:: ----------------------------------------------------------------------
set "SCRIPT=%REAL_ROOT%\engine\build\system_packaging_v4.0_rc.py"

if not exist "%SCRIPT%" (
    echo  [FATAL] Packaging script not found:
    echo          %SCRIPT%
    if not defined VALESCO_NO_PAUSE pause
    exit /b 1
)

:: ----------------------------------------------------------------------
:: Final confirmation (human intent check)
:: ----------------------------------------------------------------------
echo.
echo  Target output directory:
echo    %OUTPUT_DIR%
echo.
echo  This directory will be ERASED if it already exists.
echo.
set /p CONFIRM="Type YES to continue > "

if /I not "%CONFIRM%"=="YES" (
    echo.
    echo  Aborted by user.
    exit /b 2
)

:: ----------------------------------------------------------------------
:: Execute packaging
:: ----------------------------------------------------------------------
echo.
echo  [*] Starting release packaging...
echo.

"%PYTHON_EXE%" "%SCRIPT%" "%OUTPUT_DIR%"
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo  [!] Packaging failed ^(exit code %EXIT_CODE%^).
    if not defined VALESCO_NO_PAUSE pause
    exit /b %EXIT_CODE%
)

echo.
echo  ======================================================================
echo   [SUCCESS] RELEASE PACKAGE COMPLETE
echo  ======================================================================
echo   Output: %OUTPUT_DIR%
echo.
if not defined VALESCO_NO_PAUSE pause
exit /b 0
