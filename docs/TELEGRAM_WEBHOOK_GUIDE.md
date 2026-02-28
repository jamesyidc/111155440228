# Telegram Webhook批量开仓功能指南

## 功能概述

该功能允许用户通过Telegram机器人的按钮，触发批量开仓操作。整个流程分为三个步骤：
1. **点击开仓按钮** → 显示账号信息
2. **确认执行** → 批量开仓
3. **反馈结果** → 显示每个账号的开仓结果

## 系统架构

### 1. Telegram Bot
- Bot Token: 存储在环境变量 `TG_BOT_TOKEN`
- Webhook URL: `https://your-domain.com/api/telegram/webhook`

### 2. 开仓按钮格式
callback_data格式: `trade_{direction}_{tier}_{percentage}`
- direction: `long`(做多) 或 `short`(做空)
- tier: `pre6`(前6) 或 `post6`(后6)
- percentage: `3`, `5`, 或 `8`

示例按钮：
```python
{
    'inline_keyboard': [[
        {'text': '多前6 3%', 'callback_data': 'trade_long_pre6_3'},
        {'text': '多前6 5%', 'callback_data': 'trade_long_pre6_5'},
        {'text': '多前6 8%', 'callback_data': 'trade_long_pre6_8'}
    ], [
        {'text': '多后6 3%', 'callback_data': 'trade_long_post6_3'},
        {'text': '多后6 5%', 'callback_data': 'trade_long_post6_5'},
        {'text': '多后6 8%', 'callback_data': 'trade_long_post6_8'}
    ], [
        {'text': '空前6 3%', 'callback_data': 'trade_short_pre6_3'},
        {'text': '空前6 5%', 'callback_data': 'trade_short_pre6_5'},
        {'text': '空前6 8%', 'callback_data': 'trade_short_pre6_8'}
    ], [
        {'text': '空后6 3%', 'callback_data': 'trade_short_post6_3'},
        {'text': '空后6 5%', 'callback_data': 'trade_short_post6_5'},
        {'text': '空后6 8%', 'callback_data': 'trade_short_post6_8'}
    ]]
}
```

## 实现流程

### 步骤1: 点击开仓按钮
当用户点击按钮（如"多前6 3%"）：

1. Telegram发送callback_query到webhook：
```json
{
    "callback_query": {
        "data": "trade_long_pre6_3",
        "from": {"id": 123456, "first_name": "User"},
        "message": {"chat": {"id": 123456}}
    }
}
```

2. Webhook处理：
```python
@app.route('/api/telegram/webhook', methods=['POST'])
def telegram_webhook():
    # 解析callback_data
    parts = callback_data.split('_')
    direction = parts[1]  # long
    tier = parts[2]       # pre6
    percentage = parts[3]  # 3
    
    # 获取所有账号
    accounts = get_all_okx_accounts()
    
    # 显示账号信息
    message = f"📋 找到 {len(accounts)} 个账号:\\n"
    for acc in accounts:
        message += f"• {acc['name']}\\n"
    message += f"\\n💰 将为每个账号开仓 {percentage}% 资金\\n"
    
    # 发送确认按钮
    send_telegram_message(chat_id, message, buttons)
```

3. 返回给用户的消息：
```
📋 找到 2 个账号:

• Default Account
• Fangfang12

💰 将为每个账号开仓 3% 资金
📊 方向: 做多

⚠️ 请在60秒内确认执行

[✅ 确认执行] [❌ 取消]
```

### 步骤2: 确认执行
当用户点击"✅ 确认执行"按钮：

1. Telegram发送新的callback_query:
```json
{
    "callback_query": {
        "data": "confirm_trade_long_pre6_3"
    }
}
```

2. Webhook处理：
```python
elif callback_data.startswith('confirm_trade_'):
    # 解析原始交易参数
    original_data = callback_data.replace('confirm_', '')
    
    # 执行批量开仓
    result = execute_batch_trading(direction, tier, percentage)
    
    # 发送结果
    send_result_message(chat_id, result)
```

