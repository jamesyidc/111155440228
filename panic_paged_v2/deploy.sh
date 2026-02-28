#!/bin/bash
# Panic Paged V2 快速部署脚本

set -e  # 遇到错误立即退出

echo "=========================================="
echo "  Panic Paged V2 - 快速部署脚本"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'  # No Color

# 工作目录
WEBAPP_DIR="/home/user/webapp"
PANIC_DIR="$WEBAPP_DIR/panic_paged_v2"
DATA_DIR="$PANIC_DIR/data"
LOGS_DIR="$WEBAPP_DIR/logs"

echo -e "${YELLOW}[1/6] 检查目录结构...${NC}"
cd "$WEBAPP_DIR"

if [ ! -d "$PANIC_DIR" ]; then
    echo -e "${RED}错误: $PANIC_DIR 目录不存在${NC}"
    exit 1
fi

# 创建data和logs目录
mkdir -p "$DATA_DIR"
mkdir -p "$LOGS_DIR"
echo -e "${GREEN}✓ 目录结构正常${NC}"
echo ""

echo -e "${YELLOW}[2/6] 检查Python文件...${NC}"
required_files=(
    "collector_24h.py"
    "collector_1h.py"
    "data_manager.py"
    "api_routes.py"
    "ecosystem.config.json"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$PANIC_DIR/$file" ]; then
        echo -e "${RED}错误: $file 不存在${NC}"
        exit 1
    fi
    echo "  ✓ $file"
done
echo -e "${GREEN}✓ 所有必需文件存在${NC}"
echo ""

echo -e "${YELLOW}[3/6] 测试Python依赖...${NC}"
python3 -c "import requests; import json; import time" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python依赖正常${NC}"
else
    echo -e "${RED}错误: 缺少Python依赖（requests）${NC}"
    echo "运行: pip3 install requests"
    exit 1
fi
echo ""

echo -e "${YELLOW}[4/6] 启动PM2采集器...${NC}"
cd "$PANIC_DIR"

# 停止旧的采集器（如果存在）
pm2 stop panic-paged-v2-collector-24h 2>/dev/null || true
pm2 stop panic-paged-v2-collector-1h 2>/dev/null || true
pm2 delete panic-paged-v2-collector-24h 2>/dev/null || true
pm2 delete panic-paged-v2-collector-1h 2>/dev/null || true

# 启动新的采集器
pm2 start ecosystem.config.json
sleep 2

# 检查状态
if pm2 status | grep -q "panic-paged-v2-collector-24h.*online"; then
    echo -e "${GREEN}✓ 24h采集器已启动${NC}"
else
    echo -e "${RED}✗ 24h采集器启动失败${NC}"
fi

if pm2 status | grep -q "panic-paged-v2-collector-1h.*online"; then
    echo -e "${GREEN}✓ 1h采集器已启动${NC}"
else
    echo -e "${RED}✗ 1h采集器启动失败${NC}"
fi

pm2 save
echo ""

echo -e "${YELLOW}[5/6] 集成到Flask应用...${NC}"
FLASK_APP="$WEBAPP_DIR/code/python/app.py"

if [ ! -f "$FLASK_APP" ]; then
    echo -e "${RED}错误: Flask应用不存在: $FLASK_APP${NC}"
    exit 1
fi

# 检查是否已经集成
if grep -q "register_panic_paged_routes" "$FLASK_APP"; then
    echo -e "${GREEN}✓ Flask路由已集成${NC}"
else
    echo -e "${YELLOW}需要手动集成Flask路由${NC}"
    echo "在 $FLASK_APP 中添加:"
    echo ""
    echo "  import sys"
    echo "  sys.path.insert(0, '/home/user/webapp/panic_paged_v2')"
    echo "  from api_routes import register_panic_paged_routes"
    echo "  register_panic_paged_routes(app)"
    echo ""
fi
echo ""

echo -e "${YELLOW}[6/6] 验证部署...${NC}"

# 等待采集器运行
echo "等待采集器生成数据..."
sleep 5

# 检查数据文件
DATA_FILES_COUNT=$(find "$DATA_DIR" -name "panic_*.jsonl" 2>/dev/null | wc -l)
if [ "$DATA_FILES_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ 数据文件已生成 ($DATA_FILES_COUNT 个)${NC}"
    ls -lh "$DATA_DIR"/*.jsonl 2>/dev/null | tail -5
else
    echo -e "${YELLOW}⚠ 暂无数据文件，请等待1分钟后再检查${NC}"
fi
echo ""

echo "=========================================="
echo -e "${GREEN}  部署完成！${NC}"
echo "=========================================="
echo ""

echo "📊 系统状态:"
pm2 status | grep -E "flask-app|panic-paged-v2"
echo ""

echo "🔍 快速测试命令:"
echo ""
echo "  # 查看采集器日志"
echo "  pm2 logs panic-paged-v2-collector-24h"
echo "  pm2 logs panic-paged-v2-collector-1h"
echo ""
echo "  # 查看数据文件"
echo "  ls -lh $DATA_DIR/"
echo ""
echo "  # 测试API（需要先重启flask-app）"
echo "  curl http://localhost:5000/api/panic-paged/available-dates | python3 -m json.tool"
echo ""

echo "⚠️  注意事项:"
echo "  1. 需要重启Flask应用: pm2 restart flask-app"
echo "  2. 如果API路由未集成，需要手动添加到app.py"
echo "  3. 数据采集需要1分钟后才会有第一条记录"
echo ""

echo "📚 文档:"
echo "  README: $PANIC_DIR/README.md"
echo ""
