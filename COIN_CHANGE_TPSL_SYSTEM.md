# 27币涨跌幅止盈系统

## 功能概述

基于27个主流币种涨跌幅之和的自动止盈系统，支持空单和多单两种方向的止盈触发。

### 特性

- ✅ **空单止盈（跌破止盈）**: 当27币涨跌幅之和跌破设定阈值时，自动平掉所有空单持仓
- ✅ **多单止盈（突破止盈）**: 当27币涨跌幅之和突破设定阈值时，自动平掉所有多单持仓
- ✅ **账户独立配置**: 每个交易账户独立配置JSONL文件
- ✅ **开关控制**: 每个方向都有独立的启用/禁用开关
- ✅ **防重复执行**: 每个持仓只会执行一次止盈，记录在execution文件中
- ✅ **Telegram通知**: 止盈成功后自动发送Telegram通知

## 系统架构

### 1. 监控脚本

`source_code/okx_coin_change_tpsl_monitor.py`

- 每30秒检查一次27币涨跌幅数据
- 根据配置判断是否触发止盈条件
- 调用OKX API平仓
- 记录执行结果
- 发送Telegram通知

### 2. 配置存储

每个账户一个JSONL配置文件：

```
data/okx_tpsl_settings/
├── account_main_coin_change_tpsl.jsonl
├── account_fangfang12_coin_change_tpsl.jsonl
├── account_poit_coin_change_tpsl.jsonl
├── account_poit_main_coin_change_tpsl.jsonl
└── account_anchor_coin_change_tpsl.jsonl
```

**JSONL格式示例**:
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

### 3. 执行记录

每个账户一个execution JSONL文件：

```
data/okx_tpsl_settings/
├── account_main_coin_change_tpsl_execution.jsonl
├── account_fangfang12_coin_change_tpsl_execution.jsonl
...
```

**执行记录格式**:
```json
{
  "timestamp": "2026-03-02T11:30:45.123456",
  "account_id": "account_main",
  "instId": "BTC-USDT-SWAP",
  "posSide": "short",
  "triggerType": "short_take_profit",
  "totalChange": -10.5,
  "threshold": 10.0,
  "success": true,
  "message": "平仓成功",
  "error": ""
}
```

## API接口

### 1. 获取当前27币涨跌幅数据

```http
GET /api/okx-trading/coin-change-current
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_change": 2.4,
    "beijing_time": "2026-03-02 11:54:51",
    "up_coins": 12,
    "down_coins": 15,
    "up_ratio": 44.4
  }
}
```

### 2. 获取配置

```http
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
    "last_updated": "2026-03-02 03:55:20",
    "comment": "27币涨跌幅止盈配置 - 空单跌破止盈/多单突破止盈"
  }
}
```

### 3. 更新配置

```http
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

### 4. 获取状态和执行记录

```http
GET /api/okx-trading/coin-change-tpsl-status/<account_id>
```

**响应示例**:
```json
{
  "success": true,
  "config": {
    "account_id": "account_main",
    "shortTakeProfitEnabled": true,
    "shortTakeProfitThreshold": 10.0,
    "longTakeProfitEnabled": true,
    "longTakeProfitThreshold": 15.0,
    "last_updated": "2026-03-02 03:55:20"
  },
  "executions": [
    {
      "timestamp": "2026-03-02T11:30:45",
      "instId": "BTC-USDT-SWAP",
      "posSide": "short",
      "triggerType": "short_take_profit",
      "totalChange": -10.5,
      "threshold": 10.0,
      "success": true
    }
  ],
  "statistics": {
    "total": 1,
    "successful": 1,
    "short_take_profit": 1,
    "long_take_profit": 0
  }
}
```

## Web界面

### 访问地址

```
https://9002-id51ob5t89zrt4phphxq8-5634da27.sandbox.novita.ai/okx-coin-change-tpsl
```

### 功能特性

- 📊 **实时27币数据展示**: 显示当前涨跌幅之和、上涨/下跌币种数量
- ⚙️ **账户选择器**: 支持切换不同交易账户
- 🔴 **空单止盈配置**: 
  - 启用/禁用开关
  - 阈值设置（百分比）
  - 说明：当涨跌幅 < -阈值时触发
- 🟢 **多单止盈配置**:
  - 启用/禁用开关
  - 阈值设置（百分比）
  - 说明：当涨跌幅 > +阈值时触发
- 📋 **执行记录**: 显示最近20条止盈执行记录
- 📈 **统计数据**: 总执行次数、成功次数、分类统计

### 界面截图说明

1. **当前数据区**: 显示27币涨跌幅之和、上涨下跌币种数、更新时间
2. **配置区**: 空单和多单的独立配置卡片
3. **执行记录区**: 执行历史、统计数据

## PM2进程管理

### 启动所有监控进程

```bash
cd /home/user/webapp
pm2 start ecosystem.config.js --only okx-coin-change-tpsl-main,okx-coin-change-tpsl-fangfang12,okx-coin-change-tpsl-poit,okx-coin-change-tpsl-poit-main,okx-coin-change-tpsl-anchor
```

### 查看进程状态

```bash
pm2 list | grep coin-change-tpsl
```

### 查看日志

```bash
# 主账户日志
pm2 logs okx-coin-change-tpsl-main --nostream --lines 50

