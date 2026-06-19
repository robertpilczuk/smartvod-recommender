@echo off
REM Wrapper na run.py — przygotowuje wszystko i uruchamia SmartVOD (Windows).
REM Rownowazne: python run.py
cd /d "%~dp0"
python run.py %*
pause
