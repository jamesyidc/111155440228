# 27币涨跌幅止盈止损系统 - 激活文档

**日期**: 2026-03-02  
**操作**: 激活已有的27币涨跌幅之和止盈止损功能  
**状态**: ✅ 已完成并运行

---

## 📋 系统概述

### 功能说明

27币涨跌幅止盈止损系统是一个基于27个主流币种涨跌幅之和的自动止盈系统：

- **空单止盈**: 当27币涨跌幅之和跌破设定阈值时自动平仓止盈
  - 触发条件: `total_change < -threshold` (负值跌破)
  - 示例: 阈值设为10%，当涨跌幅之和为-11%时触发

- **多单止盈**: 当27币涨跌幅之和突破设定阈值时自动平仓止盈
  - 触发条件: `total_change > threshold` (正值突破)
  - 示例: 阈值设为15%，当涨跌幅之和为16%时触发

### 系统特点

1. **独立账户配置**: 每个交易账户独立配置JSONL文件
2. **开关控制**: 空单和多单止盈独立启用/禁用
3. **防重复执行**: 每个持仓只执行一次止盈，记录在execution文件中
4. **实时监控**: 每30秒检查一次持仓和市场数据
5. **Telegram通知**: 平仓成功后发送通知

---

## 🔧 系统组件

### 1. 监控服务

**文件**: `source_code/okx_coin_change_tpsl_monitor.py`

**功能**:
- 读取账户配置和止盈阈值
- 获取最新27币涨跌幅之和数据
- 检查持仓并判断是否触发止盈
- 执行平仓操作
- 记录执行结果
- 发送Telegram通知

**监控间隔**: 30秒

### 2. 配置文件

**位置**: `data/okx_tpsl_settings/`

**格式**: JSONL (第一行为配置)

**示例** (`account_main_coin_change_tpsl.jsonl`):
```json
{
  "account_id": "account_main",
  "shortTakeProfitEnabled": true,
  "shortTakeProfitThreshold": 10.0,
  "longTakeProfitEnabled": true,
  "longTakeProfitThreshold": 15.0,
  "last_updated": "2026-03-02 03:55:20",
  "comment": "27币涨跌幅止盈配置 - 空单跌破止盈/多单突破止盈"
}
```

**字段说明**:
- `shortTakeProfitEnabled`: 空单止盈开关 (true/false)
- `shortTakeProfitThreshold`: 空单止盈阈值 (正数，实际触发时为负值)
- `longTakeProfitEnabled`: 多单止盈开关 (true/false)
- `longTakeProfitThreshold`: 多单止盈阈值 (正数)
- `last_updated`: 最后更新时间
- `comment`: 配置说明

### 3. 执行记录文件

**位置**: `data/okx_tpsl_settings/`

**格式**: JSONL (每次执行追加一行)

**示例** (`account_main_coin_change_tpsl_execution.jsonl`):
```json
{
  "timestamp": "2026-03-02T12:30:15.123456",
  "account_id": "account_main",
  "instId": "BTC-USDT-SWAP",
  "posSide": "short",
  "triggerType": "short_take_profit",
  "totalChange": -11.5,
  "threshold": 10.0,
  "success": true,
  "message": "平仓成功",
  "error": ""
}
```

### 4. 数据源

**位置**: `data/coin_change_tracker/coin_change_YYYYMMDD.jsonl`

**数据结构**:
```json
{
  "timestamp": 1772425828982,
  "beijing_time": "2026-03-02 12:30:16",
  "total_change": 3.25,
  "up_coins": 12,
  "down_coins": 15,
  "changes": {...}
}
```

**数据更新**: 实时采集，约每分钟更新

### 5. Web UI

**路由**: `/okx-coin-change-tpsl`

**访问地址**: https://9002-id51ob5t89zrt4phphxq8-5634da27.sandbox.novita.ai/okx-coin-change-tpsl

**功能**:
- 查看当前27币涨跌幅之和
- 配置各账户止盈参数
- 启用/禁用止盈功能
- 查看配置历史

### 6. API接口

#### 获取配置
```bash
GET /api/okx-trading/coin-change-tpsl-settings/<account_id>
```

**响应示例**:
```json
{
  "success": true,
  "exists": true,
  "settings": {
    "account_id": "account_main",
    "shortTakeProfitEnabled": true,
    "shortTakeProfitThreshold": 10.0,
    "longTakeProfitEnabled": true,
    "longTakeProfitThreshold": 15.0,
    "last_updated": "2026-03-02 03:55:20"
  }
}
```

#### 更新配置
```bash
POST /api/okx-trading/coin-change-tpsl-settings/<account_id>
Content-Type: application/json

{
  "shortTakeProfitEnabled": true,
  "shortTakeProfitThreshold": 10.0,
  "longTakeProfitEnabled": true,
  "longTakeProfitThreshold": 15.0
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "27币涨跌幅止盈配置已更新",
  "settings": {
    "shortTakeProfitEnabled": true,
    "shortTakeProfitThreshold": 10.0,
    "longTakeProfitEnabled": true,
    "longTakeProfitThreshold": 15.0
  }
}
```

