# 0点0分对冲底仓系统文档

## 📋 系统概述

### 功能描述
每天北京时间 **00:00:00** 自动执行对冲底仓策略：
- 📈 开一份多单（底仓）
- 📉 开一份空单（对冲）
- 💰 分别跟踪盈亏情况
- 📊 记录到JSONL文件

### 核心特性
- ✅ 账户独立配置
- ✅ 策略自由选择（下拉菜单）
- ✅ 自动执行（无需人工干预）
- ✅ 盈亏独立跟踪
- ✅ 完整执行记录
- ✅ 防重复触发（每天仅执行一次）

## 🎯 使用场景

### 对冲策略优势
1. **风险对冲**：多空同时持仓，降低单边风险
2. **波动获利**：无论涨跌，总有一边盈利
3. **底仓布局**：每日自动建仓，积累底仓
4. **灵活策略**：可选择不同策略组合

### 适用人群
- 长期投资者
- 风险厌恶者
- 定投策略用户
- 波段交易者

## 🔧 系统架构

### 1. 监控器
**文件**：`monitors/midnight_hedge_monitor.py`

**功能**：
- 每30秒检查当前时间
- 在 00:00:00 执行对冲开单
- 记录执行结果
- 初始化盈亏记录

**执行条件**（同时满足）：
1. ✅ 已启用开关（`enabled = true`）
2. ✅ 已选择多单策略（`long_strategy_code` 非空）
3. ✅ 已选择空单策略（`short_strategy_code` 非空）
4. ✅ 今天尚未执行过

**防重复机制**：
- 创建执行标记文件：`executed_{YYYYMMDD}.flag`
- 检测到标记文件时跳过执行

### 2. API端点

#### 2.1 获取配置
```
GET /api/okx-trading/midnight-hedge/<account_id>
```

**响应示例**：
```json
{
    "success": true,
    "config": {
        "account_id": "account_main",
        "enabled": true,
        "long_strategy_code": "STG_LONG_BOTTOM8",
        "short_strategy_code": "STG_SHORT_TOP8",
        "execution_time": "00:00:00",
        "created_at": "2026-03-03 11:30:21",
        "updated_at": "2026-03-03 11:30:21"
    },
    "timestamp": "2026-03-03 11:30:21"
}
```

#### 2.2 更新配置
```
POST /api/okx-trading/midnight-hedge/<account_id>
Content-Type: application/json

{
    "enabled": true,
    "long_strategy_code": "STG_LONG_BOTTOM8",
    "short_strategy_code": "STG_SHORT_TOP8"
}
```

**响应示例**：
```json
{
    "success": true,
    "message": "配置已更新",
    "config": { ... },
    "timestamp": "2026-03-03 11:30:21"
}
```

#### 2.3 获取执行记录
```
GET /api/okx-trading/midnight-hedge/<account_id>/execution-records?date=20260303
```

**响应示例**：
```json
{
    "success": true,
    "records": [
        {
            "account_id": "account_main",
            "execution_time": "2026-03-03 00:00:05",
            "date": "20260303",
            "long_order": {
                "success": true,
                "order_id": "HEDGE_20260303_LONG_account_main",
                "strategy_code": "STG_LONG_BOTTOM8",
                "side": "long",
                "entry_price": 100.0,
                "quantity": 1.0,
                "timestamp": "2026-03-03 00:00:05"
            },
            "short_order": {
                "success": true,
                "order_id": "HEDGE_20260303_SHORT_account_main",
                "strategy_code": "STG_SHORT_TOP8",
                "side": "short",
                "entry_price": 100.0,
                "quantity": 1.0,
                "timestamp": "2026-03-03 00:00:06"
            },
            "both_success": true
        }
    ],
    "count": 1,
    "date": "20260303"
}
```

#### 2.4 获取盈亏记录
```
GET /api/okx-trading/midnight-hedge/<account_id>/pnl-records?date=20260303
```

**响应示例**：
```json
{
    "success": true,
    "records": [ ... ],
    "long_records": [ ... ],
    "short_records": [ ... ],
    "stats": {
        "long_pnl": 50.25,
        "short_pnl": -20.10,
        "total_pnl": 30.15,
        "long_count": 1,
        "short_count": 1
    },
    "date": "20260303"
}
```

