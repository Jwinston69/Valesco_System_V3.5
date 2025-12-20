@echo off
setlocal EnableExtensions DisableDelayedExpansion
cls
echo.
echo  ==========================================================================
echo   VALESCO DEPENDENCY MANAGER                                 [v1.9.1]
echo  ==========================================================================
echo   ACTION: PORTABLE RUNTIME BOOTSTRAP
echo  ==========================================================================
echo.

:: 1. RESOLVE ABSOLUTE PATHS
pushd "%~dp0.."
set "REAL_ROOT=%CD%"
popd

set "PY_DIR=%REAL_ROOT%\engine\python_runtime"
set "PY_EXE=%PY_DIR%\python.exe"
set "PY_URL=https://www.python.org/ftp/python/3.11.6/python-3.11.6-embed-amd64.zip"
set "GET_PIP_URL=https://bootstrap.pypa.io/get-pip.py"
set "BOOTSTRAP_LOG=%REAL_ROOT%\install_deps_bootstrap.log"

echo.>>"%BOOTSTRAP_LOG%"
echo [%date% %time%] install_deps.bat start>>"%BOOTSTRAP_LOG%"
echo [%date% %time%] REAL_ROOT=%REAL_ROOT%>>"%BOOTSTRAP_LOG%"
echo [%date% %time%] PY_DIR=%PY_DIR%>>"%BOOTSTRAP_LOG%"

:: 2. CHECK EXISTING RUNTIME
if exist "%PY_EXE%" (
    echo  [+] Portable Runtime found at:
    echo      engine\python_runtime\
    echo [%date% %time%] INFO portable runtime already present>>"%BOOTSTRAP_LOG%"
    goto CONFIGURE_ENV
)

:: 3. COLD BOOT (Download & Extract)
echo  [!] Runtime missing. Initiating Cold Boot...
echo  ----------------------------------------------------------
echo [%date% %time%] INFO cold boot start>>"%BOOTSTRAP_LOG%"

if exist "%PY_DIR%" rd /s /q "%PY_DIR%"
mkdir "%PY_DIR%"

echo  [*] [1/3] Downloading Python 3.11 (Portable)...
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PY_URL%' -OutFile '%PY_DIR%\python.zip'" >>"%BOOTSTRAP_LOG%" 2>&1
if errorlevel 1 goto FAIL_DOWNLOAD_PYTHON
if not exist "%PY_DIR%\python.zip" goto FAIL_MISSING_PYTHON_ZIP

echo  [*] [2/3] Extracting Runtime...
powershell -Command "Expand-Archive -Path '%PY_DIR%\python.zip' -DestinationPath '%PY_DIR%' -Force" >>"%BOOTSTRAP_LOG%" 2>&1
if errorlevel 1 goto FAIL_EXTRACT_PYTHON

del "%PY_DIR%\python.zip" >nul 2>&1
if not exist "%PY_EXE%" goto FAIL_MISSING_PYTHON_EXE

:CONFIGURE_ENV
:: 4. CONFIGURATION (Enable PIP)
set "PTH_FILE=%PY_DIR%\python311._pth"
if exist "%PTH_FILE%" (
    :: Enable 'import site' so pip can function. Write deterministically (ASCII, no BOM).
    powershell -Command "(Get-Content -Raw '%PTH_FILE%') -replace '#import site', 'import site' | Set-Content -Encoding Ascii '%PTH_FILE%'" >>"%BOOTSTRAP_LOG%" 2>&1
    if errorlevel 1 goto FAIL_PTH_EDIT
) else (
    echo [%date% %time%] WARN missing python311._pth; continuing>>"%BOOTSTRAP_LOG%"
)

:: 5. INSTALL PIP & LIBS
if exist "%PY_DIR%\Scripts\pip.exe" goto INSTALL_LIBS

echo  [*] [3/3] Installing PIP...
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%GET_PIP_URL%' -OutFile '%PY_DIR%\get-pip.py'" >>"%BOOTSTRAP_LOG%" 2>&1
if errorlevel 1 goto FAIL_DOWNLOAD_GETPIP
if not exist "%PY_DIR%\get-pip.py" goto FAIL_MISSING_GETPIP