#### 获取状态
```bash
GET /api/okx-trading/coin-change-tpsl-status/<account_id>
```

---

## 🚀 本次操作记录

### 操作时间
2026-03-02 12:32 (北京时间)

### 发现问题
用户反馈止盈止损系统需要添加"27币涨跌幅之和止盈"功能。

### 调查结果
1. ✅ 系统已完整实现 (`okx_coin_change_tpsl_monitor.py`)
2. ✅ API端点已配置 (`/api/okx-trading/coin-change-tpsl-settings/`)
3. ✅ Web UI已存在 (`/okx-coin-change-tpsl`)
4. ✅ PM2配置文件已包含监控服务
5. ❌ **问题**: PM2监控服务未启动

### 解决方案
启动所有账户的coin-change-tpsl监控服务：

```bash
# 启动监控服务
pm2 start source_code/okx_coin_change_tpsl_monitor.py --name okx-coin-change-tpsl-main --interpreter python3 -- account_main
pm2 start source_code/okx_coin_change_tpsl_monitor.py --name okx-coin-change-tpsl-fangfang12 --interpreter python3 -- account_fangfang12
pm2 start source_code/okx_coin_change_tpsl_monitor.py --name okx-coin-change-tpsl-poit --interpreter python3 -- account_poit
pm2 start source_code/okx_coin_change_tpsl_monitor.py --name okx-coin-change-tpsl-poit-main --interpreter python3 -- account_poit_main
pm2 start source_code/okx_coin_change_tpsl_monitor.py --name okx-coin-change-tpsl-anchor --interpreter python3 -- account_anchor

# 保存PM2配置
pm2 save
```

### 验证结果

```bash
# 检查服务状态
pm2 list | grep coin-change-tpsl
```

**输出**:
```
│ 33 │ okx-coin-change-tpsl-main       │ ... │ online │
│ 34 │ okx-coin-change-tpsl-fangfang12 │ ... │ online │
│ 35 │ okx-coin-change-tpsl-poit       │ ... │ online │
│ 36 │ okx-coin-change-tpsl-poit-main  │ ... │ online │
│ 37 │ okx-coin-change-tpsl-anchor     │ ... │ online │
```

**日志验证** (`account_main`):
```
✅ Telegram已配置
[account_main] 🚀 启动27币涨跌幅止盈监控
[account_main] 📊 监控间隔: 30秒
[account_main] 📊 当前27币涨跌幅之和: 3.25% (时间: 2026-03-02 12:30:16)
[account_main] ℹ️  当前无持仓
```

**API测试**:
```bash
curl "http://localhost:9002/api/okx-trading/coin-change-tpsl-settings/account_main"
```

**输出**:
```json
{
  "success": true,
  "exists": true,
  "settings": {
    "account_id": "account_main",
    "shortTakeProfitEnabled": true,
    "shortTakeProfitThreshold": 10.0,
    "longTakeProfitEnabled": true,
    "longTakeProfitThreshold": 15.0,
    "last_updated": "2026-03-02 03:55:20",
    "comment": "27币涨跌幅止盈配置 - 空单跌破止盈/多单突破止盈"
  }
}
```

---

## 📊 当前配置状态

### 已激活的账户

| 账户 | 空单止盈 | 空单阈值 | 多单止盈 | 多单阈值 | 监控状态 |
|------|----------|----------|----------|----------|----------|
| account_main | ✅ 启用 | -10% | ✅ 启用 | +15% | 🟢 运行中 |
| account_fangfang12 | - | - | - | - | 🟢 运行中 |
| account_poit | - | - | - | - | 🟢 运行中 |
| account_poit_main | - | - | - | - | 🟢 运行中 |
| account_anchor | - | - | - | - | 🟢 运行中 |

### 当前市场数据

**27币涨跌幅之和**: +3.25%  
**更新时间**: 2026-03-02 12:30:16 (北京时间)  
**上涨币种**: 12  
**下跌币种**: 15

---

## 🎯 使用指南

### 配置止盈参数

#### 方法1: 通过Web UI
1. 访问 https://9002-id51ob5t89zrt4phphxq8-5634da27.sandbox.novita.ai/okx-coin-change-tpsl
2. 选择账户
3. 设置空单/多单止盈开关
4. 输入止盈阈值
5. 点击"保存配置"

#### 方法2: 通过API
```bash
curl -X POST "http://localhost:9002/api/okx-trading/coin-change-tpsl-settings/account_main" \
  -H "Content-Type: application/json" \
  -d '{
    "shortTakeProfitEnabled": true,
    "shortTakeProfitThreshold": 10.0,
    "longTakeProfitEnabled": true,
    "longTakeProfitThreshold": 15.0
  }'
```

### 查看执行记录

```bash
# 查看执行记录
tail -f data/okx_tpsl_settings/account_main_coin_change_tpsl_execution.jsonl

# 查看监控日志
pm2 logs okx-coin-change-tpsl-main --nostream --lines 50
```

### 停止/重启监控

