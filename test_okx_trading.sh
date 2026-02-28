#!/bin/bash
# OKX 交易页面功能测试脚本

BASE_URL="http://localhost:9002"

echo "======================================"
echo "OKX 交易系统功能测试"
echo "======================================"
echo ""

# 1. 测试账户列表 API
echo "1. 测试账户列表 API..."
response=$(curl -s "${BASE_URL}/api/okx-accounts/list-with-credentials")
if echo "$response" | grep -q '"success": true'; then
    echo "✅ 账户列表 API 正常"
else
    echo "❌ 账户列表 API 异常"
    echo "$response"
fi
echo ""

# 2. 测试常用币列表 API
echo "2. 测试常用币列表 API..."
response=$(curl -s "${BASE_URL}/api/okx-trading/favorite-symbols")
if echo "$response" | grep -q '"success": true'; then
    echo "✅ 常用币列表 API 正常"
else
    echo "❌ 常用币列表 API 异常"
    echo "$response"
fi
echo ""

# 3. 测试交易日志 API
echo "3. 测试交易日志 API..."
response=$(curl -s "${BASE_URL}/api/okx-trading/logs?limit=5")
if echo "$response" | grep -q '"success": true'; then
    echo "✅ 交易日志 API 正常"
else
    echo "❌ 交易日志 API 异常"
    echo "$response"
fi
echo ""

# 4. 测试止盈止损设置 API (GET)
echo "4. 测试止盈止损设置 API (GET)..."
response=$(curl -s "${BASE_URL}/api/okx-trading/tpsl-settings/account_main")
if echo "$response" | grep -q '"success": true'; then
    echo "✅ 止盈止损设置 API (GET) 正常"
else
    echo "❌ 止盈止损设置 API (GET) 异常"
    echo "$response"
fi
echo ""

# 5. 测试自动交易策略 API (GET)
echo "5. 测试自动交易策略 API (GET)..."
response=$(curl -s "${BASE_URL}/api/okx-trading/auto-strategy/account_main")
if echo "$response" | grep -q '"success": true'; then
    echo "✅ 自动交易策略 API (GET) 正常"
else
    echo "❌ 自动交易策略 API (GET) 异常"
    echo "$response"
fi
echo ""

# 6. 检查数据目录权限
echo "6. 检查数据目录权限..."
for dir in okx_trading_logs okx_tpsl_settings okx_auto_strategies; do
    if [ -d "/home/user/webapp/data/$dir" ]; then
        perms=$(ls -ld "/home/user/webapp/data/$dir" | awk '{print $1}')
        echo "   $dir: $perms ✅"
    else
        echo "   $dir: 目录不存在 ⚠️"
    fi
done
echo ""

# 7. 检查 Flask 日志中的错误
echo "7. 检查 Flask 近期日志..."
error_count=$(pm2 logs flask-app --nostream --lines 100 2>&1 | grep -i "error\|exception\|permission denied" | wc -l)
if [ "$error_count" -eq 0 ]; then
    echo "✅ 近期日志无错误"
else
    echo "⚠️ 发现 $error_count 条错误日志"
    pm2 logs flask-app --nostream --lines 20 | grep -i "error\|exception\|permission denied" | tail -5
fi
echo ""

echo "======================================"
echo "测试完成"
echo "======================================"