3. 批量开仓逻辑：
```python
def execute_batch_trading(direction, tier, percentage):
    # 获取所有账号
    accounts = get_all_okx_accounts()
    
    results = {'success_count': 0, 'failed_count': 0, 'details': []}
    
    # 遍历每个账号
    for account in accounts:
        try:
            # 构建开仓参数
            trade_data = {
                'account_id': account['id'],
                'direction': 'buy' if direction == 'long' else 'sell',
                'percentage': int(percentage),
                'tier': tier,
                'symbol': 'BTC-USDT-SWAP'
            }
            
            # 调用OKX开仓API
            response = place_okx_order(trade_data)
            
            if response.success:
                results['success_count'] += 1
                results['details'].append(f"✅ {account['name']}: 开仓成功")
            else:
                results['failed_count'] += 1
                results['details'].append(f"❌ {account['name']}: {error}")
        
        except Exception as e:
            results['failed_count'] += 1
            results['details'].append(f"❌ {account['name']}: {str(e)}")
    
    return results
```

### 步骤3: 反馈结果
系统发送最终结果消息：
```
📊 批量开仓结果

✅ 成功: 2
❌ 失败: 0

详情:
• ✅ Default Account: 开仓成功
• ✅ Fangfang12: 开仓成功
```

## API端点

### 1. Telegram Webhook
- **URL**: `/api/telegram/webhook`
- **Method**: POST
- **处理**: 接收Telegram的callback_query

### 2. 获取账号列表
- **URL**: `/api/okx-accounts/list`
- **Method**: GET
- **返回**:
```json
{
    "success": true,
    "count": 2,
    "accounts": [
        {
            "id": "default",
            "name": "Default Account",
            "status": "active",
            "environment": "PROD"
        },
        {
            "id": "fangfang12",
            "name": "Fangfang12",
            "status": "active",
            "environment": "PROD"
        }
    ]
}
```

### 3. 下单接口
- **URL**: `/api/okx-trading/place-order`
- **Method**: POST
- **参数**:
```json
{
    "account_id": "default",
    "instId": "BTC-USDT-SWAP",
    "side": "buy",
    "posSide": "long",
    "ordType": "market",
    "sz": "100",
    "lever": "10"
}
```

## 环境配置

### 1. 设置Telegram Bot Token
```bash
export TG_BOT_TOKEN="your_bot_token_here"
```

### 2. 设置Webhook
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-domain.com/api/telegram/webhook",
    "allowed_updates": ["callback_query"]
  }'
```

### 3. 配置OKX账号
编辑 `/home/user/webapp/live-trading-system/okx_accounts_config.json`:
```json
{
    "accounts": {
        "default": {
            "name": "Default Account",
            "apiKey": "your-api-key",
            "apiSecret": "your-api-secret",
            "passphrase": "your-passphrase",
            "environment": "PROD",
            "status": "active"
        }
    }
}
```

## 测试

### 使用测试工具
```bash
cd /home/user/webapp
python3 test_telegram_webhook.py
```

### 手动测试
```bash
curl -X POST http://localhost:5000/api/telegram/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "callback_query": {
        "data": "trade_long_pre6_3",
        "from": {"id": 123456, "first_name": "Test"},
        "message": {"chat": {"id": 123456}}
    }
}'
```

## 错误处理

系统会处理以下错误：
1. **账号获取失败**: 返回"❌ 获取账号失败"
2. **开仓失败**: 记录具体账号和错误原因
3. **网络超时**: 自动重试或标记失败
4. **API凭证错误**: 返回"API凭证不完整"

## 日志查看

```bash
# 查看Flask日志
pm2 logs flask-app --lines 50

# 查看Telegram相关日志
pm2 logs flask-app | grep "Telegram"
```

## 安全注意事项

1. **验证用户身份**: 可以添加白名单验证
2. **限制频率**: 防止滥用
3. **资金安全**: 设置单次开仓上限
4. **审计日志**: 记录所有操作

## 未来改进

1. **用户权限管理**: 不同用户不同权限
2. **风险控制**: 添加仓位限制和止损
3. **多币种支持**: 选择不同币种开仓
4. **高级策略**: 支持更复杂的交易策略
5. **实时通知**: 开仓后实时推送结果
