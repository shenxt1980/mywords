@echo off
chcp 65001 >nul
echo.
echo ================================================
echo    陌生单词收集与背诵软件 - 桌面模式
echo ================================================
echo.

cd /d "%~dp0"

python main.py

pause
