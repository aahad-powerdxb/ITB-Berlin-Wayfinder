@echo off
REM Ensure we run from the script directory
cd /d "%~dp0"

REM Start the Vite dev server in a new terminal window and keep it open
start "DevServer" cmd /k "npm run dev"

REM Wait for the dev server to become available on ports 3000..3010
set PORT=
for /L %%p in (3000,1,3010) do (
	REM Try a quick request to see if the server responds on this port
	powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:%%p/' -UseBasicParsing -TimeoutSec 2; if ($r.StatusCode -ge 200) { Write-Output(%%p); exit 0 } } catch { } ; exit 1" >nul 2>&1
	if not errorlevel 1 (
		set PORT=%%p
		goto :FOUND_PORT
	)
)

:FOUND_PORT
if "%PORT%"=="" set PORT=3000

REM Open Chrome in kiosk mode to the dev server URL
REM Use a specific/temp user data dir to avoid the profile selection screen
start "" "chrome" "http://localhost:%PORT%/" --new-window --kiosk --disable-pinch --no-first-run --no-default-browser-check --user-data-dir="%TEMP%\chrome_kiosk_data"


REM Try to make the Chrome window topmost so it stays above the terminal windows.
REM Uses a helper PowerShell script located next to this batch file.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0set_chrome_topmost.ps1" "%PORT%" >nul 2>&1

echo Launched Chrome to http://localhost:%PORT%/ (Chrome window set to topmost)
pause