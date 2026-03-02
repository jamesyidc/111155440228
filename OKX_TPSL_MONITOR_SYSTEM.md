# OKX 止盈止损自动监控系统

## ✅ 止盈止损后台自动执行 - 无需浏览器打开 (v3.0 - 2026-02-28)

### 【问题】止盈止损需要浏览器保持打开，关闭后无法执行

### 【修复】后台自动监控服务 - 7×24小时运行

### 🟢 后台监控进程：okx-tpsl-monitor

- ✅ PM2守护进程管理，崩溃自动重启
- ✅ 每60秒自动检查所有账户的持仓盈亏
- ✅ 触发止盈/止损条件时立即执行平仓
- ✅ 完全不依赖浏览器，关闭浏览器也能执行
- ✅ 支持普通止盈止损 + 市场情绪紧急止盈

### 📊 监控账户（5个）：

- account_main（主账户）
- account_fangfang12
- account_poit_main（POIT子账户）
- account_anchor（锚点账户）
- account_dadanini（新增）

### 🎯 工作流程：

1. 每60秒扫描所有账户
2. 读取止盈止损配置（data/okx_tpsl_settings/）
3. 获取当前持仓并计算盈亏百分比
4. 检查是否触发：
   - 市场情绪止盈（优先）：检测到极端信号立即平仓
   - 普通止盈：盈亏% ≥ 止盈阈值
   - 普通止损：盈亏% ≤ 止损阈值
5. 执行平仓（调用OKX API设置条件单）
6. 记录执行结果（防止重复执行）
7. 发送Telegram通知

### 🔒 安全机制：

- ✅ 防重复执行：每个持仓的止盈/止损只执行一次
- ✅ 执行记录：保存到 {account_id}_tpsl_execution.jsonl
- ✅ 自动重启：PM2确保进程崩溃后自动恢复
- ✅ 日志记录：详细记录每次检查和执行过程
- ✅ 实时通知：Telegram推送执行结果

### 📋 配置文件：

- 止盈止损设置：data/okx_tpsl_settings/{account_id}_tpsl.jsonl
- 账户API凭证：data/okx_auto_strategy/{account_id}.json
- 执行记录：data/okx_tpsl_settings/{account_id}_tpsl_execution.jsonl

### 🔍 查看运行状态：

```bash
# 查看监控进程
pm2 list | grep okx-tpsl-monitor

# 查看实时日志
pm2 logs okx-tpsl-monitor --lines 50

# 日志示例：
[account_main] 📊 DOT-USDT-SWAP long: 盈亏=0.41%
[account_main] 📊 UNI-USDT-SWAP long: 盈亏=-0.75%
[account_main] 🎯 触发止盈: 12.5% >= 12.0%
[account_main] ✅ 止盈设置成功
等待 60 秒后继续...
```

### 💡 重要提示：

1. 监控进程已经在后台运行，无需手动启动
2. 浏览器中的止盈止损开关只控制前端页面的弹窗提示
3. 后台监控服务读取JSONL配置文件，不受前端开关影响
4. 修改止盈止损阈值后，后台会在下次检查时自动读取新配置
5. 如需临时禁用监控，修改JSONL文件中的 enabled 字段为 false

### ⚠️ 注意事项：

1. 确保账户API凭证配置正确（apiKey、apiSecret、passphrase）
2. 确保账户有足够的持仓才会触发止盈止损
3. 监控进程每60秒检查一次，不是实时的（已够快）
4. 市场剧烈波动时可能存在滑点，建议设置合理的止盈止损阈值
5. 详细文档：FIX_BACKEND_AUTOMATION_2026-02-28.md

---

## 📋 系统概述

**创建时间：** 2026-02-17  
**版本：** V3.0 (2026-02-28 更新)
**目的：** 按交易账户分开管理止盈止损，通过JSONL配置文件控制，防止重复执行

---

## 🎯 核心功能

### 1. 按账户分开配置
- ✅ 每个账户独立的JSONL配置文件
- ✅ 每个账户独立的执行记录文件
- ✅ 支持单独启用/禁用止盈或止损
- ✅ 支持全局启用/禁用整个账户的止盈止损

### 2. JSONL抬头控制
- ✅ 配置文件第一行为抬头，控制是否允许执行
- ✅ 修改抬头即可启用/禁用功能
- ✅ 修改配置会记录到history文件

