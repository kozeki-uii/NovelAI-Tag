@echo off
chcp 65001 >nul
cd /d %~dp0
echo == Converting codex .docx files (folder: 法典源) ==
python tools\convert.py
echo.
echo Done. Data written to site\data\
pause
