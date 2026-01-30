@echo off
REM VAJRA Shakti Kavach - Quick Start for Windows

echo.
echo ============================================================
echo   [#] VAJRA Shakti Kavach - Web App Quick Start
echo ============================================================
echo.

REM Get script directory
setlocal enabledelayedexpansion
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [+] Python found - Starting HTTP server on port 8000
    echo.
    echo ============================================================
    echo Server running at: http://localhost:8000
    echo.
    echo Access the app here:
    echo   - App:      http://localhost:8000/app.html
    echo   - Test:     http://localhost:8000/test.html
    echo   - Docs:     http://localhost:8000/APP_USAGE.md
    echo.
    echo Press Ctrl+C to stop the server
    echo ============================================================
    echo.
    python -m http.server 8000
    goto end
)

REM Try py launcher
py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [+] Python launcher found - Starting HTTP server on port 8000
    echo.
    echo ============================================================
    echo Server running at: http://localhost:8000
    echo.
    echo Access the app here:
    echo   - App:      http://localhost:8000/app.html
    echo   - Test:     http://localhost:8000/test.html
    echo   - Docs:     http://localhost:8000/APP_USAGE.md
    echo.
    echo Press Ctrl+C to stop the server
    echo ============================================================
    echo.
    py -m http.server 8000
    goto end
)

REM Try Node.js http-server
http-server --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [+] http-server found - Starting on port 8000
    echo.
    http-server -p 8000 -o app.html
    goto end
)

REM Fallback: Direct browser
echo [-] Python and http-server not found
echo.
echo Trying to open app.html directly in your browser...
echo.
start "" "%SCRIPT_DIR%app.html"

:end
pause
