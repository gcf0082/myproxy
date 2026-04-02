#!/bin/bash

# MyProxy 测试脚本

set -e

DB_PATH="/tmp/test_proxy.db"
PORT=8080

echo "========================================"
echo "MyProxy 自动化测试"
echo "========================================"

# 清理旧数据
rm -f "$DB_PATH"

# 启动代理
echo ""
echo "[1] 启动代理服务器..."
mitmdump --set ssl_insecure=true --set listen_port=$PORT --set dbpath=$DB_PATH -s addon.py 2>&1 &
PROXY_PID=$!
sleep 3

# 检查代理是否启动成功
if ! kill -0 $PROXY_PID 2>/dev/null; then
    echo "错误：代理启动失败"
    exit 1
fi
echo "代理已启动 (PID: $PROXY_PID)"

# 测试 HTTP 请求
echo ""
echo "[2] 发送测试请求..."

echo "  - GET 请求"
curl -s --proxy http://localhost:$PORT http://httpbin.org/get > /dev/null

echo "  - POST 请求"
curl -s --proxy http://localhost:$PORT -X POST -H "Content-Type: application/json" -d '{"name":"test"}' http://httpbin.org/post > /dev/null

echo "  - 带自定义 Header 的请求"
curl -s --proxy http://localhost:$PORT -H "X-Custom-Header: test-value" http://httpbin.org/headers > /dev/null

echo "  - HTTPS 请求"
curl -s --proxy http://localhost:$PORT -k https://httpbin.org/get > /dev/null

echo "请求发送完成"

# 等待数据写入
sleep 1

# 停止代理
echo ""
echo "[3] 停止代理..."
kill $PROXY_PID 2>/dev/null || true
sleep 1

# 测试查询功能
echo ""
echo "[4] 测试查询功能..."

echo ""
echo "  4.1 查询所有请求"
python main.py query --db $DB_PATH

echo ""
echo "  4.2 按方法过滤 (POST)"
python main.py query --db $DB_PATH --method POST

echo ""
echo "  4.3 按 URL 过滤 (httpbin)"
python main.py query --db $DB_PATH --url httpbin

echo ""
echo "  4.4 按状态码过滤 (200)"
python main.py query --db $DB_PATH --status 200

echo ""
echo "  4.5 按请求头过滤 (X-Custom-Header)"
python main.py query --db $DB_PATH --req-header "X-Custom-Header:test-value"

echo ""
echo "  4.6 限制结果数量 (2)"
python main.py query --db $DB_PATH --limit 2

echo ""
echo "  4.7 详细输出模式"
python main.py query --db $DB_PATH --verbose --limit 1

echo ""
echo "========================================"
echo "测试完成！"
echo "========================================"
echo ""
echo "数据库路径: $DB_PATH"
echo "测试数据已保存，可使用以下命令查看:"
echo "  python main.py query --db $DB_PATH --verbose"