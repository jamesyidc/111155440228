# 止损反手开单系统

## 📋 系统概述

止损反手开单系统是一个自动化交易策略，当检测到止损事件时，自动执行反向开仓操作。

### 核心功能

1. **多单止损反手开空**：当多单（做多）触发止损时，自动开空单（做空）
2. **空单止损反手开多**：当空单（做空）触发止损时，自动开多单（做多）
3. **防重复触发机制**：触发后自动禁用，需手动重置才能再次触发
4. **多账户独立运行**：每个账户有独立的配置和触发状态
5. **完整日志记录**：所有触发事件记录到JSONL日志文件

---

## 🎯 业务逻辑

### 止损反手流程

```
1. 系统监控 → 检测止损事件
   ↓
2. 读取配置 → 检查是否启用
   ↓
3. 检查权限 → allow_trigger == true?
   ↓
4. 执行策略 → 反向开仓
   ↓
5. 更新状态 → allow_trigger = false
   ↓
6. 记录日志 → 写入触发事件
```

### 触发条件

| 止损类型 | 反手操作 | 目标策略选项 |
|---------|---------|------------|
| 多单止损 | 开空单 | STG_SHORT_TOP8 (涨幅前8名做空)<br>STG_SHORT_BOTTOM8 (涨幅后8名做空) |
| 空单止损 | 开多单 | STG_LONG_TOP8 (涨幅前8名做多)<br>STG_LONG_BOTTOM8 (涨幅后8名做多) |

---

## 🏗️ 系统架构

### 1. API层 (app.py)

#### GET `/api/okx-trading/stoploss-reverse-orders/<account_id>`
获取指定账户的止损反手配置

**响应示例**：
```json
{
  "success": true,
  "account_id": "account_main",
  "configs": [
    {
      "id": "reverse_long_stoploss",
      "type": "long_stoploss_reverse",
      "name": "多单止损反手开空",
      "description": "多单止损后自动反手开空单",
      "enabled": true,
      "allow_trigger": true,
      "target_strategy_code": "STG_SHORT_TOP8",
      "triggered_count": 0,
      "last_triggered_at": null,
      "created_at": "2026-03-02 15:29:42",
      "updated_at": "2026-03-02 15:29:47"
    },
    {
      "id": "reverse_short_stoploss",
      "type": "short_stoploss_reverse",
      "name": "空单止损反手开多",
      "description": "空单止损后自动反手开多单",
      "enabled": false,
      "allow_trigger": true,
      "target_strategy_code": null,
      "triggered_count": 0,
      "last_triggered_at": null,
      "created_at": "2026-03-02 15:29:42",
      "updated_at": "2026-03-02 15:29:42"
    }
  ],
  "timestamp": "2026-03-02 15:29:42"
}
```

#### POST `/api/okx-trading/stoploss-reverse-orders/<account_id>`
更新止损反手配置

**请求参数**：
```json
{
  "id": "reverse_long_stoploss",
  "enabled": true,
  "target_strategy_code": "STG_SHORT_TOP8"
}
```

#### POST `/api/okx-trading/stoploss-reverse-orders/<account_id>/<config_id>/reset-trigger`
重置触发权限

**响应示例**：
```json
{
  "success": true,
  "message": "配置 reverse_long_stoploss 触发权限已重置"
}
```

### 2. 前端UI (templates/okx_trading.html)

#### 多单止损反手开空卡片
- 🔻 图标 + 红色渐变背景
- 启用开关
- 触发条件说明："当多单仓位触发止损时，自动执行反手开空单策略"
- 目标策略下拉选择（涨幅前8名做空 / 涨幅后8名做空）
- 触发权限显示（绿色 = 可触发，红色 = 已触发需重置）
- 重置按钮

#### 空单止损反手开多卡片
- 🔺 图标 + 绿色渐变背景
- 启用开关
- 触发条件说明："当空单仓位触发止损时，自动执行反手开多单策略"
- 目标策略下拉选择（涨幅前8名做多 / 涨幅后8名做多）
- 触发权限显示
- 重置按钮

#### JavaScript函数

