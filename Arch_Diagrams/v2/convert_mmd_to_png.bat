@echo off
REM Batch script to convert Mermaid diagrams (.mmd) to PNG
REM Usage: convert_mmd_to_png.bat [width] [file1.mmd file2.mmd ...]
REM Example: convert_mmd_to_png.bat 4096 screeningflow.mmd AlertsFlow.mmd
REM Or: convert_mmd_to_png.bat 4096 *.mmd

setlocal enabledelayedexpansion

REM Default width if not specified
set WIDTH=4096
set INPUT_DIR=Arch_Diagrams\v2
set OUTPUT_DIR=Arch_Diagrams\diagrams\v2

REM Check if first argument is a number (width parameter)
set "FIRST_ARG=%~1"
if defined FIRST_ARG (
    echo %FIRST_ARG%| findstr /r "^[0-9][0-9]*$" >nul
    if !errorlevel! equ 0 (
        set WIDTH=%FIRST_ARG%
        shift
    )
)

echo Using width: %WIDTH%
echo Output directory: %OUTPUT_DIR%
echo.

REM Create output directory if it doesn't exist
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

REM If no files specified, process all .mmd files in current directory
if "%~1"=="" (
    echo Processing all .mmd files in current directory...
    for %%f in (*.mmd) do (
        echo Converting: %%f
        cmd /c npx -y @mermaid-js/mermaid-cli -i "%INPUT_DIR%\%%f" -o "%OUTPUT_DIR%\%%~nf.png" -w %WIDTH%
        if !errorlevel! equ 0 (
            echo ✓ Successfully converted: %%f
        ) else (
            echo ✗ Failed to convert: %%f
        )
        echo.
    )
) else (
    REM Process specified files
    :process_files
    if "%~1"=="" goto end
    
    set "FILE=%~1"
    echo Converting: !FILE!
    
    REM Extract filename without path
    for %%A in ("!FILE!") do set "FILENAME=%%~nxA"
    for %%A in ("!FILE!") do set "BASENAME=%%~nA"
    
    cmd /c npx -y @mermaid-js/mermaid-cli -i "%INPUT_DIR%\!FILENAME!" -o "%OUTPUT_DIR%\!BASENAME!.png" -w %WIDTH%
    if !errorlevel! equ 0 (
        echo ✓ Successfully converted: !FILENAME!
    ) else (
        echo ✗ Failed to convert: !FILENAME!
    )
    echo.
    
    shift
    goto process_files
)

:end
echo.
echo Conversion complete!
pause