# Fangfang12账户日志
pm2 logs okx-coin-change-tpsl-fangfang12 --nostream --lines 50

# 所有coin-change-tpsl进程日志
pm2 logs --nostream --lines 20 | grep coin-change-tpsl
```

### 重启特定进程

```bash
pm2 restart okx-coin-change-tpsl-main
```

### 停止所有监控

```bash
pm2 stop okx-coin-change-tpsl-main okx-coin-change-tpsl-fangfang12 okx-coin-change-tpsl-poit okx-coin-change-tpsl-poit-main okx-coin-change-tpsl-anchor
```

## 使用场景

### 场景1: 空单止盈

**配置**:
- 空单止盈启用: ✅
- 空单止盈阈值: 10%

**触发条件**:
- 当27币涨跌幅之和 < -10% 时触发
- 例如：涨跌幅为 -10.5% 时，系统自动平掉所有空单

**适用情况**:
- 市场快速下跌时保护空单利润
- 避免反弹造成的利润回吐

### 场景2: 多单止盈

**配置**:
- 多单止盈启用: ✅
- 多单止盈阈值: 15%

**触发条件**:
- 当27币涨跌幅之和 > +15% 时触发
- 例如：涨跌幅为 +15.3% 时，系统自动平掉所有多单

**适用情况**:
- 市场强势上涨时锁定多单利润
- 防止高位回调造成利润损失

### 场景3: 双向止盈

**配置**:
- 空单止盈启用: ✅，阈值 10%
- 多单止盈启用: ✅，阈值 15%

**效果**:
- 空单在跌破-10%时止盈
- 多单在突破+15%时止盈
- 双向保护，灵活应对市场波动

## 触发逻辑

### 空单止盈判断

```python
if total_change < -abs(short_tp_threshold):
    # 触发空单止盈
    # 例如: -10.5% < -10.0% → 触发
```

### 多单止盈判断

```python
if total_change > abs(long_tp_threshold):
    # 触发多单止盈
    # 例如: +15.3% > +15.0% → 触发
```

## 安全机制

1. **防重复执行**: 
   - 每个持仓只会执行一次止盈
   - execution文件记录已执行的持仓

2. **配置开关**:
   - 每个方向独立的启用/禁用开关
   - 可以灵活控制哪个方向的止盈

3. **阈值验证**:
   - 阈值必须为正数
   - 系统会自动转换为正数处理

4. **API凭证校验**:
   - 每次执行前验证API凭证是否存在
   - 凭证错误时跳过该账户

## 监控日志示例

```
[account_main] 🚀 启动27币涨跌幅止盈监控
[account_main] 📊 监控间隔: 30秒
[account_main] 📊 当前27币涨跌幅之和: +2.40% (时间: 2026-03-02 11:54:51)
[account_main] ℹ️  当前无持仓
[account_main] 📊 当前27币涨跌幅之和: -10.50% (时间: 2026-03-02 12:00:15)
[account_main] 📌 检查持仓: BTC-USDT-SWAP short 数量: 0.1
[account_main] 🔔 触发空单止盈: BTC-USDT-SWAP 涨跌幅-10.50% < -10.00%
[account_main] ✅ 平仓成功: BTC-USDT-SWAP short
[account_main] ✅ 执行记录已保存: BTC-USDT-SWAP short short_take_profit
[account_main] [Telegram] ✅ 通知发送成功
```

## Telegram通知示例

### 空单止盈通知

```
🎉 空单止盈成功