| 函数名 | 功能 |
|-------|------|
| `loadStoplossReverseOrders()` | 加载止损反手配置 |
| `displayLongReverseConfig(config)` | 显示多单止损反手配置 |
| `displayShortReverseConfig(config)` | 显示空单止损反手配置 |
| `toggleLongReverse(enabled)` | 切换多单止损反手启用状态 |
| `toggleShortReverse(enabled)` | 切换空单止损反手启用状态 |
| `saveLongReverseSettings()` | 保存多单止损反手设置 |
| `saveShortReverseSettings()` | 保存空单止损反手设置 |
| `resetLongReverseTrigger()` | 重置多单止损反手触发权限 |
| `resetShortReverseTrigger()` | 重置空单止损反手触发权限 |

### 3. 监控器 (monitors/stoploss_reverse_monitor.py)

#### 监控流程
```python
while True:
    for account_id in ACCOUNTS:
        # 1. 加载配置
        configs = load_reverse_configs(account_id)
        
        # 2. 检查止损事件
        stoploss_events = check_stoploss_events(account_id)
        
        # 3. 处理止损事件
        for event in stoploss_events:
            if event.type == 'long' and config.type == 'long_stoploss_reverse':
                # 多单止损，反手开空
                if config.enabled and config.allow_trigger:
                    execute_reverse_strategy(account_id, strategy_code)
                    update_trigger_permission(account_id, config_id, False)
                    log_trigger_event(...)
            
            elif event.type == 'short' and config.type == 'short_stoploss_reverse':
                # 空单止损，反手开多
                if config.enabled and config.allow_trigger:
                    execute_reverse_strategy(account_id, strategy_code)
                    update_trigger_permission(account_id, config_id, False)
                    log_trigger_event(...)
    
    time.sleep(CHECK_INTERVAL)
```

#### 监控参数
- **检查间隔**：60秒
- **监控账户**：account_main, account_fangfang12, account_anchor, account_poit, account_poit_main, account_dadanini
- **日志级别**：INFO
- **内存限制**：300MB

---

## 📁 数据存储

### 配置文件
```
data/stoploss_reverse_orders/
├── account_main_stoploss_reverse.jsonl
├── account_fangfang12_stoploss_reverse.jsonl
├── account_anchor_stoploss_reverse.jsonl
├── account_poit_stoploss_reverse.jsonl
├── account_poit_main_stoploss_reverse.jsonl
└── account_dadanini_stoploss_reverse.jsonl
```

### 触发事件日志
```
data/stoploss_reverse_orders/trigger_events/
├── account_main_trigger_events_20260302.jsonl
├── account_main_trigger_events_20260303.jsonl
└── ...
```

### 监控日志
```
data/stoploss_reverse_orders/logs/
├── monitor_20260302.log
├── monitor_20260303.log
└── ...
```

### JSONL格式示例

#### 配置文件格式
```json
{
  "id": "reverse_long_stoploss",
  "type": "long_stoploss_reverse",
  "name": "多单止损反手开空",
  "description": "多单止损后自动反手开空单",
  "enabled": true,
  "allow_trigger": true,
  "target_strategy_code": "STG_SHORT_TOP8",
  "triggered_count": 2,
  "last_triggered_at": "2026-03-02 15:45:12",
  "created_at": "2026-03-02 15:29:42",
  "updated_at": "2026-03-02 15:45:12"
}
```

#### 触发事件格式
```json
{
  "timestamp": "2026-03-02 15:45:12",
  "account_id": "account_main",
  "config_id": "reverse_long_stoploss",
  "config_type": "long_stoploss_reverse",
  "strategy_code": "STG_SHORT_TOP8",
  "result": {
    "success": true,
    "message": "执行策略 STG_SHORT_TOP8",
    "orders": [...]
  },
  "success": true
}
```

---

## 🚀 部署与运维

### PM2配置 (ecosystem.config.js)

```javascript
{
  name: 'stoploss-reverse-monitor',
  script: 'monitors/stoploss_reverse_monitor.py',
  interpreter: 'python3',
  cwd: '/home/user/webapp',
  autorestart: true,
  watch: false,
  max_memory_restart: '300M',
  env: {
    PYTHONPATH: '/home/user/webapp'
  },
  error_file: '/home/user/webapp/logs/stoploss-reverse-error.log',
  out_file: '/home/user/webapp/logs/stoploss-reverse-out.log',
  log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
}
```

### 启动监控器
```bash
pm2 start ecosystem.config.js --only stoploss-reverse-monitor
```

### 停止监控器
```bash
pm2 stop stoploss-reverse-monitor
```

