@echo off
chcp 65001 >nul
echo.
echo ================================================
echo        陌生单词收集与背诵软件
echo ================================================
echo.
echo   1. 桌面模式 (电脑使用)
echo   2. Web模式 (手机电脑都可访问)
echo.
set /p choice="请选择 (1/2): "

if "%choice%"=="2" goto web_mode

:desktop_mode
echo.
echo 正在启动桌面模式...
python "%~dp0main.py"
goto end

:web_mode
echo.
echo 正在启动Web模式...
echo ================================================
python "%~dp0main.py" --web
goto end

:end
pause
