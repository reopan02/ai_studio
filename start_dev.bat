@echo off
SET PORT=8888
SET HOST=0.0.0.0

echo --- 正在启动 Video API Dashboard ---

REM 1. 检查环境变量
if not exist .env (
    echo [!] 未发现 .env 文件，正在从 .env.example 复制...
    copy .env.example .env
)

REM 2. 前端构建选项
set /p build_choice="是否需要重新构建前端? (y/N): "
if /i "%build_choice%"=="y" (
    echo --- 正在构建前端 ---
    cd frontend
    call npm install
    call npm run build
    cd ..
    echo [+] 前端构建完成
)

REM 3. 启动后端
echo --- 正在启动后端服务 (端口: %PORT%) ---
python -m uvicorn app.main:app --host %HOST --port %PORT --reload
pause
