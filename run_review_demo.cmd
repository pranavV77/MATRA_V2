@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" -m src.review_demo.server --port 8765
pause
