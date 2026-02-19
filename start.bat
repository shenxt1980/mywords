@echo off
chcp 65001 >nul
echo ==================================================
echo    陌生单词收集与背诵软件 - 启动器
echo ==================================================
echo.
echo 请选择启动方式:
echo   1. 桌面模式 (电脑端使用)
echo   2. Web模式 (手机和电脑都可访问)
echo.
set /p choice="请输入选择 (1/2): "

if "%choice%"=="1" (
    echo.
    echo 正在启动桌面模式...
    python main.py
) else if "%choice%"=="2" (
    echo.
    echo 正在启动Web模式...
    echo ==================================================
    python main.py --web
) else (
    echo 无效选择，启动桌面模式...
    python main.py
)

pause
