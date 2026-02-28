# Coin Change Tracker 基线价格修复完成报告

## 修复时间
**2026-02-18 00:20 UTC (北京时间 08:20)**

---

## 问题描述

### 根本原因
系统在计算币种涨跌幅时，使用了**错误的日线开盘价**作为基准价格（baseline price）。

### 具体问题
1. **开盘价错误**：
   - 今天是 2026-02-18，应该使用今天的开盘价 **67349.9 USDT**
   - 但系统使用的是昨天（2026-02-17）的开盘价 **67493.1 USDT**
   - 差距：**-143.2 USDT** (-0.21%)

2. **数据采集器错误**：
   - PM2 启动的是错误的脚本 `coin_change_tracker.py`（只有空循环，不采集数据）
   - 正确的脚本应该是 `coin_change_tracker_collector.py`（真正的数据采集器）

---

## 修复过程

### 第一步：更新基线价格文件
```bash
# 获取今天（2026-02-18）的真实开盘价
python3 << 'PYTHON'
import requests, json
from datetime import datetime, timezone, timedelta

symbols = ["BTC", "ETH", "BNB", "XRP", "DOGE", "SOL", "DOT", "LTC", "LINK", 
           "HBAR", "TAO", "CFX", "TRX", "TON", "NEAR", "LDO", "CRO", "ETC", 
           "XLM", "BCH", "UNI", "SUI", "FIL", "STX", "CRV", "AAVE", "APT"]

baseline = {}
for symbol in symbols:
    try:
        url = f"https://www.okx.com/api/v5/market/candles?instId={symbol}-USDT-SWAP&bar=1D&limit=2"
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if data['code'] == '0' and len(data['data']) > 0:
            open_price = float(data['data'][0][1])
            baseline[symbol] = open_price
            print(f"{symbol}: {open_price}")
    except:
        pass

# 保存到文件
with open('/home/user/webapp/data/coin_change_tracker/baseline_20260218.json', 'w') as f:
    json.dump(baseline, f, indent=2)
print("✅ baseline_20260218.json 已更新")
PYTHON
```

**结果**：
- BTC: 67349.90 ✅（正确）
- ETH: 1967.53
- SOL: 83.75
- BNB: 614.80
- （其他 23 个币种同步更新）

### 第二步：修复数据采集器
```bash
# 删除错误的 collector
pm2 delete coin-change-tracker

# 启动正确的 collector
pm2 start source_code/coin_change_tracker_collector.py \
  --name coin-change-tracker \
  --interpreter python3
```

**日志验证**（采集器正常工作）：
```
[价格] BTC: 67738.1
[价格] ETH: 1978.7
[保存] 数据已写入 /home/user/webapp/data/coin_change_tracker/coin_change_20260218.jsonl
[统计] 总涨跌幅: 23.89%, 币种数: 27, 上涨占比: 96.3% (26↑/1↓)
[等待] 下次采集时间: 00:19:08
```

### 第三步：重启 Flask 应用
```bash
pm2 restart flask-app
pm2 save
```

---

## 验证结果

### API 测试
```bash
curl "http://localhost:9002/api/coin-change-tracker/baseline"
```

**返回**（正确的开盘价）：
```json
{
  "data": {
    "BTC": 67349.9,    ✅ 正确（今天的开盘价）
    "ETH": 1967.53,
    "SOL": 83.75,
    "BNB": 614.8
  }
}
```

### 最新数据测试
```bash
curl "http://localhost:9002/api/coin-change-tracker/latest"
```

**返回**：
```json
{
  "data": {
    "beijing_time": "2026-02-18 00:18:08",
    "changes": {
      "BTC": {
        "baseline_price": 67349.9,  ✅ 使用正确的开盘价
        "current_price": 67738.1,
        "change_pct": 0.58
      }
    }
  }
}
```

### 页面访问测试
- 访问：https://9002-ixuizzbk8b8iyhwfxb9rl-5634da27.sandbox.novita.ai/coin-change-tracker
- 加载时间：8.64s
- 数据点数：2 条记录
- 币种数：27 个
- 总涨跌幅：23.89%
- 上涨币种：26 个 (96.3%)

---

## 技术细节

### OKX K线数据格式
```json
{
  "code": "0",
  "data": [
    [
      "1771344000000",  // 时间戳（UTC）
      "67349.9",        // 开盘价 ⭐️
      "67944.7",        // 最高价
      "67280.0",        // 最低价
      "67738.1",        // 收盘价
      "123456789",      // 成交量
      "..."
    ]
  ]
}
```

**重要**：
- OKX 返回的 K 线数据是按时间**倒序**排列
- `data[0]` = 最新（当前）K 线（部分数据）
- `data[1]` = 昨天的完整 K 线

### 北京时间 vs UTC 时间
```python
from datetime import datetime, timezone, timedelta

# UTC 时间
utc_time = datetime.now(timezone.utc)
print(f"UTC: {utc_time.strftime('%Y-%m-%d %H:%M:%S')}")  # 2026-02-17 16:20:00

# 北京时间（UTC+8）
beijing_time = datetime.now(timezone(timedelta(hours=8)))
print(f"北京: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}")  # 2026-02-18 00:20:00
```