### 3. 数据存储

#### 3.1 配置文件
**路径**：`data/midnight_hedge_orders/{account_id}_hedge_config.jsonl`

**格式**：
```json
{
    "account_id": "account_main",
    "enabled": true,
    "long_strategy_code": "STG_LONG_BOTTOM8",
    "short_strategy_code": "STG_SHORT_TOP8",
    "execution_time": "00:00:00",
    "created_at": "2026-03-03 00:00:00",
    "updated_at": "2026-03-03 12:00:00"
}
```

#### 3.2 执行记录
**路径**：`data/midnight_hedge_orders/execution_records/{account_id}_executions_{YYYYMMDD}.jsonl`

**格式**：见 API 2.3 示例

#### 3.3 盈亏记录
**路径**：`data/midnight_hedge_orders/pnl_records/{account_id}_pnl_{YYYYMMDD}.jsonl`

**格式**：
```json
{
    "account_id": "account_main",
    "order_id": "HEDGE_20260303_LONG_account_main",
    "side": "long",
    "strategy_code": "STG_LONG_BOTTOM8",
    "entry_time": "2026-03-03 00:00:05",
    "entry_price": 100.0,
    "quantity": 1.0,
    "current_price": 105.0,
    "unrealized_pnl": 50.0,
    "unrealized_pnl_percent": 5.0,
    "last_updated": "2026-03-03 12:00:00"
}
```

#### 3.4 执行标记
**路径**：`data/midnight_hedge_orders/executed_{YYYYMMDD}.flag`

**作用**：防止重复执行，每天自动创建

#### 3.5 日志文件
**路径**：`data/midnight_hedge_orders/logs/monitor_{YYYYMMDD}.log`

**内容**：
- 监控器启动信息
- 配置检查结果
- 执行过程详情
- 错误信息（如有）

## 🎨 前端界面

### UI组件

#### 1. 启用开关
```
🔵 启用自动开单 [开关]
```

#### 2. 工作原理说明
```
💡 工作原理
每天北京时间 00:00:00 自动执行：
1️⃣ 开一份多单（底仓）
2️⃣ 开一份空单（对冲）
分别跟踪盈亏，记录到JSONL文件
```

#### 3. 策略选择（双列布局）
```
┌─────────────────────┬─────────────────────┐
│ 🟢 多单策略         │ 🔴 空单策略         │
├─────────────────────┼─────────────────────┤
│ [下拉选择]          │ [下拉选择]          │
│ - 涨幅前8名做多     │ - 涨幅前8名做空     │
│ - 涨幅后8名做多     │ - 涨幅后8名做空     │
└─────────────────────┴─────────────────────┘
```

#### 4. 今日执行记录
```
📊 今日执行记录
┌─────────────┬─────────────┐
│ 多单 🟢     │ 空单 🔴     │
│ ✅ 已执行   │ ✅ 已执行   │
│ (订单ID)    │ (订单ID)    │
└─────────────┴─────────────┘
```

#### 5. 盈亏统计
```
💰 今日盈亏
┌──────────┬──────────┬──────────┐
│ 多单盈亏 │ 空单盈亏 │ 总盈亏   │
│ +50.25   │ -20.10   │ +30.15   │
└──────────┴──────────┴──────────┘
```

### JavaScript函数

```javascript
// 加载配置
async function loadMidnightHedgeConfig()

// 显示配置
function displayMidnightHedgeConfig(config)

// 切换启用状态
async function toggleMidnightHedge(enabled)

// 保存配置
async function saveMidnightHedgeSettings()

// 加载执行记录和盈亏
async function loadMidnightHedgeRecords()
```

## 📊 策略选项

### 多单策略
| 代码 | 名称 | 描述 |
|------|------|------|
| `STG_LONG_TOP8` | 涨幅前8名做多 | 对涨幅前8名币种开多单 |
| `STG_LONG_BOTTOM8` | 涨幅后8名做多（抄底） | 对涨幅后8名币种开多单 |