"%PY_EXE%" "%PY_DIR%\get-pip.py" --no-warn-script-location >>"%BOOTSTRAP_LOG%" 2>&1
if errorlevel 1 goto FAIL_RUN_GETPIP

del "%PY_DIR%\get-pip.py" >nul 2>&1
if not exist "%PY_DIR%\Scripts\pip.exe" goto FAIL_MISSING_PIP

:INSTALL_LIBS
echo.
echo  [*] Installing/Updating Valesco Core...
echo      (pandas, openpyxl, pyyaml, jsonschema)
echo.

"%PY_EXE%" -m pip install --upgrade pandas openpyxl pyyaml jsonschema >>"%BOOTSTRAP_LOG%" 2>&1
if errorlevel 1 goto FAIL_PIP_INSTALL

echo [%date% %time%] OK environment ready>>"%BOOTSTRAP_LOG%"

echo.
echo  ==========================================================================
echo   [SUCCESS] ENVIRONMENT READY
echo  ==========================================================================
echo   Location: engine\python_runtime\
echo.
if not defined VALESCO_NO_PAUSE pause
exit /b 0

:FAIL_DOWNLOAD_PYTHON
echo.
echo  [!] FATAL: Download command failed.
echo [%date% %time%] FAIL download python.zip>>"%BOOTSTRAP_LOG%"
if not defined VALESCO_NO_PAUSE pause
exit /b 1

:FAIL_MISSING_PYTHON_ZIP
echo.
echo  [!] FATAL: Download failed. Check internet connection.
echo [%date% %time%] FAIL missing python.zip after download>>"%BOOTSTRAP_LOG%"
if not defined VALESCO_NO_PAUSE pause
exit /b 1

:FAIL_EXTRACT_PYTHON
echo.
echo  [!] FATAL: Extract failed.
echo [%date% %time%] FAIL extract python.zip>>"%BOOTSTRAP_LOG%"
if not defined VALESCO_NO_PAUSE pause
exit /b 1

:FAIL_MISSING_PYTHON_EXE
echo.
echo  [!] FATAL: Portable python.exe missing after extract.
echo [%date% %time%] FAIL missing python.exe after extract>>"%BOOTSTRAP_LOG%"
if not defined VALESCO_NO_PAUSE pause
exit /b 1

:FAIL_PTH_EDIT
echo.
echo  [!] FATAL: Failed to update python311._pth.
echo [%date% %time%] FAIL update python311._pth>>"%BOOTSTRAP_LOG%"
if not defined VALESCO_NO_PAUSE pause
exit /b 1

:FAIL_DOWNLOAD_GETPIP
echo.
echo  [!] FATAL: get-pip download failed.
echo [%date% %time%] FAIL download get-pip.py>>"%BOOTSTRAP_LOG%"
if not defined VALESCO_NO_PAUSE pause
exit /b 1

:FAIL_MISSING_GETPIP
echo.
echo  [!] FATAL: get-pip.py missing after download.
echo [%date% %time%] FAIL missing get-pip.py after download>>"%BOOTSTRAP_LOG%"
if not defined VALESCO_NO_PAUSE pause
exit /b 1

:FAIL_RUN_GETPIP
echo.
echo  [!] FATAL: get-pip execution failed.
echo [%date% %time%] FAIL run get-pip.py>>"%BOOTSTRAP_LOG%"
if not defined VALESCO_NO_PAUSE pause
exit /b 1

:FAIL_MISSING_PIP
echo.
echo  [!] FATAL: pip.exe missing after get-pip.
echo [%date% %time%] FAIL missing pip.exe after get-pip>>"%BOOTSTRAP_LOG%"
if not defined VALESCO_NO_PAUSE pause
exit /b 1

:FAIL_PIP_INSTALL
echo.
echo  [!] ERROR: Library installation failed.
echo [%date% %time%] FAIL pip install>>"%BOOTSTRAP_LOG%"
if not defined VALESCO_NO_PAUSE pause
exit /b 1
