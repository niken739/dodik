@echo off
REM run_all.bat - Start backend and frontend in separate CMD windows
REM Usage: double-click or run from project root. Requires Python and Node/npm in PATH.

pushd %~dp0

REM Check if virtual environment exists, if not create it and install dependencies
if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
    echo Installing Python dependencies...
    call .venv\Scripts\pip.exe install -r backend\requirements.txt
)

REM Start backend in a new window (keeps window open on exit)
start "OK Backend" cmd /k "cd /d %~dp0 && .venv\Scripts\python.exe -u backend\run.py"

REM Start frontend in a new window (keeps window open on exit)
start "OK Frontend" cmd /k "cd /d "%~dp0frontend" & npm run dev"

popd
exit /b 0