### 空单策略
| 代码 | 名称 | 描述 |
|------|------|------|
| `STG_SHORT_TOP8` | 涨幅前8名做空 | 对涨幅前8名币种开空单 |
| `STG_SHORT_BOTTOM8` | 涨幅后8名做空 | 对涨幅后8名币种开空单 |

### 策略组合建议

#### 组合1：追涨与防跌
- **多单**：涨幅前8名做多（追涨）
- **空单**：涨幅前8名做空（对冲）
- **适用**：强势市场

#### 组合2：抄底与对冲
- **多单**：涨幅后8名做多（抄底）
- **空单**：涨幅前8名做空（对冲）
- **适用**：震荡市场

#### 组合3：均衡配置
- **多单**：涨幅后8名做多（抄底）
- **空单**：涨幅后8名做空（跟随弱势）
- **适用**：弱势市场

## 🚀 部署配置

### PM2配置
**文件**：`ecosystem.config.js`

```javascript
{
  name: 'midnight-hedge-monitor',
  script: 'monitors/midnight_hedge_monitor.py',
  interpreter: 'python3',
  cwd: '/home/user/webapp',
  autorestart: true,
  watch: false,
  max_memory_restart: '300M',
  env: {
    PYTHONPATH: '/home/user/webapp'
  },
  error_file: '/home/user/webapp/logs/midnight-hedge-error.log',
  out_file: '/home/user/webapp/logs/midnight-hedge-out.log',
  log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
}
```

### 启动服务
```bash
# 启动监控器
pm2 start ecosystem.config.js --only midnight-hedge-monitor

# 查看状态
pm2 status midnight-hedge-monitor

# 查看日志
pm2 logs midnight-hedge-monitor --lines 50

# 重启服务
pm2 restart midnight-hedge-monitor
```

## 🔍 监控与日志

### 查看运行状态
```bash
pm2 status midnight-hedge-monitor
```

**预期输出**：
```
│ 40 │ midnight-hedge-monitor │ online │ 0s │ 27.5mb │
```

### 查看实时日志
```bash
pm2 logs midnight-hedge-monitor --lines 20
```

**日志示例**：
```
🚀 0点0分对冲底仓监控器启动
📊 检查间隔: 30秒
👥 监控账户: account_main, account_fangfang12, ...
⏰ 执行时间: 每天北京时间 00:00:00
```

### 检查配置文件
```bash
cat data/midnight_hedge_orders/account_main_hedge_config.jsonl
```

### 检查执行记录
```bash
cat data/midnight_hedge_orders/execution_records/account_main_executions_20260303.jsonl
```

### 检查盈亏记录
```bash
cat data/midnight_hedge_orders/pnl_records/account_main_pnl_20260303.jsonl
```

## 📝 使用流程

### 快速启动（3步）
1. **打开启用开关**
2. **选择多单策略**（如：涨幅后8名做多）
3. **选择空单策略**（如：涨幅前8名做空）

✅ 完成！系统将在今晚 00:00 自动执行

### 详细步骤

#### 步骤1：访问页面
访问：https://9002-id51ob5t89zrt4phphxq8-5634da27.sandbox.novita.ai/okx-trading

#### 步骤2：选择账户
在顶部账户选择器中选择目标账户

#### 步骤3：找到"0点0分对冲底仓"卡片
滚动到页面中部，找到蓝色渐变卡片

#### 步骤4：启用开关
打开"🔵 启用自动开单"开关

#### 步骤5：选择策略
- **多单策略**：选择 `STG_LONG_BOTTOM8`（涨幅后8名做多）
- **空单策略**：选择 `STG_SHORT_TOP8`（涨幅前8名做空）

#### 步骤6：等待执行
- 系统将在今晚 00:00:00 自动执行
- 第二天查看"今日执行记录"和"今日盈亏"

## ⚠️ 注意事项

### 1. 账户余额
确保账户有足够余额执行两笔订单（多单+空单）

### 2. 执行时间
- **北京时间 00:00:00** 执行
- **每天仅执行一次**
- 防重复机制确保不会重复开单

