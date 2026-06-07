@echo off
chcp 65001 >nul
cd /d %~dp0
echo Opening http://localhost:8766  (close this window to stop)
start "" http://localhost:8766
python -m http.server 8766 --directory site
