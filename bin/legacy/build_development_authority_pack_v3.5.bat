@echo off
setlocal EnableExtensions DisableDelayedExpansion

REM ============================================================================
REM  VALESCO v3.5 - BUILD AGENT ORIENTATION PACK
REM  Purpose:
REM    Create a curated, layered handover pack for a new development agent.
REM    Governance files are binding and must be loaded in order.
REM    Vision documents are reference-only and do not grant authority.
REM    No system state is modified. No code is executed.
REM ============================================================================

REM Resolve system root (this script lives in \bin\legacy\)
set "BIN_DIR=%~dp0"
for %%I in ("%BIN_DIR%\..\..") do set "SYSROOT=%%~fI"

REM Locale-agnostic timestamp
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HHmmss"') do set "TS=%%i"

set "OUT=%SYSROOT%\AGENT_ORIENTATION_PACK_%TS%"
set "MANIFEST=%OUT%\PACK_MANIFEST.txt"

mkdir "%OUT%" >nul 2>&1
mkdir "%OUT%\01_GOVERNANCE_BINDING" >nul 2>&1
mkdir "%OUT%\02_EXECUTION_ANCHOR" >nul 2>&1
mkdir "%OUT%\03_VISION_REFERENCE_ONLY" >nul 2>&1
mkdir "%OUT%\04_OPTIONAL_CONTEXT" >nul 2>&1

> "%MANIFEST%" echo VALESCO v3.5 Agent Orientation Pack
>>"%MANIFEST%" echo Built: %date% %time%
>>"%MANIFEST%" echo Source Root: %SYSROOT%
>>"%MANIFEST%" echo.

set "MISSING=0"

REM ============================================================================
REM GOVERNANCE (BINDING)
REM ============================================================================
call :COPY "%SYSROOT%\governance\valesco_bootstrap_v3.5.md" "%OUT%\01_GOVERNANCE_BINDING\valesco_bootstrap_v3.5.md"
call :COPY "%SYSROOT%\governance\valesco_primer_v3.5.txt" "%OUT%\01_GOVERNANCE_BINDING\valesco_primer_v3.5.txt"
call :COPY "%SYSROOT%\governance\valesco_snapshot_v3.5.txt" "%OUT%\01_GOVERNANCE_BINDING\valesco_snapshot_v3.5.txt"
call :COPY "%SYSROOT%\governance\valesco_snapshot_template_v3.5.txt" "%OUT%\01_GOVERNANCE_BINDING\valesco_snapshot_template_v3.5.txt"

REM ============================================================================
REM EXECUTION ANCHOR (SCOPED GUIDANCE)
REM ============================================================================
call :COPY "%SYSROOT%\governance\execution_anchor\CORTEX_DEVELOPMENT_ANCHOR_v1.0.md" "%OUT%\02_EXECUTION_ANCHOR\CORTEX_DEVELOPMENT_ANCHOR_v1.0.md"

REM ============================================================================
REM VISION & INTENT (REFERENCE-ONLY)
REM ============================================================================
call :COPY "%SYSROOT%\docs\VALESCO_ROADMAP_v2.0.md" "%OUT%\03_VISION_REFERENCE_ONLY\VALESCO_ROADMAP_v2.0.md"
call :COPY_FALLBACK "%SYSROOT%\docs\_archive\v1.x\VALESCO_SYSTEM_MANIFEST_v1.9.1.md" "%SYSROOT%\docs\VALESCO_SYSTEM_MANIFEST_v1.9.1.md" "%OUT%\03_VISION_REFERENCE_ONLY\VALESCO_SYSTEM_MANIFEST_v1.9.1.md"
call :COPY "%SYSROOT%\docs\VALESCO_ROADMAP_v2.0_CONTEXT_ENGINEERING_ADDENDUM.md" "%OUT%\03_VISION_REFERENCE_ONLY\VALESCO_ROADMAP_v2.0_CONTEXT_ENGINEERING_ADDENDUM.md"
call :COPY "%SYSROOT%\docs\governance\VALESCO_TRUTH_HIERARCHY.md" "%OUT%\03_VISION_REFERENCE_ONLY\VALESCO_TRUTH_HIERARCHY.md"