账户: account_main
币对: BTC-USDT-SWAP
方向: 空单
27币涨跌幅: -10.50%
止盈阈值: -10.00%
时间: 2026-03-02 12:00:15
```

### 多单止盈通知

```
🎉 多单止盈成功

账户: account_main
币对: ETH-USDT-SWAP
方向: 多单
27币涨跌幅: +15.30%
止盈阈值: +15.00%
时间: 2026-03-02 14:30:22
```

## 故障排查

### 1. 监控进程未运行

```bash
# 检查进程状态
pm2 list | grep coin-change-tpsl

# 启动进程
pm2 start ecosystem.config.js --only okx-coin-change-tpsl-main

# 查看错误日志
pm2 logs okx-coin-change-tpsl-main --err --lines 50
```

### 2. 止盈未触发

- 检查配置是否启用：`shortTakeProfitEnabled` 或 `longTakeProfitEnabled`
- 检查阈值设置是否合理
- 查看监控日志确认涨跌幅数据
- 确认持仓是否存在

### 3. 平仓失败

- 检查API凭证是否正确
- 检查网络连接
- 查看execution文件中的error字段
- 检查OKX账户状态

### 4. 重复执行

- 检查execution文件是否正常记录
- 重启监控进程清理状态
- 检查文件权限

## 注意事项

⚠️ **重要提示**:

1. **阈值设置**: 
   - 阈值应根据市场波动性合理设置
   - 过小的阈值可能频繁触发
   - 过大的阈值可能错过最佳止盈时机

2. **监控频率**:
   - 当前设置为30秒检查一次
   - 可根据需要调整`CHECK_INTERVAL`

3. **数据依赖**:
   - 依赖coin_change_tracker的实时数据
   - 确保coin-change-tracker进程正常运行

4. **账户配置**:
   - 每个账户需要在`data/okx_auto_strategy/`目录下有对应的配置文件
   - 配置文件包含API凭证

5. **风险控制**:
   - 止盈只是风险控制的一部分
   - 建议配合止损、仓位管理等综合使用

## 文件清单

### 核心文件

- `source_code/okx_coin_change_tpsl_monitor.py` - 监控脚本
- `templates/okx_coin_change_tpsl.html` - Web界面
- `ecosystem.config.js` - PM2配置（已添加5个监控进程）
- `app.py` - Flask路由和API（已添加4个新接口）

### 数据文件

- `data/okx_tpsl_settings/account_*_coin_change_tpsl.jsonl` - 配置文件
- `data/okx_tpsl_settings/account_*_coin_change_tpsl_execution.jsonl` - 执行记录
- `data/coin_change_tracker/coin_change_YYYYMMDD.jsonl` - 币种涨跌数据源

### 日志文件

- `logs/okx-coin-change-tpsl-main-out.log` - 主账户日志
- `logs/okx-coin-change-tpsl-fangfang12-out.log` - Fangfang12账户日志
- `logs/okx-coin-change-tpsl-poit-out.log` - POIT账户日志
- `logs/okx-coin-change-tpsl-poit-main-out.log` - POIT主账户日志
- `logs/okx-coin-change-tpsl-anchor-out.log` - 锚点账户日志

## 版本历史

### v1.0.0 (2026-03-02)

- ✅ 初始版本发布
- ✅ 支持空单和多单两个方向的止盈
- ✅ 每个账户独立配置和监控
- ✅ Web界面配置管理
- ✅ Telegram通知
- ✅ 执行记录和统计

## 未来计划

- [ ] 添加止盈历史图表展示
- [ ] 支持分时段不同阈值
- [ ] 添加模拟测试模式
- [ ] 支持部分平仓（按比例）
- [ ] 添加止盈效果回测分析

---

**文档更新时间**: 2026-03-02  
**系统版本**: v1.0.0  
**维护者**: Trading System Team