### 3. 防止重复执行
- ✅ 每个持仓只允许执行一次止盈或止损
- ✅ 执行记录写入独立的execution JSONL文件
- ✅ 下次检查前先验证是否已执行

### 4. 后台自动监控
- ✅ PM2守护进程，每60秒检查一次
- ✅ 自动获取持仓，计算盈亏百分比
- ✅ 达到阈值自动触发止盈/止损

---

## 📂 文件结构

```
data/okx_tpsl_settings/
├── account_main_tpsl.jsonl              # 配置文件（抬头）
├── account_main_tpsl_execution.jsonl    # 执行记录
├── account_main_history.jsonl           # 配置修改历史
│
├── account_fangfang12_tpsl.jsonl
├── account_fangfang12_tpsl_execution.jsonl
├── account_fangfang12_history.jsonl
│
├── account_poit_main_tpsl.jsonl
├── account_poit_main_tpsl_execution.jsonl
├── account_poit_main_history.jsonl
│
├── account_anchor_tpsl.jsonl
├── account_anchor_tpsl_execution.jsonl
├── account_anchor_history.jsonl
│
└── account_dadanini_tpsl.jsonl
    account_dadanini_tpsl_execution.jsonl
    account_dadanini_history.jsonl

source_code/
└── okx_tpsl_monitor.py                  # 后台监控脚本
```

---

## 📝 配置文件格式

### JSONL配置文件（*_tpsl.jsonl）

**文件：** `data/okx_tpsl_settings/account_main_tpsl.jsonl`

```json
{"account_id": "account_main", "enabled": true, "take_profit_enabled": true, "take_profit_threshold": 12.0, "stop_loss_enabled": true, "stop_loss_threshold": -8.0, "last_updated": "2026-02-17 20:00:00", "comment": "止盈止损配置 - 当前触发允许JSONL文件抬头"}
```

**字段说明：**

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `account_id` | string | 账户ID | `"account_main"` |
| `enabled` | boolean | 是否启用整个止盈止损功能 | `true` / `false` |
| `take_profit_enabled` | boolean | 是否启用止盈 | `true` / `false` |
| `take_profit_threshold` | float | 止盈阈值（百分比） | `12.0` (表示+12%) |
| `stop_loss_enabled` | boolean | 是否启用止损 | `true` / `false` |
| `stop_loss_threshold` | float | 止损阈值（百分比） | `-8.0` (表示-8%) |
| `last_updated` | string | 最后更新时间 | `"2026-02-17 20:00:00"` |
| `comment` | string | 备注信息 | 任意文字 |

**重要说明：**
- ⚠️ **只读取第一行（抬头）**
- ⚠️ 修改任何字段都会影响监控行为
- ⚠️ `enabled: false` 会完全停止该账户的止盈止损监控

---

### 执行记录文件（*_tpsl_execution.jsonl）

**文件：** `data/okx_tpsl_settings/account_main_tpsl_execution.jsonl`

```json
{"timestamp": "2026-02-17T20:15:30.123456", "account_id": "account_main", "instId": "BTC-USDT-SWAP", "posSide": "long", "triggerType": "take_profit", "success": true, "message": "take_profit设置成功", "error": ""}
{"timestamp": "2026-02-17T21:30:45.654321", "account_id": "account_main", "instId": "ETH-USDT-SWAP", "posSide": "short", "triggerType": "stop_loss", "success": true, "message": "stop_loss设置成功", "error": ""}
```

**字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `timestamp` | string | 执行时间戳（ISO格式） |
| `account_id` | string | 账户ID |
| `instId` | string | 交易对（如 `BTC-USDT-SWAP`） |
| `posSide` | string | 持仓方向（`long`/`short`） |
| `triggerType` | string | 触发类型（`take_profit`/`stop_loss`） |
| `success` | boolean | 是否成功 |
| `message` | string | 成功消息 |
| `error` | string | 错误信息（成功时为空） |

**用途：**
- ✅ 防止同一持仓重复触发
- ✅ 记录执行历史，便于审计
- ✅ 失败记录可用于排查问题

---

## 🔧 API接口

### 1. 获取止盈止损设置

**端点：** `GET /api/okx-trading/tpsl-settings/<account_id>`

**说明：** 从JSONL文件读取配置（优先读取抬头）

