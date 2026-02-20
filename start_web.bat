@echo off
chcp 65001 >nul
echo.
echo ================================================
echo    陌生单词收集与背诵软件 - Web模式
echo ================================================
echo.

cd /d "%~dp0"

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    goto :found
)
:found
set IP=%IP: =%

echo   电脑访问: http://localhost:8555
echo   手机访问: http://%IP%:8555
echo ================================================
echo   提示: 确保手机和电脑在同一WiFi
echo ================================================
echo.
echo   正在启动... 请等待浏览器自动打开
echo.

flet run --web --port 8555 main.py

pause