### 3. 策略选择
- 必须同时选择多单和空单策略
- 缺少任一策略时不会执行

### 4. 监控器状态
```bash
pm2 status midnight-hedge-monitor
```
确保状态为 `online`

### 5. 数据文件
- 配置文件：JSONL格式，单行
- 执行记录：每天一个文件
- 盈亏记录：每天一个文件
- 日志文件：每天一个文件（北京时间）

## 🐛 故障排查

### 问题1：监控器未启动
**检查**：
```bash
pm2 status midnight-hedge-monitor
```

**解决**：
```bash
pm2 start ecosystem.config.js --only midnight-hedge-monitor
```

### 问题2：未执行开单
**检查**：
1. 是否启用开关？
2. 是否选择策略？
3. 是否已执行过（检查标记文件）？

**日志**：
```bash
pm2 logs midnight-hedge-monitor --lines 100
```

### 问题3：盈亏不显示
**检查**：
- 是否有执行记录？
- 是否有盈亏记录？
- 前端是否正确加载？

**API测试**：
```bash
curl -s "http://localhost:9002/api/okx-trading/midnight-hedge/account_main/pnl-records"
```

### 问题4：时区问题
**说明**：系统使用北京时间（UTC+8）

**验证**：
```bash
python3 -c "from utils.beijing_time import get_beijing_now_str; print(get_beijing_now_str())"
```

## 📊 统计与分析

### 每日盈亏统计
```bash
# 查看今日盈亏
curl -s "http://localhost:9002/api/okx-trading/midnight-hedge/account_main/pnl-records" | python3 -m json.tool

# 提取统计数据
curl -s "http://localhost:9002/api/okx-trading/midnight-hedge/account_main/pnl-records" | python3 -c "import json, sys; data=json.load(sys.stdin); print(f'多单: {data[\"stats\"][\"long_pnl\"]}, 空单: {data[\"stats\"][\"short_pnl\"]}, 总计: {data[\"stats\"][\"total_pnl\"]}')"
```

### 历史执行记录
```bash
# 查看指定日期
curl -s "http://localhost:9002/api/okx-trading/midnight-hedge/account_main/execution-records?date=20260303"
```

## 🔗 相关文档

- `TIMEZONE_FIX_DOCUMENTATION.md` - 时区修复文档
- `STOPLOSS_REVERSE_SYSTEM.md` - 止损反手系统文档
- `COIN_CHANGE_CONDITIONAL_ORDER_SYSTEM.md` - 27币条件单系统文档

## 📈 未来改进

### 计划功能
1. **实时盈亏更新**：定时刷新当前盈亏
2. **多期统计**：周度、月度盈亏统计
3. **策略优化**：基于历史数据推荐策略
4. **风险提醒**：余额不足时Telegram通知
5. **手动平仓**：提供手动平仓功能

### 扩展方向
1. **多时段执行**：支持自定义执行时间
2. **动态仓位**：根据行情调整仓位
3. **智能策略**：AI选择最优策略组合
4. **绩效分析**：详细的绩效报告

## 🎓 使用建议

### 新手建议
1. 先用小仓位测试
2. 观察一周数据
3. 调整策略组合
4. 逐步增加仓位

### 高级建议
1. 结合市场情绪
2. 定期回顾数据
3. 优化策略组合
4. 设置止盈止损

## 📞 技术支持

### 日志路径
- PM2日志：`logs/midnight-hedge-out.log`
- 监控器日志：`data/midnight_hedge_orders/logs/monitor_{date}.log`

### 数据路径
- 配置：`data/midnight_hedge_orders/{account}_hedge_config.jsonl`
- 执行记录：`data/midnight_hedge_orders/execution_records/`
- 盈亏记录：`data/midnight_hedge_orders/pnl_records/`

### PM2命令
```bash
pm2 status          # 查看状态
pm2 logs           # 查看日志
pm2 restart        # 重启服务
pm2 stop           # 停止服务
pm2 delete         # 删除服务
```

---

**系统版本**：v1.0.0  
**最后更新**：2026-03-03  
**作者**：OKX Trading Team  
**Git提交**：212f92d