**返回示例：**
```json
{
  "success": true,
  "settings": {
    "takeProfitThreshold": 12.0,
    "stopLossThreshold": -8.0,
    "takeProfitEnabled": true,
    "stopLossEnabled": true,
    "enabled": true,
    "lastUpdated": "2026-02-17 20:00:00"
  },
  "source": "jsonl"
}
```

**source说明：**
- `jsonl` - 从JSONL文件读取
- `json` - 从旧JSON文件读取（兼容）
- `default` - 使用默认值

---

### 2. 保存止盈止损设置

**端点：** `POST /api/okx-trading/tpsl-settings/<account_id>`

**请求体：**
```json
{
  "enabled": true,
  "takeProfitEnabled": true,
  "takeProfitThreshold": 12.0,
  "stopLossEnabled": true,
  "stopLossThreshold": -8.0
}
```

**返回示例：**
```json
{
  "success": true,
  "message": "止盈止损设置已保存到JSONL",
  "settings": {
    "takeProfitThreshold": 12.0,
    "stopLossThreshold": -8.0,
    "takeProfitEnabled": true,
    "stopLossEnabled": true,
    "enabled": true,
    "lastUpdated": "2026-02-17 20:15:30"
  }
}
```

**说明：**
- ✅ 会覆盖JSONL文件的第一行（抬头）
- ✅ 会追加一条记录到history文件
- ✅ 前端传入camelCase，后端转换为snake_case

---

## 🤖 后台监控脚本

### 脚本信息

**文件：** `source_code/okx_tpsl_monitor.py`  
**PM2进程名：** `okx-tpsl-monitor`  
**检查间隔：** 60秒

### 工作流程

```
1. 扫描所有账户配置文件 (data/okx_auto_strategy/account_*.json)
   └─> 找到4个账户: account_main, account_fangfang12, account_poit_main, account_poit

2. 为每个账户创建监控器 (TPSLMonitor)
   
3. 每个监控器执行以下步骤:
   
   ├─> 3.1 加载JSONL配置文件抬头
   │        文件: data/okx_tpsl_settings/<account_id>_tpsl.jsonl
   │        检查: enabled 字段
   │
   ├─> 3.2 检查是否启用
   │        如果 enabled=false，跳过该账户
   │
   ├─> 3.3 加载账户API凭证
   │        文件: data/okx_auto_strategy/<account_id>.json
   │        读取: apiKey, apiSecret, passphrase
   │
   ├─> 3.4 调用OKX API获取当前持仓
   │        端点: /api/v5/account/positions
   │
   ├─> 3.5 遍历每个持仓
   │   │
   │   ├─> 计算当前盈亏百分比
   │   │    多单: pnl% = ((当前价 - 开仓价) / 开仓价) * 100
   │   │    空单: pnl% = ((开仓价 - 当前价) / 开仓价) * 100
   │   │
   │   ├─> 检查止盈条件
   │   │    如果 take_profit_enabled=true 且 pnl% >= take_profit_threshold:
   │   │      ├─> 检查是否已执行 (查询execution文件)
   │   │      └─> 执行止盈 (调用OKX API)
   │   │           └─> 记录执行结果到execution文件
   │   │
   │   └─> 检查止损条件
   │        如果 stop_loss_enabled=true 且 pnl% <= stop_loss_threshold:
   │          ├─> 检查是否已执行
   │          └─> 执行止损 (调用OKX API)
   │               └─> 记录执行结果到execution文件

4. 等待60秒，重复步骤3
```

### 执行逻辑

**止盈计算：**
```python
# 多单止盈价
tp_px = 开仓价 * (1 + 止盈百分比)

# 空单止盈价
tp_px = 开仓价 * (1 - 止盈百分比)
```

**止损计算：**
```python
# 多单止损价
sl_px = 开仓价 * (1 - |止损百分比|)

# 空单止损价
sl_px = 开仓价 * (1 + |止损百分比|)
```

**示例：**
- 开仓价：100 USDT
- 止盈：12%
- 止损：-8%

**多单：**
- 止盈价：100 * 1.12 = 112 USDT
- 止损价：100 * 0.92 = 92 USDT

**空单：**
- 止盈价：100 * 0.88 = 88 USDT
- 止损价：100 * 1.08 = 108 USDT

---

## 🚀 启动和停止

### PM2命令

