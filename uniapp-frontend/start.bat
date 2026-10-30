@echo off
chcp 65001 >nul
echo ========================================
echo   AI 私人厨师 - UniApp 前端启动
echo ========================================
echo.

:: 检查 Node.js 版本
echo [1/3] 检查 Node.js 版本...
node --version
if errorlevel 1 (
    echo 错误: 未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)
echo.

:: 安装依赖
echo [2/3] 安装依赖...
call npm install
if errorlevel 1 (
    echo 错误: 依赖安装失败，请以管理员身份运行
    pause
    exit /b 1
)
echo.

:: 启动开发服务器
echo [3/3] 启动 H5 开发服务器...
echo 访问地址: http://localhost:5173
echo.
call npm run dev:h5
