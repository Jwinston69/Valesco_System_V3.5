@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ============================================================================
REM  VALESCO v3.5 - BUILD AGENT ORIENTATION PACK
REM  Purpose:
REM    Create a curated, layered handover pack for a new development agent.
REM    Governance is binding. Vision documents are reference-only.
REM    No system state is modified. No code is executed.
REM ============================================================================

REM Resolve system root (script assumed to live in \bin\)
set "BIN_DIR=%~dp0"
for %%I in ("%BIN_DIR%\..") do set "SYSROOT=%%~fI"

REM Timestamp (filesystem-safe)
for /f "tokens=1-3 delims=/" %%a in ("%date%") do set "D=%%c-%%b-%%a"
for /f "tokens=1-2 delims=:" %%a in ("%time%") do set "T=%%a%%b"
set "T=%T: =0%"

set "OUT=%SYSROOT%\AGENT_ORIENTATION_PACK_%D%_%T%"
set "MANIFEST=%OUT%\PACK_MANIFEST.txt"

mkdir "%OUT%" >nul 2>&1

mkdir "%OUT%\01_GOVERNANCE_BINDING" >nul 2>&1
mkdir "%OUT%\02_EXECUTION_ANCHOR" >nul 2>&1
mkdir "%OUT%\03_VISION_REFERENCE_ONLY" >nul 2>&1
mkdir "%OUT%\04_OPTIONAL_CONTEXT" >nul 2>&1

echo VALESCO v3.5 Agent Orientation Pack > "%MANIFEST%"
echo Built: %date% %time%>> "%MANIFEST%"
echo Source Root: %SYSROOT%>> "%MANIFEST%"
echo.>> "%MANIFEST%"

set "MISSING=0"

REM ============================================================================
REM GOVERNANCE (BINDING)
REM ============================================================================
call :COPY "%SYSROOT%\governance\valesco_bootstrap_v3.5.txt" "%OUT%\01_GOVERNANCE_BINDING\valesco_bootstrap_v3.5.txt"
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
call :COPY "%SYSROOT%\docs\VALESCO_SYSTEM_MANIFEST_v1.9.1.md" "%OUT%\03_VISION_REFERENCE_ONLY\VALESCO_SYSTEM_MANIFEST_v1.9.1.md"
call :COPY "%SYSROOT%\docs\VALESCO_ROADMAP_v2.0_CONTEXT_ENGINEERING_ADDENDUM.md" "%OUT%\03_VISION_REFERENCE_ONLY\VALESCO_ROADMAP_v2.0_CONTEXT_ENGINEERING_ADDENDUM.md"
call :COPY "%SYSROOT%\docs\governance\VALESCO_TRUTH_HIERARCHY.md" "%OUT%\03_VISION_REFERENCE_ONLY\VALESCO_TRUTH_HIERARCHY.md"

REM ============================================================================
REM OPTIONAL CONTEXT (NON-BINDING)
REM ============================================================================
call :COPY "%SYSROOT%\docs\VALESCO_DEPENDENCY_MAP.md" "%OUT%\04_OPTIONAL_CONTEXT\VALESCO_DEPENDENCY_MAP.md"
call :COPY "%SYSROOT%\docs\VALESCO_FULL_SYSTEM_HANDOVER_v2.0.md" "%OUT%\04_OPTIONAL_CONTEXT\VALESCO_FULL_SYSTEM_HANDOVER_v2.0.md"
call :COPY "%SYSROOT%\docs\VALESCO_REGRESSION_SUITE_v1.9.md" "%OUT%\04_OPTIONAL_CONTEXT\VALESCO_REGRESSION_SUITE_v1.9.md"
call :COPY "%SYSROOT%\docs\dev\history\mvp_completion_report_v2.1.md" "%OUT%\04_OPTIONAL_CONTEXT\mvp_completion_report_v2.1.md"

REM ============================================================================
REM README
REM ============================================================================
call :WRITE_README "%OUT%\README_FIRST.txt"

echo.>> "%MANIFEST%"
if "%MISSING%"=="0" (
  echo Pack build completed: NO missing files.>> "%MANIFEST%"
) else (
  echo Pack build completed: MISSING FILES=%MISSING% (see above).>> "%MANIFEST%"
)

echo.
echo Agent Orientation Pack created:
echo   %OUT%
echo.
if not defined VALESCO_NO_PAUSE pause
exit /b 0

REM ============================================================================
REM HELPERS
REM ============================================================================
:COPY
set "SRC=%~1"
set "DST=%~2"
if exist "%SRC%" (
  copy /y "%SRC%" "%DST%" >nul
  echo OK    "%SRC%" ^> "%DST%">> "%MANIFEST%"
) else (
  set /a MISSING+=1
  echo MISS  "%SRC%">> "%MANIFEST%"
)
exit /b 0

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
>>"%R%" echo 1) 01_GOVERNANCE_BINDING\valesco_bootstrap_v3.5.txt
>>"%R%" echo 2) 01_GOVERNANCE_BINDING\valesco_primer_v3.5.txt
>>"%R%" echo 3) 01_GOVERNANCE_BINDING\valesco_snapshot_v3.5.txt
>>"%R%" echo 4) 01_GOVERNANCE_BINDING\valesco_snapshot_template_v3.5.txt
>>"%R%" echo.
>>"%R%" echo EXECUTION GUIDANCE (SCOPED)
>>"%R%" echo - 02_EXECUTION_ANCHOR\CORTEX_DEVELOPMENT_ANCHOR_v1.0.md
>>"%R%" echo   This document defines the current development phase.
>>"%R%" echo   It does not supersede governance or roadmaps.
>>"%R%" echo.
>>"%R%" echo VISION AND INTENT (REFERENCE-ONLY)
>>"%R%" echo - 03_VISION_REFERENCE_ONLY\*
>>"%R%" echo   These documents describe long-term direction and invariants.
>>"%R%" echo   They are not instructions.
>>"%R%" echo.
>>"%R%" echo NOTE ON VERSIONING
>>"%R%" echo - Snapshot v3.5 is current operational state.
>>"%R%" echo - Roadmap v2.0 is a destination label, not a chronology.
exit /b 0
