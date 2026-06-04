@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo   ========================================
echo   小区物业管理系统 - 一键启动
echo   ========================================
echo.
python setup.py
pause
