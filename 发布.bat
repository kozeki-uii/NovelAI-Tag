@echo off
chcp 65001 >nul
cd /d %~dp0
echo == Publishing updates to GitHub (Cloudflare will auto-deploy) ==
git add -A
git commit -m "update codex / images"
git push
echo.
echo Done. The live site updates in ~1 minute.
pause
