@echo off
chcp 65001 >nul
cd /d %~dp0
echo Image tool:  http://localhost:8767/__pei__
echo Gallery:     http://localhost:8767/
start "" http://localhost:8767/__pei__
python tools\imgserver.py
