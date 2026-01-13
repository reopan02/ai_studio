#!/bin/bash

# Move to project root (works regardless of where the script is invoked from).
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

# 尝试激活虚拟环境
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# 配置
APP_NAME="AI Video Generator API"
MODULE="app.main:app"
HOST="0.0.0.0"
PORT=8887
LOG_FILE="server.log"
PID_FILE="server.pid"

# Supabase (database) compose directory (created by following infra/supabase/README.md)
SUPABASE_COMPOSE_DIR="${SUPABASE_COMPOSE_DIR:-$PROJECT_ROOT/.supabase/docker}"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

usage() {
    echo "使用方法: $0 {start|stop|restart|status|logs|db-start|db-stop|db-restart|db-status}"
    exit 1
}

detect_compose_cmd() {
    if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
        COMPOSE_CMD=(docker compose)
        return 0
    fi
    if command -v docker-compose >/dev/null 2>&1; then
        COMPOSE_CMD=(docker-compose)
        return 0
    fi
    return 1
}

has_supabase_compose() {
    if [ ! -d "$SUPABASE_COMPOSE_DIR" ]; then
        return 1
    fi
    if [ -f "$SUPABASE_COMPOSE_DIR/docker-compose.yml" ] || [ -f "$SUPABASE_COMPOSE_DIR/docker-compose.yaml" ] || [ -f "$SUPABASE_COMPOSE_DIR/compose.yml" ] || [ -f "$SUPABASE_COMPOSE_DIR/compose.yaml" ]; then
        return 0
    fi
    return 1
}

db_start() {
    if ! has_supabase_compose; then
        echo -e "${YELLOW}[DB] 未检测到 Supabase docker compose 目录：$SUPABASE_COMPOSE_DIR（将跳过数据库启动）${NC}"
        return 0
    fi

    if ! detect_compose_cmd; then
        echo -e "${RED}[DB] 未检测到 docker compose（请安装 Docker Desktop / docker-compose），无法启动数据库${NC}"
        return 1
    fi

    if [ ! -f "$SUPABASE_COMPOSE_DIR/.env" ] && [ -f "$SUPABASE_COMPOSE_DIR/.env.example" ]; then
        cp "$SUPABASE_COMPOSE_DIR/.env.example" "$SUPABASE_COMPOSE_DIR/.env"
        echo -e "${YELLOW}[DB] 已从 .env.example 生成 $SUPABASE_COMPOSE_DIR/.env，请按需修改（尤其是 JWT_SECRET 等）${NC}"
    fi

    echo -e "${GREEN}[DB] 正在启动 Supabase（Postgres/Auth/PostgREST）...${NC}"
    (cd "$SUPABASE_COMPOSE_DIR" && "${COMPOSE_CMD[@]}" up -d)
}

db_stop() {
    if ! has_supabase_compose; then
        echo -e "${YELLOW}[DB] 未检测到 Supabase docker compose 目录：$SUPABASE_COMPOSE_DIR（将跳过数据库停止）${NC}"
        return 0
    fi

    if ! detect_compose_cmd; then
        echo -e "${RED}[DB] 未检测到 docker compose，无法停止数据库${NC}"
        return 1
    fi

    echo -e "${YELLOW}[DB] 正在停止 Supabase...${NC}"
    (cd "$SUPABASE_COMPOSE_DIR" && "${COMPOSE_CMD[@]}" down)
}

db_status() {
    if ! has_supabase_compose; then
        echo -e "${YELLOW}[DB] 未检测到 Supabase docker compose 目录：$SUPABASE_COMPOSE_DIR${NC}"
        return 0
    fi

    if ! detect_compose_cmd; then
        echo -e "${RED}[DB] 未检测到 docker compose，无法查看数据库状态${NC}"
        return 1
    fi

    (cd "$SUPABASE_COMPOSE_DIR" && "${COMPOSE_CMD[@]}" ps)
}

is_running() {
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null; then
            return 0
        else
            rm "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

start() {
    if is_running; then
        echo -e "${YELLOW}$APP_NAME 已经在运行中 (PID: $(cat "$PID_FILE"))${NC}"
    else
        echo -e "${GREEN}正在启动 $APP_NAME...${NC}"
        nohup uvicorn "$MODULE" --host "$HOST" --port "$PORT" > "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        sleep 2
        if is_running; then
            echo -e "${GREEN}$APP_NAME 启动成功! (PID: $(cat "$PID_FILE"))${NC}"
            echo -e "日志文件: $LOG_FILE"
        else
            echo -e "${RED}$APP_NAME 启动失败，请检查日志 $LOG_FILE${NC}"
        fi
    fi
}

stop() {
    if is_running; then
        pid=$(cat "$PID_FILE")
        echo -e "${YELLOW}正在停止 $APP_NAME (PID: $pid)...${NC}"
        kill "$pid"
        sleep 2
        if is_running; then
            echo -e "${YELLOW}进程未响应，尝试强制停止...${NC}"
            kill -9 "$pid"
            sleep 1
        fi
        [ -f "$PID_FILE" ] && rm "$PID_FILE"
        echo -e "${GREEN}$APP_NAME 已停止${NC}"
    else
        # 兜底检查端口
        port_pid=$(lsof -t -i:$PORT)
        if [ -n "$port_pid" ]; then
            echo -e "${YELLOW}发现端口 $PORT 被占用 (PID: $port_pid)，正在停止...${NC}"
            kill "$port_pid"
            echo -e "${GREEN}已清理占用端口的进程${NC}"
        else
            echo -e "${YELLOW}$APP_NAME 未在运行${NC}"
        fi
    fi
}

status() {
    if is_running; then
        echo -e "${GREEN}$APP_NAME 正在运行 (PID: $(cat "$PID_FILE"))${NC}"
        echo -e "监听地址: http://$HOST:$PORT"
    else
        echo -e "${RED}$APP_NAME 未在运行${NC}"
    fi
}

logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo -e "${RED}日志文件 $LOG_FILE 不存在${NC}"
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        start
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    db-start)
        db_start
        ;;
    db-stop)
        db_stop
        ;;
    db-restart)
        db_stop
        db_start
        ;;
    db-status)
        db_status
        ;;
    *)
        usage
        ;;
esac