REM ============================================================================
REM OPTIONAL CONTEXT (NON-BINDING)
REM ============================================================================
call :COPY_FALLBACK "%SYSROOT%\docs\_archive\v1.x\VALESCO_DEPENDENCY_MAP.md" "%SYSROOT%\docs\VALESCO_DEPENDENCY_MAP.md" "%OUT%\04_OPTIONAL_CONTEXT\VALESCO_DEPENDENCY_MAP.md"
call :COPY_FALLBACK "%SYSROOT%\docs\_archive\v1.x\VALESCO_FULL_SYSTEM_HANDOVER_v2.0.md" "%SYSROOT%\docs\VALESCO_FULL_SYSTEM_HANDOVER_v2.0.md" "%OUT%\04_OPTIONAL_CONTEXT\VALESCO_FULL_SYSTEM_HANDOVER_v2.0.md"
call :COPY_FALLBACK "%SYSROOT%\docs\_archive\v1.x\VALESCO_REGRESSION_SUITE_v1.9.md" "%SYSROOT%\docs\VALESCO_REGRESSION_SUITE_v1.9.md" "%OUT%\04_OPTIONAL_CONTEXT\VALESCO_REGRESSION_SUITE_v1.9.md"
call :COPY_FALLBACK "%SYSROOT%\docs\_archive\v1.x\dev\history\mvp_completion_report_v2.1.md" "%SYSROOT%\docs\dev\history\mvp_completion_report_v2.1.md" "%OUT%\04_OPTIONAL_CONTEXT\mvp_completion_report_v2.1.md"

REM ============================================================================
REM README
REM ============================================================================
call :WRITE_README "%OUT%\README_FIRST.txt"

>>"%MANIFEST%" echo.
if "%MISSING%"=="0" >>"%MANIFEST%" echo Pack build completed: NO missing files.
if not "%MISSING%"=="0" >>"%MANIFEST%" echo Pack build completed: MISSING FILES=%MISSING% (see above).

echo.
echo Agent Orientation Pack created:
echo   %OUT%
echo.
if not defined VALESCO_NO_PAUSE pause
exit /b 0

REM ============================================================================
REM HELPERS (NO PARENTHESIS BLOCKS - AVOID PARSE FAILURES)
REM ============================================================================
:COPY
set "SRC=%~1"
set "DST=%~2"
if not exist "%SRC%" set /a MISSING+=1 & >>"%MANIFEST%" echo MISS  "%SRC%" & goto :eof
copy /y "%SRC%" "%DST%" >nul & >>"%MANIFEST%" echo OK    "%SRC%" ^> "%DST%"
goto :eof

:COPY_FALLBACK
set "SRC_PRIMARY=%~1"
set "SRC_FALLBACK=%~2"
set "DST=%~3"
if exist "%SRC_PRIMARY%" call :COPY "%SRC_PRIMARY%" "%DST%" & goto :eof
call :COPY "%SRC_FALLBACK%" "%DST%"
goto :eof

:WRITE_README
set "R=%~1"
> "%R%" echo VALESCO v3.5 Agent Orientation Pack
>>"%R%" echo.
>>"%R%" echo PURPOSE
>>"%R%" echo - Provide a curated, layered handover for a new development agent.
>>"%R%" echo - Governance files are binding and must be loaded in order.
>>"%R%" echo - Vision documents are reference-only and do not grant authority.
>>"%R%" echo.
>>"%R%" echo LOAD ORDER (MANDATORY)
>>"%R%" echo 1) 01_GOVERNANCE_BINDING\valesco_bootstrap_v3.5.md
>>"%R%" echo 2) 01_GOVERNANCE_BINDING\valesco_primer_v3.5.txt
>>"%R%" echo 3) 01_GOVERNANCE_BINDING\valesco_snapshot_v3.5.txt
>>"%R%" echo 4) 01_GOVERNANCE_BINDING\valesco_snapshot_template_v3.5.txt
>>"%R%" echo.
>>"%R%" echo EXECUTION GUIDANCE (SCOPED)
>>"%R%" echo - 02_EXECUTION_ANCHOR\CORTEX_DEVELOPMENT_ANCHOR_v1.0.md
>>"%R%" echo   This document defines the current development phase.
>>"%R%" echo   It does not supersede governance or roadmaps.
goto :eof