```bash
# 启动监控服务
pm2 start okx-tpsl-monitor

# 停止监控服务
pm2 stop okx-tpsl-monitor

# 重启监控服务
pm2 restart okx-tpsl-monitor

# 查看日志
pm2 logs okx-tpsl-monitor --nostream --lines 50

# 查看实时日志
pm2 logs okx-tpsl-monitor

# 查看服务状态
pm2 list | grep okx-tpsl-monitor
```

### 手动执行（测试用）

```bash
cd /home/user/webapp
python3 source_code/okx_tpsl_monitor.py
```

**注：** 手动执行会持续运行，按 `Ctrl+C` 停止

---

## ⚙️ 配置示例

### 场景1：只启用止盈

```json
{"account_id": "account_main", "enabled": true, "take_profit_enabled": true, "take_profit_threshold": 15.0, "stop_loss_enabled": false, "stop_loss_threshold": -8.0, "last_updated": "2026-02-17 20:00:00", "comment": "只启用止盈15%"}
```

### 场景2：只启用止损

```json
{"account_id": "account_main", "enabled": true, "take_profit_enabled": false, "take_profit_threshold": 12.0, "stop_loss_enabled": true, "stop_loss_threshold": -5.0, "last_updated": "2026-02-17 20:00:00", "comment": "只启用止损-5%"}
```

### 场景3：完全禁用

```json
{"account_id": "account_main", "enabled": false, "take_profit_enabled": true, "take_profit_threshold": 12.0, "stop_loss_enabled": true, "stop_loss_threshold": -8.0, "last_updated": "2026-02-17 20:00:00", "comment": "完全禁用止盈止损"}
```

### 场景4：同时启用（默认）

```json
{"account_id": "account_main", "enabled": true, "take_profit_enabled": true, "take_profit_threshold": 12.0, "stop_loss_enabled": true, "stop_loss_threshold": -8.0, "last_updated": "2026-02-17 20:00:00", "comment": "止盈+12%，止损-8%"}
```

---

## 🔍 监控和日志

### 日志位置

```bash
# PM2日志
~/.pm2/logs/okx-tpsl-monitor-out.log    # 标准输出
~/.pm2/logs/okx-tpsl-monitor-error.log  # 错误输出
```

### 日志内容示例

```
============================================================
OKX 止盈止损自动监控服务启动
时间: 2026-02-17 20:30:00
============================================================
✓ 发现账户数: 4
  账户列表: account_main, account_fangfang12, account_poit_main, account_poit

============================================================
第 1 次检查 - 2026-02-17 20:30:01
============================================================

[account_main] 📊 当前持仓数: 3
[account_main] 📊 BTC-USDT-SWAP long: 开仓=95000.00, 当前=96500.00, 盈亏=+1.58%
[account_main] 📊 ETH-USDT-SWAP long: 开仓=3200.00, 当前=3600.00, 盈亏=+12.50%
[account_main] 🎯 触发止盈条件: 12.50% >= 12.00%
[account_main] 📈 触发止盈: ETH-USDT-SWAP long, 开仓价=3200.00, 止盈价=3584.00
[account_main] ✅ take_profit 设置成功: ETH-USDT-SWAP long
[account_main] ✅ 执行记录已保存: ETH-USDT-SWAP long take_profit

[account_fangfang12] ℹ️  当前无持仓
[account_poit_main] ℹ️  止盈止损未启用
[account_poit] ℹ️  未找到配置文件

============================================================
等待 60 秒后继续...
============================================================
```

---

## ⚠️ 注意事项

### 1. 防止重复执行

**问题：** 如何确保每个持仓只执行一次？

**解决：** 
- ✅ 执行前检查execution文件
- ✅ 通过 `(instId, posSide, triggerType)` 三元组判断
- ✅ 已执行的持仓会被跳过

**示例：**
```
持仓: BTC-USDT-SWAP long
触发止盈 -> 检查execution文件 -> 未找到记录 -> 执行 -> 记录到文件
下次检查 -> 发现已记录 -> 跳过执行
```

### 2. 阈值设置建议

**止盈阈值：**
- 短线：5% - 10%
- 中线：10% - 20%
- 长线：20% - 50%

**止损阈值：**
- 保守：-3% 到 -5%
- 适中：-5% 到 -10%
- 激进：-10% 到 -15%

