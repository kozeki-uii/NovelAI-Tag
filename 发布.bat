@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

where git >nul 2>nul
if errorlevel 1 (
  echo Git not found. Please install Git for Windows first.
  pause
  exit /b 1
)

REM --- find Python: prefer the 'py' launcher, then 'python' ---
set "PY="
where py >nul 2>nul && set "PY=py"
if not defined PY ( where python >nul 2>nul && set "PY=python" )
if not defined PY (
  echo [ERROR] Python not found.
  echo Install Python 3 from https://www.python.org/downloads/ ^(tick "Add to PATH"^).
  pause
  exit /b 1
)

if not exist r2_config.json (
  echo [ERROR] Missing r2_config.json
  echo Copy r2_config.example.json to r2_config.json and fill in your R2 keys before publishing.
  pause
  exit /b 1
)

echo == Syncing images to Cloudflare R2 ==
%PY% tools\sync_r2.py
set "RC=%ERRORLEVEL%"
if "%RC%"=="1" goto :fail
if not "%RC%"=="0" echo [WARN] R2 sync reported non-fatal issues, code %RC%. Continuing to publish.

echo == Publishing updates to GitHub - Cloudflare will auto-deploy ==
call git add -A
if errorlevel 1 goto :fail

call git diff --cached --quiet
if errorlevel 1 (
  call git commit -m "更新站点数据和图片"
  if errorlevel 1 goto :fail
) else (
  echo No local changes to commit.
)

call git push
if errorlevel 1 goto :fail

echo.
echo Done. The live site updates in ~1 minute.
pause
exit /b 0

:fail
echo.
echo Publish failed. Please check the message above.
pause
exit /b 1