### 重启监控器
```bash
pm2 restart stoploss-reverse-monitor
```

### 查看日志
```bash
# 实时日志
pm2 logs stoploss-reverse-monitor

# 最近20行
pm2 logs stoploss-reverse-monitor --lines 20 --nostream
```

### 查看状态
```bash
pm2 status stoploss-reverse-monitor
```

---

## 🧪 测试

### 测试API

#### 获取配置
```bash
curl -X GET "http://localhost:9002/api/okx-trading/stoploss-reverse-orders/account_main" \
  -H "Content-Type: application/json"
```

#### 更新配置
```bash
curl -X POST "http://localhost:9002/api/okx-trading/stoploss-reverse-orders/account_main" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "reverse_long_stoploss",
    "enabled": true,
    "target_strategy_code": "STG_SHORT_TOP8"
  }'
```

#### 重置触发权限
```bash
curl -X POST "http://localhost:9002/api/okx-trading/stoploss-reverse-orders/account_main/reverse_long_stoploss/reset-trigger" \
  -H "Content-Type: application/json"
```

### 前端测试

1. 访问 OKX Trading 页面
2. 找到 "🔄 止损反手开单" 面板
3. 启用多单止损反手开空
4. 选择目标策略（涨幅前8名做空）
5. 查看触发权限状态
6. 触发后点击重置按钮

---

## 📊 使用场景

### 场景1：趋势反转保护
- **情况**：持有多单，市场突然反转
- **触发**：多单止损
- **反手**：自动开空单（选择涨幅前8名做空）
- **目的**：减少损失，同时捕捉下跌趋势

### 场景2：震荡市场对冲
- **情况**：市场震荡，频繁触发止损
- **触发**：空单止损
- **反手**：自动开多单（选择涨幅后8名做多，抄底）
- **目的**：在震荡中捕捉反弹机会

### 场景3：风险控制
- **情况**：单边行情，连续止损
- **触发**：第一次止损后反手
- **保护**：触发后禁用，防止连续反手导致更大损失
- **操作**：人工判断后重置权限

---

## ⚠️ 注意事项

### 1. 防重复触发
- ✅ 触发后 `allow_trigger` 自动设置为 `false`
- ✅ 必须手动点击重置按钮才能再次触发
- ⚠️ 避免在极端行情下连续反手导致损失放大

### 2. 策略选择
- 🎯 **涨幅前8名**：适合强势突破或反转行情
- 🎯 **涨幅后8名**：适合抄底或震荡行情
- ⚠️ 根据市场情况选择合适的策略

### 3. 监控器状态
- ✅ 确保监控器正常运行（`pm2 status`）
- ✅ 定期查看日志确认无异常
- ⚠️ 监控器停止将无法自动触发反手

### 4. 数据完整性
- ✅ 配置存储在JSONL文件，支持备份
- ✅ 触发事件完整记录，可追溯
- ⚠️ 不要手动修改JSONL文件，使用API更新

---

## 🔗 访问地址

- **OKX Trading 页面**：https://9002-id51ob5t89zrt4phphxq8-5634da27.sandbox.novita.ai/okx-trading
- **API Base URL**：https://9002-id51ob5t89zrt4phphxq8-5634da27.sandbox.novita.ai/api/okx-trading/

---

## 📝 更新日志

### v1.0.0 (2026-03-02)
- ✅ 实现止损反手API endpoints
- ✅ 添加前端UI（多单/空单反手卡片）
- ✅ 实现防重复触发机制
- ✅ 添加止损反手监控器
- ✅ 集成PM2自动管理
- ✅ 完整的日志记录系统
- ✅ 多账户独立运行

---

## 🔮 后续计划

### 待实现功能
1. **实际止损检测**
   - 集成OKX API获取止损订单
   - 读取本地止损日志
   - 监听止损通知（WebSocket）

2. **策略执行**
   - 调用现有策略执行函数
   - 支持自定义开仓参数（杠杆、仓位大小）
   - 支持批量开仓

3. **高级配置**
   - 设置触发次数上限
   - 设置时间窗口限制
   - 支持条件组合（如：仅在特定时间段触发）

4. **Telegram通知**
   - 触发时发送通知
   - 执行结果推送
   - 异常告警

5. **统计分析**
   - 反手成功率
   - 盈亏统计
   - 策略效果对比

---

## 🤝 支持

如有问题或建议，请联系开发团队。