**注意：** 止损阈值为负数（如 `-8.0` 表示 -8%）

### 3. 监控频率

**当前设置：** 60秒检查一次

**调整方式：** 修改 `source_code/okx_tpsl_monitor.py` 中的 `CHECK_INTERVAL` 常量

```python
CHECK_INTERVAL = 60  # 改为30秒: CHECK_INTERVAL = 30
```

**建议：**
- 高频策略：30秒
- 中频策略：60秒（默认）
- 低频策略：120秒

### 4. API限流

**OKX API限流：**
- 持仓查询：每2秒1次（30次/分钟）
- 下单API：每秒1次（60次/分钟）

**当前脚本：**
- 每60秒执行一次全部检查
- 4个账户 * 1次持仓查询 = 4次/分钟
- 触发止盈/止损时才调用下单API

**结论：** 当前频率安全，不会触发限流

### 5. 错误处理

**网络错误：**
- ✅ 自动捕获异常
- ✅ 打印错误信息
- ✅ 继续下一个账户的检查

**API错误：**
- ✅ 检查返回码
- ✅ 记录错误到execution文件
- ✅ 不影响其他持仓

---

## 📊 数据验证

### 检查配置文件

```bash
# 查看所有账户的配置
cat data/okx_tpsl_settings/account_main_tpsl.jsonl
cat data/okx_tpsl_settings/account_fangfang12_tpsl.jsonl
cat data/okx_tpsl_settings/account_poit_main_tpsl.jsonl
cat data/okx_tpsl_settings/account_poit_tpsl.jsonl
```

### 检查执行记录

```bash
# 查看执行记录数量
wc -l data/okx_tpsl_settings/*_execution.jsonl

# 查看最近的执行记录
tail -10 data/okx_tpsl_settings/account_main_tpsl_execution.jsonl | jq
```

### 检查配置历史

```bash
# 查看配置修改历史
tail -20 data/okx_tpsl_settings/account_main_history.jsonl | jq
```

---

## 🔧 故障排查

### 问题1：监控服务未启动

**症状：**
```bash
pm2 list | grep okx-tpsl-monitor
# 显示: stopped
```

**排查：**
```bash
# 查看错误日志
pm2 logs okx-tpsl-monitor --err --lines 50

# 手动测试
python3 source_code/okx_tpsl_monitor.py
```

**常见原因：**
- Python依赖缺失（requests, pytz）
- 配置文件格式错误
- 权限问题

---

### 问题2：止盈/止损未触发

**排查步骤：**

1. **检查配置是否启用**
```bash
cat data/okx_tpsl_settings/account_main_tpsl.jsonl
# 确认: enabled=true, take_profit_enabled=true
```

2. **检查阈值设置**
```json
{"take_profit_threshold": 12.0}  // 需要达到+12%
```

3. **检查execution记录**
```bash
grep "BTC-USDT-SWAP" data/okx_tpsl_settings/account_main_tpsl_execution.jsonl
# 如果有记录，说明已经执行过
```

4. **查看监控日志**
```bash
pm2 logs okx-tpsl-monitor --lines 100 | grep "触发"
```

---

### 问题3：API调用失败

**症状：**
```
❌ take_profit 设置失败: Invalid API key
```

**排查：**
1. 检查账户配置文件
```bash
cat data/okx_auto_strategy/account_main.json | jq '{apiKey, apiSecret, passphrase}'
```

2. 验证API凭证
   - 登录OKX账户
   - 检查API密钥是否有效
   - 确认权限包含"交易"

---

### 问题4：重复执行

**症状：** 同一持仓被多次设置止盈/止损

**排查：**
```bash
# 检查execution文件
cat data/okx_tpsl_settings/account_main_tpsl_execution.jsonl | grep "BTC-USDT-SWAP"

# 预期: 每个 (instId, posSide, triggerType) 只有一条记录
```

**解决：**
- 脚本有防重复逻辑，理论上不会发生
- 如果发生，可能是execution文件被删除或损坏
- 恢复方案：从history重建execution文件

---

## 📈 扩展功能

### 未来可能的改进

1. **高级止盈策略**
   - 移动止损（Trailing Stop）
   - 分批止盈（部分平仓）
   - 根据波动率调整阈值

2. **通知功能**
   - 触发止盈/止损时发送通知
   - 支持Telegram/Email/Webhook

