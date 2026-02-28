# 事件7和事件8的SAR条件修复报告

## 修复时间
2026-02-06

## 问题描述

### 原问题
事件7（一般逃顶）和事件8（一般抄底）的SAR条件判断逻辑存在严重错误：

1. **统计对象错误**：统计的是**记录数**而非**币种数**
2. **字段不存在**：使用不存在的`long_pct`和`short_pct`字段
3. **条件不准确**：无法真实反映市场的偏多/偏空情况

### 触发条件（修复前）
- **事件7**：SAR偏空>=80%的**记录数**>=20
- **事件8**：SAR偏多>=80%的**记录数**>=7

这会导致误判，因为：
- 一个币种在12小时内可能有很多记录
- 记录数不等于币种数
- `long_pct`/`short_pct`字段在实际数据中不存在

---

## 修复方案

### 新的统计逻辑

#### 事件7（一般逃顶）- 条件2：SAR偏空趋势
```python
# 1. 遍历27个交易对
for symbol in trading_pairs:
    # 2. 读取该币种最近12小时的SAR数据
    sar_data = load_sar_data(symbol, 12_hours)
    
    # 3. 统计处于bearish状态的数据点
    bearish_count = count_where(position == "bearish")
    total_count = len(sar_data)
    
    # 4. 计算偏空比例
    bearish_ratio = bearish_count / total_count
    
    # 5. 如果>=80%，该币种计入偏空币种
    if bearish_ratio >= 0.80:
        high_bearish_symbols.append(symbol)

# 6. 条件：偏空币种数>=20
if len(high_bearish_symbols) >= 20:
    条件2满足
```

#### 事件8（一般抄底）- 条件3：SAR偏多趋势
```python
# 1. 遍历27个交易对
for symbol in trading_pairs:
    # 2. 读取该币种最近12小时的SAR数据
    sar_data = load_sar_data(symbol, 12_hours)
    
    # 3. 统计处于bullish状态的数据点
    bullish_count = count_where(position == "bullish")
    total_count = len(sar_data)
    
    # 4. 计算偏多比例
    bullish_ratio = bullish_count / total_count
    
    # 5. 如果>=80%，该币种计入偏多币种
    if bullish_ratio >= 0.80:
        high_bullish_symbols.append(symbol)

# 6. 条件：偏多币种数>=7
if len(high_bullish_symbols) >= 7:
    条件3满足
```

---

## 修复细节

### 文件修改
- `major-events-system/major_events_monitor.py`

### 修改要点

#### 1. 数据源正确化
- **修复前**：读取`bias_stats_*.jsonl`，使用不存在的字段
- **修复后**：读取每个币种的`data/sar_jsonl/{SYMBOL}.jsonl`

#### 2. 统计逻辑正确化
- **修复前**：`count(records where long_pct >= 80)`
- **修复后**：`count(symbols where bullish_ratio >= 80%)`

#### 3. 添加详细日志
```
📊 [事件7] SAR偏空>=80%的币种数: 18/27
[事件7] 偏空币种: BTC, ETH, SOL, ...
```

```
📊 [事件8] SAR偏多>=80%的币种数: 5/27
[事件8] 偏多币种: TON, BNB, ...
```

---

## 验证结果

### 事件8示例（2026-02-05 20:25）
Telegram消息显示事件8触发，但实际检查：

#### 条件1：✅ 满足
- 总跌幅创新低：-142.20%
- 绝对值和：>60%

#### 条件2：✅ 满足
- 10分钟内未再创新低

#### 条件3：❌ 不满足（修复后正确判断）
- **期望**：>=7个币种偏多比例>=80%
- **实际**：仅2-3个币种满足条件
- **结论**：系统现在会正确拒绝触发

---

## 修复后的触发条件

### 事件7（一般逃顶）
1. **条件1**：涨跌幅绝对值和 > 60%
2. **条件2**：创新高后10分钟未再创新高
3. **条件3**：**>=20个币种**在最近12小时内**偏空比例>=80%**

### 事件8（一般抄底）
1. **条件1**：涨跌幅绝对值和 > 60%
2. **条件2**：创新低后10分钟未再创新低
3. **条件3**：**>=7个币种**在最近12小时内**偏多比例>=80%**

---

## 代码变更

### 关键代码段

#### 事件8 - 条件3检查（偏多）
```python
# 统计偏多>=80%的币种数量
trading_pairs = ['AAVE', 'APT', 'BCH', ...] # 27个币种

high_bullish_symbols = []
for symbol in trading_pairs:
    sar_file = f'data/sar_jsonl/{symbol}.jsonl'
    if not os.path.exists(sar_file):
        continue
    
    # 读取最近12小时数据
    twelve_hours_ago = beijing_now - timedelta(hours=12)
    bullish_count = 0
    total_count = 0
    
    with open(sar_file, 'r') as f:
        for line in f:
            record = json.loads(line)
            timestamp = datetime.fromtimestamp(record['timestamp'] / 1000, tz=BEIJING_TZ)
            if timestamp >= twelve_hours_ago:
                total_count += 1
                if record.get('position') == 'bullish':
                    bullish_count += 1
    
    if total_count > 0:
        bullish_ratio = bullish_count / total_count
        if bullish_ratio >= 0.80:
            high_bullish_symbols.append(symbol)

# 条件判断
if len(high_bullish_symbols) >= 7:
    logger.info(f"✅ [事件8] 条件3满足：偏多>=80%币种数 {len(high_bullish_symbols)}>=7")
    logger.info(f"[事件8] 偏多币种: {', '.join(high_bullish_symbols)}")
    event8_condition3_met = True
```

---

## 系统状态

### 服务状态
- ✅ major-events-monitor: 已重启，修复生效
- ✅ flask-app: 运行正常
- ✅ 所有数据采集器: 正常运行

### 数据验证
```bash
# 查看SAR数据
tail -1 data/sar_jsonl/BTC.jsonl | python3 -m json.tool

# 输出示例
{
  "symbol": "BTC",
  "timestamp": 1770294600000,
  "beijing_time": "2026-02-05 20:30:00",
  "close": 69471.5,
  "sar": 70428.181067008,
  "position": "bearish",  # ← 使用此字段判断
  "quadrant": "Q3",
  "duration_minutes": 20,
  "slope_value": 0.136,
  "slope_direction": "up"
}
```

---

## 提交记录

### Commit信息
```
fix: 修复事件7的SAR偏空条件判断逻辑

- 原问题：统计的是记录数而非币种数，且使用不存在的short_pct字段
- 新逻辑：
  1. 遍历27个交易对，读取每个币种最近12小时的SAR数据
  2. 计算每个币种在12小时内处于bearish状态的比例
  3. 统计有多少个币种的偏空比例>=80%
  4. 当>=20个币种满足条件时，条件2才成立
- 添加详细日志输出偏空币种列表

Commit: 07e912f
```

---

## 测试建议

### 手动测试
1. 监控Telegram消息
2. 观察事件7/8的触发情况
3. 验证日志输出的偏多/偏空币种列表

### 预期行为
- **事件触发更准确**：不会因为误判而频繁触发
- **日志更详细**：可以清楚看到哪些币种满足条件
- **条件更严格**：确保市场真正处于极端偏多/偏空状态

---

## 总结

✅ **已修复**：事件7和事件8的SAR条件判断逻辑
✅ **已验证**：逻辑正确，统计的是币种数而非记录数
✅ **已部署**：服务已重启，修复立即生效
✅ **已提交**：代码已提交到Git仓库

系统现在能够正确判断市场的偏多/偏空情况，避免误触发！
