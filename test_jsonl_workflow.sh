#!/bin/bash
# 测试JSONL工作流程

set -e

echo "========================================="
echo "📊 测试日内模式检测JSONL工作流"
echo "========================================="

DATE="2026-02-25"

echo ""
echo "1️⃣ 生成检测结果到JSONL..."
python3 scripts/generate_all_patterns_daily.py --date "$DATE"

echo ""
echo "2️⃣ 检查JSONL文件是否存在..."
JSONL_FILE="data/intraday_patterns/all_detections_${DATE}.jsonl"
if [ -f "$JSONL_FILE" ]; then
    echo "✅ JSONL文件存在: $JSONL_FILE"
    echo "   文件大小: $(du -h "$JSONL_FILE" | cut -f1)"
else
    echo "❌ JSONL文件不存在: $JSONL_FILE"
    exit 1
fi

echo ""
echo "3️⃣ 测试API从JSONL读取..."
API_RESPONSE=$(curl -s "http://localhost:9002/api/intraday-patterns/all-detections/${DATE}")

echo "   API响应示例:"
echo "$API_RESPONSE" | python3 -m json.tool | head -20

echo ""
echo "4️⃣ 验证数据源标记..."
SOURCE=$(echo "$API_RESPONSE" | python3 -c "import json, sys; print(json.load(sys.stdin).get('source', 'UNKNOWN'))")
if [ "$SOURCE" = "jsonl" ]; then
    echo "✅ 数据来源正确: $SOURCE"
else
    echo "❌ 数据来源错误: $SOURCE (期望: jsonl)"
    exit 1
fi

echo ""
echo "5️⃣ 验证页面能正常加载..."
PAGE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:9002/coin-change-tracker")
if [ "$PAGE_STATUS" = "200" ]; then
    echo "✅ 页面加载成功: HTTP $PAGE_STATUS"
else
    echo "❌ 页面加载失败: HTTP $PAGE_STATUS"
    exit 1
fi

echo ""
echo "========================================="
echo "✅ 所有测试通过！"
echo "========================================="
echo ""
echo "📝 使用说明:"
echo "   - JSONL文件路径: $JSONL_FILE"
echo "   - API地址: http://localhost:9002/api/intraday-patterns/all-detections/${DATE}"
echo "   - 页面地址: http://localhost:9002/coin-change-tracker"
echo ""
