#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR" || exit 1

# Colors (keep consistent with scripts/manage.sh)
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() { echo -e "${GREEN}[start] $*${NC}"; }
warn() { echo -e "${YELLOW}[start] $*${NC}"; }
err() { echo -e "${RED}[start] $*${NC}"; }
have_cmd() { command -v "$1" >/dev/null 2>&1; }

warn "正在进行启动前依赖检查..."

# 1) Env file
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    warn "未发现 .env，已从 .env.example 生成（请按需填写 API_KEY 等配置）"
    cp ".env.example" ".env"
fi

# 2) Python + venv + backend deps
PYTHON=""
if have_cmd python3; then
    PYTHON="python3"
elif have_cmd python; then
    PYTHON="python"
else
    err "未检测到 python/python3。请安装 Python 3.10+ 后重试。"
    exit 1
fi

VENV_DIR="${VENV_DIR:-$SCRIPT_DIR/.venv}"
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    warn "未检测到虚拟环境：$VENV_DIR（将尝试创建）"
    if ! "$PYTHON" -m venv "$VENV_DIR" >/dev/null 2>&1; then
        err "创建虚拟环境失败：$PYTHON -m venv $VENV_DIR"
        err "Linux(ubuntu/debian) 可能需要：sudo apt-get install -y python3-venv"
        exit 1
    fi
    log "已创建虚拟环境：$VENV_DIR"
fi

# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

if ! python -c 'import uvicorn' >/dev/null 2>&1; then
    warn "未检测到后端依赖（uvicorn 等），将自动安装 requirements.txt"
    if ! python -m pip --version >/dev/null 2>&1; then
        err "未检测到 pip。请先安装 pip 后重试。"
        exit 1
    fi
    python -m pip install --upgrade pip
    python -m pip install -r "$SCRIPT_DIR/requirements.txt"
fi

# 3) Docker / Compose (optional, used for local Supabase)
SUPABASE_COMPOSE_DIR="${SUPABASE_COMPOSE_DIR:-$SCRIPT_DIR/.supabase/docker}"
SKIP_DB="${SKIP_DB:-0}"

has_compose_file=0
if [ -d "$SUPABASE_COMPOSE_DIR" ]; then
    for f in docker-compose.yml docker-compose.yaml compose.yml compose.yaml; do
        if [ -f "$SUPABASE_COMPOSE_DIR/$f" ]; then
            has_compose_file=1
            break
        fi
    done
fi

if [ "$SKIP_DB" != "1" ] && [ "$has_compose_file" = "1" ]; then
    if ! have_cmd docker; then
        warn "未检测到 docker，将跳过本地 Supabase 启动（安装 Docker Desktop / Docker Engine 后再试）"
        SKIP_DB=1
    elif ! docker info >/dev/null 2>&1; then
        warn "docker 已安装但不可用（daemon 未启动或权限不足），将跳过本地 Supabase 启动"
        warn "如需使用：启动 Docker Desktop / docker 服务，或将当前用户加入 docker 组"
        SKIP_DB=1
    elif ! (docker compose version >/dev/null 2>&1 || have_cmd docker-compose); then
        warn "未检测到 docker compose，将跳过本地 Supabase 启动（请安装 compose 插件或 docker-compose）"
        SKIP_DB=1
    fi
elif [ "$has_compose_file" = "0" ]; then
    warn "未检测到 Supabase compose 目录：$SUPABASE_COMPOSE_DIR（如需本地数据库请先运行 ./setup-supabase.sh）"
fi

# 4) npm (optional, only needed when app/static is missing and frontend needs rebuild)
if [ -d "$SCRIPT_DIR/frontend" ] && [ -f "$SCRIPT_DIR/frontend/package.json" ]; then
    if [ ! -d "$SCRIPT_DIR/app/static" ] || [ ! -f "$SCRIPT_DIR/app/static/app.html" ]; then
        if ! have_cmd npm; then
            err "未检测到 npm，且 app/static 缺失；无法构建前端。请安装 Node.js(LTS) 后重试。"
            exit 1
        fi
        warn "未检测到前端构建产物 app/static（将执行 npm install && npm run build）"
        (cd "$SCRIPT_DIR/frontend" && npm install && npm run build)
    elif ! have_cmd npm; then
        warn "未检测到 npm（不影响启动；如需重新构建前端请安装 Node.js）"
    fi
fi

log "依赖检查完成，开始启动服务..."

if [ "$SKIP_DB" != "1" ]; then
    "$SCRIPT_DIR/scripts/manage.sh" db-start || warn "数据库启动失败（将继续启动后端；请查看上方日志）"
else
    warn "已跳过数据库启动（可设置 SKIP_DB=0 并确保 Docker 可用后重试）"
fi

"$SCRIPT_DIR/scripts/manage.sh" start