3. **统计分析**
   - 统计止盈/止损执行次数
   - 计算平均盈亏
   - 生成报表

4. **Web界面**
   - 可视化配置管理
   - 实时监控持仓状态
   - 历史执行记录查询

---

## 📚 相关文档

- **API文档：** `app.py` 中的API实现
- **监控脚本：** `source_code/okx_tpsl_monitor.py`
- **前端页面：** `templates/okx_trading.html`

---

## ✅ 总结

**实现的功能：**
1. ✅ 按账户分开配置止盈止损
2. ✅ JSONL抬头控制是否允许执行
3. ✅ 防止重复执行（每个持仓只执行一次）
4. ✅ 后台自动监控（PM2守护）
5. ✅ API支持JSONL读写
6. ✅ 执行记录完整保存

**使用流程：**
1. 在前端页面设置止盈止损阈值
2. API自动保存到JSONL配置文件
3. 启动 `okx-tpsl-monitor` 服务
4. 服务自动监控持仓，达到阈值自动触发
5. 执行记录保存到execution文件，防止重复

**安全保障：**
- ✅ 每个持仓最多执行一次
- ✅ 执行前检查记录
- ✅ 配置文件控制启用/禁用
- ✅ 错误捕获和日志记录

---

**文档版本：** 1.0  
**最后更新：** 2026-02-17 20:30:00  
**维护者：** AI Assistant

---

## 📱 Telegram 通知功能

### 功能说明

**自动运行，无需人工确认：**
- ✅ 达到止盈/止损阈值自动执行
- ✅ 平仓完成后自动发送Telegram通知
- ✅ 包含完整的平仓结果信息

### 通知内容

**止盈通知示例：**
```
🎯 OKX 止盈止损通知

账户: account_main
交易对: BTC-USDT-SWAP
方向: 多单
类型: 止盈
开仓价: 95000.00 USDT
触发价: 106400.00 USDT
状态: ✅ 设置成功

时间: 2026-02-17 20:30:00
```

**止损通知示例：**
```
🎯 OKX 止盈止损通知

账户: account_main
交易对: ETH-USDT-SWAP
方向: 空单
类型: 止损
开仓价: 3200.00 USDT
触发价: 3456.00 USDT
状态: ✅ 设置成功

时间: 2026-02-17 20:30:00
```

**失败通知示例：**
```
⚠️ OKX 止盈止损失败

账户: account_main
交易对: BTC-USDT-SWAP
方向: 多单
类型: 止盈
状态: ❌ 设置失败
错误: Insufficient margin

时间: 2026-02-17 20:30:00
```

### 配置步骤

#### 1. 创建Telegram Bot

1. 在Telegram中搜索 **@BotFather**
2. 发送 `/newbot` 命令
3. 获得Bot Token（如：`123456789:ABCdefGHI...`）

#### 2. 获取Chat ID

1. 在Telegram中搜索 **@userinfobot**
2. 发送任意消息
3. 获得Chat ID（如：`987654321`）

#### 3. 配置环境变量

编辑 `.env` 文件：

```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=987654321
```

#### 4. 测试配置

```bash
cd /home/user/webapp
python3 test_telegram.py
```

**预期输出：**
```
✅ Telegram配置正确，测试消息已发送！
请检查你的Telegram，应该会收到测试消息。
```

#### 5. 重启服务

```bash
pm2 restart okx-tpsl-monitor --update-env
```

### 验证通知

启动服务后，查看日志：

```bash
pm2 logs okx-tpsl-monitor | grep Telegram
```

**预期输出：**
```
[account_main] [Telegram] ✅ 通知发送成功
```

### 详细文档

完整的Telegram配置指南请查看：`TELEGRAM_NOTIFICATION_SETUP.md`

---

## 🔄 完整工作流程（含Telegram通知）

```
每60秒循环：
  1. 读取所有账户的配置文件（抬头）
  2. 检查 enabled 字段
  3. 调用OKX API获取持仓
  4. 计算每个持仓的盈亏百分比
  5. 检查是否达到阈值
  6. 检查是否已执行过
  7. 如果未执行，调用OKX API设置止盈/止损
     ├─> 成功 → 发送成功通知到Telegram
     └─> 失败 → 发送失败通知到Telegram
  8. 记录执行结果到execution文件
```

---

