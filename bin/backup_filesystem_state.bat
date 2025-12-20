@echo off
setlocal
cls
echo.
echo  ==========================================================================
echo   VALESCO SNAPSHOT ENGINE                                    [v1.9.1]
echo  ==========================================================================
echo   ACTION: CLOUD/LOCAL BACKUP
echo  ==========================================================================
echo.

:: 1. RESOLVE ABSOLUTE ROOT
pushd "%~dp0.."
set "REAL_ROOT=%CD%"
popd

:: 2. GENERATE ROBUST TIMESTAMP
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set "TIMESTAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,4%"

:: 3. DETERMINE TARGET (Cloud vs Local)
set "CLOUD_TARGET=G:\My Drive\Valesco System"
set "LOCAL_TARGET=%REAL_ROOT%\_SNAPSHOTS"

if exist "G:\My Drive" (
    :: UPDATE: Changed prefix to v1.9.1
    set "DEST=%CLOUD_TARGET%\v1.9.1_SNAPSHOT_%TIMESTAMP%"
    echo  [+] Google Drive Detected [G:]
    echo  [*] Target: Cloud Archive
) else (
    :: UPDATE: Aligned local prefix for consistency
    set "DEST=%LOCAL_TARGET%\v1.9.1_SNAP_%TIMESTAMP%"
    echo  [!] Cloud Not Found.
    echo  [*] Target: Local Archive [_SNAPSHOTS]
)

echo  [*] Destination: %DEST%
echo.

if not defined VALESCO_NO_PAUSE (
    echo  Press any key to start backup...
    pause >nul
)

:: 4. EXECUTION (Robocopy with Smart Exclusions)
:: Robocopy exit codes: 0-7 = success (incl. files copied); >=8 = failure.

set "FAILED=0"

echo.
echo  [1/5] Backing up Governance...
robocopy "%REAL_ROOT%\docs" "%DEST%\docs" /E /FFT /R:1 /W:1 /NFL /NDL >nul
set "RC=%ERRORLEVEL%"
if %RC% GEQ 8 (
    echo  [!] FAIL: docs backup (robocopy rc=%RC%)
    set "FAILED=1"
)

echo  [2/5] Backing up Engine Logic...
robocopy "%REAL_ROOT%\engine" "%DEST%\engine" /E /FFT /R:1 /W:1 /NFL /NDL /XD "python_runtime" "__pycache__" >nul
set "RC=%ERRORLEVEL%"
if %RC% GEQ 8 (
    echo  [!] FAIL: engine backup (robocopy rc=%RC%)
    set "FAILED=1"
)

echo  [3/5] Backing up Library (Core Data)...
robocopy "%REAL_ROOT%\library" "%DEST%\library" /E /FFT /R:1 /W:1 /NFL /NDL >nul
set "RC=%ERRORLEVEL%"
if %RC% GEQ 8 (
    echo  [!] FAIL: library backup (robocopy rc=%RC%)
    set "FAILED=1"
)

echo  [4/5] Backing up Workspace (User Data)...
robocopy "%REAL_ROOT%\workspace" "%DEST%\workspace" /E /FFT /R:1 /W:1 /NFL /NDL >nul
set "RC=%ERRORLEVEL%"
if %RC% GEQ 8 (
    echo  [!] FAIL: workspace backup (robocopy rc=%RC%)
    set "FAILED=1"
)

echo  [5/5] Backing up Binaries and Root...
robocopy "%REAL_ROOT%\bin" "%DEST%\bin" /E /FFT /R:1 /W:1 /NFL /NDL >nul
set "RC=%ERRORLEVEL%"
if %RC% GEQ 8 (
    echo  [!] FAIL: bin backup (robocopy rc=%RC%)
    set "FAILED=1"
)

:: Optional root files: missing is OK; failed copy when present is fatal.
if exist "%REAL_ROOT%\_START_VALESCO.bat" (
    copy /Y "%REAL_ROOT%\_START_VALESCO.bat" "%DEST%\" >nul
    if %ERRORLEVEL% NEQ 0 (
        echo  [!] FAIL: could not copy _START_VALESCO.bat
        set "FAILED=1"
    )
) else (
    echo  [WARN] Optional root file missing: _START_VALESCO.bat
)

if exist "%REAL_ROOT%\README.md" (
    copy /Y "%REAL_ROOT%\README.md" "%DEST%\" >nul
    if %ERRORLEVEL% NEQ 0 (
        echo  [!] FAIL: could not copy README.md
        set "FAILED=1"
    )
) else (
    echo  [WARN] Optional root file missing: README.md
)

echo.
echo  ==========================================================================
if "%FAILED%"=="0" (
    echo   [SUCCESS] SNAPSHOT COMPLETE
) else (
    echo   [FAIL] SNAPSHOT INCOMPLETE
)
echo  ==========================================================================
echo   Saved to: %DEST%
echo.

if not defined VALESCO_NO_PAUSE pause

if "%FAILED%"=="0" (
    exit /b 0
) else (
    exit /b 1
)