```bash
# 停止监控
pm2 stop okx-coin-change-tpsl-main

# 重启监控
pm2 restart okx-coin-change-tpsl-main

# 查看状态
pm2 list | grep coin-change-tpsl
```

---

## 🔍 监控逻辑详解

### 检查流程

1. **加载配置**: 读取JSONL配置文件第一行
2. **检查开关**: 验证空单/多单止盈是否启用
3. **获取数据**: 读取最新27币涨跌幅之和
4. **获取持仓**: 调用OKX API获取当前持仓
5. **判断触发**: 
   - 空单: `total_change < -threshold`
   - 多单: `total_change > threshold`
6. **检查执行记录**: 确保不重复执行
7. **执行平仓**: 调用OKX平仓API
8. **记录结果**: 写入execution JSONL
9. **发送通知**: Telegram通知平仓结果

### 触发示例

#### 空单止盈场景
- **持仓**: BTC-USDT-SWAP 空单
- **配置**: 阈值 = 10%，启用
- **市场**: 27币涨跌幅之和 = -11%
- **判断**: -11% < -10% ✅ 触发
- **动作**: 平空单 → 记录 → 通知

#### 多单止盈场景
- **持仓**: ETH-USDT-SWAP 多单
- **配置**: 阈值 = 15%，启用
- **市场**: 27币涨跌幅之和 = +16%
- **判断**: +16% > +15% ✅ 触发
- **动作**: 平多单 → 记录 → 通知

---

## 📝 注意事项

### 1. 阈值设置建议
- **空单阈值**: 建议 5-15%，根据市场波动调整
- **多单阈值**: 建议 10-20%，根据市场波动调整
- **原则**: 阈值过小→频繁触发，阈值过大→止盈滞后

### 2. 监控频率
- 当前: 30秒检查一次
- 数据延迟: 约1分钟
- 极端波动: 可能有30-90秒反应延迟

### 3. 防重复机制
- 每个持仓只执行一次止盈
- execution文件记录所有执行
- 重启服务不影响防重复逻辑

### 4. 开关控制
- 空单和多单止盈独立控制
- 可以只启用其中一个
- 配置即时生效（30秒内）

### 5. 故障恢复
- 服务崩溃自动重启（PM2 autorestart）
- 配置持久化在JSONL文件
- 执行记录不会丢失

---

## 🛠️ 故障排查

### 问题1: 服务未启动
```bash
# 检查状态
pm2 list | grep coin-change-tpsl

# 如果不存在，启动服务
pm2 start source_code/okx_coin_change_tpsl_monitor.py --name okx-coin-change-tpsl-main --interpreter python3 -- account_main
```

### 问题2: 配置未生效
```bash
# 检查配置文件
cat data/okx_tpsl_settings/account_main_coin_change_tpsl.jsonl | head -1 | jq

# 重启服务使配置生效
pm2 restart okx-coin-change-tpsl-main
```

### 问题3: 数据获取失败
```bash
# 检查数据文件是否存在
ls -lh data/coin_change_tracker/coin_change_$(date -d '+8 hours' +%Y%m%d).jsonl

# 查看最新数据
tail -1 data/coin_change_tracker/coin_change_$(date -d '+8 hours' +%Y%m%d).jsonl | jq
```

### 问题4: 平仓失败
```bash
# 查看执行记录
tail -10 data/okx_tpsl_settings/account_main_coin_change_tpsl_execution.jsonl | jq

# 查看详细日志
pm2 logs okx-coin-change-tpsl-main --lines 100 | grep -i error
```

---

## 📞 系统集成

### 与其他止盈系统的关系

| 系统 | 触发条件 | 监控服务 | 配置文件 |
|------|----------|----------|----------|
| **币种涨跌幅止盈** | 27币涨跌幅之和 | okx-coin-change-tpsl-* | *_coin_change_tpsl.jsonl |
| 百分比止盈止损 | 持仓保证金百分比 | okx-percent-tpsl-monitor | *_percent_tpsl.jsonl |
| 固定价格止盈止损 | 固定价格触发 | okx-tpsl-monitor | *_tpsl.jsonl |
| RSI止盈 | RSI指标 | rsi-takeprofit-monitor | - |

**注意**: 各系统独立运行，可同时启用

---

## ✅ 总结

### 完成情况
- ✅ 系统代码已完整实现
- ✅ API端点已配置并测试
- ✅ Web UI已部署可访问
- ✅ PM2监控服务已启动（5个账户）
- ✅ 配置文件已就绪
- ✅ 数据采集正常运行

### 当前状态
- 🟢 5个账户监控服务全部运行中
- 🟢 API端点正常响应
- 🟢 Web UI可访问配置
- 🟢 数据采集实时更新
- 🟢 Telegram通知已配置

### 下一步建议
1. 根据实际交易策略调整各账户的止盈阈值
2. 监控执行记录，优化阈值设置
3. 定期查看日志，确保服务稳定运行
4. 根据市场波动调整检查频率（如需要）

---

**文档创建**: 2026-03-02 12:32  
**系统版本**: 2026-03-02  
**作者**: AI Assistant  
**状态**: ✅ 生产环境运行中