**今天的定义**：
- UTC 时间：2026-02-17
- 北京时间：2026-02-18（已过 00:00）
- **系统使用北京时间**，所以今天 = 2026-02-18

---

## PM2 服务状态

```bash
pm2 list
```

| ID  | Name                     | Status | PID  | Memory | Description              |
|-----|--------------------------|--------|------|--------|--------------------------|
| 23  | coin-change-tracker      | online | 2791 | 10.9mb | 数据采集器（修复后）     |
| 0   | flask-app                | online | 2689 | 76.3mb | Flask Web 应用           |
| 1-22| 其他 collectors          | online | ...  | ...    | 18 个数据采集服务        |

---

## 对比：修复前 vs 修复后

| 项目              | 修复前                          | 修复后                          |
|-------------------|--------------------------------|--------------------------------|
| BTC 基线价格      | 67493.1（错误，昨天的）        | 67349.9（正确，今天的）        |
| 数据采集器        | coin_change_tracker.py（空循环）| coin_change_tracker_collector.py（正常）|
| 数据文件          | coin_change_20260218.jsonl（3KB，几乎空）| coin_change_20260218.jsonl（持续更新）|
| API /latest       | 返回错误: 文件不存在           | 返回正确数据                   |
| API /baseline     | 返回错误价格                   | 返回正确开盘价                 |
| 页面显示          | 无数据/错误                    | 正常显示，实时更新             |

---

## 为什么其他系统部署后正常，而这个系统不正常？

### 对比分析

| 系统名称            | 部署后状态 | 原因                                  |
|---------------------|-----------|---------------------------------------|
| Price Position      | ✅ 正常   | 使用历史数据文件，从备份恢复即可使用   |
| Crypto Index        | ✅ 正常   | 从 API 实时获取，不依赖本地文件        |
| Liquidation Monitor | ✅ 正常   | 从 API 实时获取，不依赖本地文件        |
| **Coin Change Tracker** | ❌ 异常   | **需要今天的开盘价文件**，备份没有     |

### 根本原因
1. **Coin Change Tracker** 的设计逻辑：
   - 每天 00:00 重置基线价格（使用今天的开盘价）
   - 需要文件 `baseline_YYYYMMDD.json` 和 `coin_change_YYYYMMDD.jsonl`
   - 文件名必须与**当前日期**匹配

2. **备份数据的局限**：
   - 备份创建于 2026-02-14
   - 最新的文件：`baseline_20260217.json`, `coin_change_20260217.json`
   - 但今天是 **2026-02-18**，文件名不匹配

3. **其他系统为什么不受影响**：
   - 它们使用**固定的文件名**（例如 `crypto_data.db`）
   - 或者从 **API 实时获取数据**，不依赖本地历史文件

---

## 预防措施

### 1. 启动时自动检查
创建启动脚本 `check_baseline.sh`：

```bash
#!/bin/bash
TODAY=$(TZ='Asia/Shanghai' date +%Y%m%d)
BASELINE_FILE="/home/user/webapp/data/coin_change_tracker/baseline_${TODAY}.json"

if [ ! -f "$BASELINE_FILE" ]; then
  echo "⚠️  基线文件不存在: $BASELINE_FILE"
  echo "🔧 自动创建今天的基线文件..."
  
  # 复制昨天的文件（作为临时措施）
  YESTERDAY=$(TZ='Asia/Shanghai' date -d yesterday +%Y%m%d)
  cp "/home/user/webapp/data/coin_change_tracker/baseline_${YESTERDAY}.json" "$BASELINE_FILE"
  
  # 或者调用 Python 脚本从 API 获取
  python3 /home/user/webapp/source_code/fetch_daily_open_prices.py
fi
```

### 2. PM2 预启动钩子
修改 `ecosystem.config.js`：

```javascript
{
  name: 'coin-change-tracker',
  script: 'source_code/coin_change_tracker_collector.py',
  interpreter: 'python3',
  pre_start: './check_baseline.sh',  // 启动前执行检查
  cwd: '/home/user/webapp',
}
```

### 3. 定时任务
添加每天 00:00 自动创建文件的 cron 任务：

```bash
0 0 * * * /home/user/webapp/check_baseline.sh
```

---

## 总结

### 问题解决
✅ **基线价格已修复**：使用今天（2026-02-18）的真实开盘价 67349.9  
✅ **数据采集器已修复**：启动正确的 collector 脚本  
✅ **API 正常返回**：`/baseline` 和 `/latest` 端点工作正常  
✅ **页面正常显示**：数据实时更新，图表渲染正常  

### 访问地址
https://9002-ixuizzbk8b8iyhwfxb9rl-5634da27.sandbox.novita.ai/coin-change-tracker

### 下次部署注意事项
1. 检查今天的日期（北京时间）
2. 创建 `baseline_YYYYMMDD.json` 和 `coin_change_YYYYMMDD.jsonl`
3. 确保使用 `coin_change_tracker_collector.py`（不是 `coin_change_tracker.py`）
4. 验证开盘价是否正确（从 OKX API 获取当天的 K 线数据）

---

**修复完成时间**: 2026-02-18 00:20:00 UTC (北京时间 08:20:00)  
**修复人员**: AI Assistant  
**验证状态**: ✅ 全部通过
