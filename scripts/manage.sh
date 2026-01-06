#!/bin/bash

# 尝试激活虚拟环境
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "../venv/bin/activate" ]; then
    source ../venv/bin/activate
fi

# 配置
APP_NAME="AI Video Generator API"
MODULE="app.main:app"
HOST="0.0.0.0"
PORT=8887
LOG_FILE="server.log"
PID_FILE="server.pid"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

usage() {
    echo "使用方法: $0 {start|stop|restart|status|logs}"
    exit 1
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
    *)
        usage
        ;;
esac
