# SAR斜率系统完整修复报告

**报告时间**: 2026-02-01 13:45:00 (北京时间)  
**问题**: XRP详情页显示undefined，数据未更新  
**状态**: ✅ 已修复，等待13:50首次数据采集

---

## 🔍 问题诊断过程

### 初步诊断

运行诊断脚本发现：
```bash
./scripts/diagnose_system.sh "SAR斜率系统"
```

**诊断结果**:
- ✅ Flask服务: 正常
- ✅ PM2服务 (sar-jsonl-collector): online (PID 689399)
- ⚠️ PM2服务: 重启次数108次（稳定性问题）
- ✅ PM2服务 (sar-slope-collector): online
- ❌ 数据文件 (sar_slope_data.jsonl): 不存在
- ⚠️ 数据文件 (XRP.jsonl): 数据过期 18,121分钟（12.5天）
- ✅ API端点: 正常

### 根本原因分析

1. **PM2服务虽然在线，但采集全部失败**
   - 总采集次数: 12次
   - 成功: 0个
   - 失败: 324个
   - 成功率: 0.00%

2. **错误信息**
   ```
   ERROR: 'Market' object has no attribute 'get_candlesticks'
   ```

3. **原因**
   - 之前修复时将 `okx.MarketData` 改为 `okx.api.Market`
   - 但没有修改API方法名
   - 旧API: `MarketData.get_candlesticks()`
   - 新API: `Market.get_candles()`

---

## 🔧 修复步骤

### 1. 修复API方法名

**文件**: `source_code/sar_jsonl_collector.py:171`

**修改前**:
```python
result = marketDataAPI.get_candlesticks(
    instId=inst_id,
    bar=bar,
    limit=str(limit)
)
```

**修改后**:
```python
result = marketDataAPI.get_candles(
    instId=inst_id,
    bar=bar,
    limit=str(limit)
)
```

### 2. 验证API可用性

测试新API方法：
```bash
python3 -c "
from okx import api
marketAPI = api.Market(flag='0')
result = marketAPI.get_candles(instId='XRP-USDT', bar='5m', limit='10')
print(f\"code: {result['code']}\")  # 0 表示成功
print(f\"数据条数: {len(result['data'])}\")  # 10
"
```

**结果**:
- ✅ API调用成功
- ✅ 返回10条K线数据
- ✅ 数据格式正确

### 3. 重启SAR采集器

```bash
pm2 restart sar-jsonl-collector
pm2 save
```

**重启后状态**:
- ✅ PM2服务: online (PID: 709136)
- ⏰ 首次采集时间: 2026-02-01 13:50:00
- ⏰ 等待时长: 约8分钟
- 📝 采集策略: 延迟5分钟采集（等K线完全形成）

### 4. 提交代码修复

```bash
git add source_code/sar_jsonl_collector.py
git commit -m "fix: change get_candlesticks to get_candles for new OKX API"
```

---

## 📊 SAR系统完整依赖关系

### 必需组件清单

| 组件类型 | 组件名称 | 状态 | 说明 |
|---------|---------|------|------|
| PM2服务 | sar-jsonl-collector | ✅ online | 采集原始SAR数据，每5分钟 |
| PM2服务 | sar-slope-collector | ✅ online | 计算斜率统计，每60秒 |
| 数据文件 | data/sar_jsonl/*.jsonl | ⏳ 等待更新 | 27个币种，每个一个文件 |
| 数据文件 | data/sar_slope_data.jsonl | ⏳ 等待生成 | 斜率统计数据 |
| API路由 | /api/sar-slope/latest | ✅ 正常 | 最新SAR数据 |
| API路由 | /api/sar-slope/current-cycle/{symbol} | ✅ 正常 | 单币种序列数据 |
| 页面路由 | /sar-slope | ✅ 正常 | 主页 |
| 页面路由 | /sar-slope/{symbol} | ⏳ 等待数据 | 详情页 |
| Python依赖 | okx | ✅ 已安装 | 新版OKX API |

### 数据流向

```
OKX交易所 K线数据
    ↓ (每5分钟)
sar-jsonl-collector
    ↓ 采集 + SAR计算
    ↓ 写入 data/sar_jsonl/*.jsonl
    ↓
sar-slope-collector (每60秒)
    ↓ 读取所有币种SAR数据
    ↓ 计算斜率和序列
    ↓ 写入 data/sar_slope_data.jsonl
    ↓
Flask API (/api/sar-slope/*)
    ↓ 读取JSONL数据
    ↓ 返回给前端
    ↓
前端页面 (/sar-slope, /sar-slope/XRP)
    ↓ 渲染图表和数据
```

### 采集策略

1. **延迟采集策略**
   - 延迟5分钟采集，确保K线完全形成
   - 例如: 13:45的K线 → 13:50采集
   - 原因: 避免采集到未完成的K线数据

2. **采集周期**
   - sar-jsonl-collector: 300秒（5分钟）
   - sar-slope-collector: 60秒（1分钟）

3. **首次启动延迟**
   - 等待到下一个整5分钟时刻
   - 例如: 13:42启动 → 等到13:50采集

---

## ⏰ 数据恢复时间线

| 时间 | 事件 | 状态 |
|------|------|------|
| 13:42:03 | SAR采集器重启 | ✅ 完成 |
| 13:45:00 | K线时间点 | - |
| 13:50:00 | **首次数据采集** | ⏳ 等待中 |
| 13:50:30 | XRP.jsonl更新 | ⏳ 预计 |
| 13:51:00 | sar-slope-collector读取新数据 | ⏳ 预计 |
| 13:51:00 | sar_slope_data.jsonl生成 | ⏳ 预计 |
| 13:51:30 | 详情页恢复正常 | ⏳ 预计 |
| 13:55:00 | 第二次采集（13:50 K线） | ⏳ 预计 |
| 14:00:00 | 第三次采集（13:55 K线） | ⏳ 预计 |

**预计完全恢复时间**: 2026-02-01 13:55:00（约10分钟后）

---

## ✅ 验证步骤

### 1. 检查采集器日志（13:50后）

```bash
pm2 logs sar-jsonl-collector --nostream --lines 50 | grep -E "采集|成功|失败"
```

**期望输出**:
```
[INFO] 本次采集完成: 成功 27 个, 失败 0 个
[INFO] 成功率: 100.00%
```

### 2. 检查XRP数据文件

```bash
tail -1 data/sar_jsonl/XRP.jsonl | jq '{time, position, sar, price}'
```

**期望输出**:
```json
{
  "time": "2026-02-01 13:45:00",  # 应该是最新时间
  "position": "long",  # 或 "short"
  "sar": 1.6xxx,
  "price": 1.6xxx  # 不应该是null
}
```

### 3. 检查斜率数据文件

```bash
tail -1 data/sar_slope_data.jsonl | jq '{timestamp, total_long, total_short}'
```

**期望输出**:
```json
{
  "timestamp": "2026-02-01 13:51:00",
  "total_long": 15,  # 示例值
  "total_short": 12
}
```

### 4. 测试API

```bash
curl -s 'http://localhost:5000/api/sar-slope/current-cycle/XRP?limit=10' | \
  jq '{symbol, current_status, latest_update: .current_status.last_update}'
```

**期望输出**:
```json
{
  "symbol": "XRP",
  "current_status": {...},
  "latest_update": "2026-02-01 13:45:00"  # 应该是最新时间
}
```

### 5. 访问详情页

URL: https://5000-ikmpd2up5chrwx4jjjkih-5634da27.sandbox.novita.ai/sar-slope/XRP

**期望结果**:
- ✅ 显示最新SAR数据
- ✅ 显示当前序列信息
- ✅ 图表正常渲染
- ❌ 不再显示 undefined

---

## 🚨 历史问题回顾

### 问题1: okx模块缺失（已修复）
- **时间**: 首次发现
- **错误**: `ModuleNotFoundError: No module named 'okx'`
- **修复**: `pip3 install okx`

### 问题2: API类名错误（已修复）
- **时间**: 第一次修复后
- **错误**: `ModuleNotFoundError: No module named 'okx.MarketData'`
- **修复**: 将 `from okx.MarketData import MarketAPI` 改为 `from okx import api; marketDataAPI = api.Market(flag="0")`

### 问题3: API方法名错误（本次修复）
- **时间**: 第二次修复后
- **错误**: `'Market' object has no attribute 'get_candlesticks'`
- **修复**: 将 `get_candlesticks()` 改为 `get_candles()`

### 根本原因

**OKX API版本变化**:

| API版本 | 导入方式 | 类名 | 方法名 |
|---------|---------|------|--------|
| 旧版 | `import okx.MarketData` | `MarketAPI` | `get_candlesticks()` |
| 新版 | `from okx import api` | `api.Market()` | `get_candles()` |

---

## 📋 完整修复清单

- [x] 安装okx模块
- [x] 更新API导入方式
- [x] 更新API类初始化
- [x] **更新API方法名** ← 本次修复
- [x] 重启PM2服务
- [x] 保存PM2配置
- [x] 提交代码修复
- [ ] 等待首次数据采集（13:50）
- [ ] 验证数据更新
- [ ] 验证详情页显示

---

## 🛠️ 监控命令

### 实时监控采集器

```bash
# 持续监控日志（后台运行）
pm2 logs sar-jsonl-collector --lines 0

# 查看最近采集结果
pm2 logs sar-jsonl-collector --nostream --lines 30 | grep -E "采集完成|成功|失败"
```

### 检查数据文件

```bash
# 列出所有SAR数据文件及其修改时间
ls -lth data/sar_jsonl/*.jsonl | head -10

# 检查特定币种最新数据
for symbol in XRP BTC ETH SOL; do
  echo "=== $symbol ==="
  tail -1 data/sar_jsonl/$symbol.jsonl | jq '{time, position, sar}'
done
```

### 诊断系统健康

```bash
# 完整诊断
./scripts/diagnose_system.sh "SAR斜率系统"

# 快速检查
curl -s 'http://localhost:5000/api/sar-slope/latest' | \
  jq '{success, data_count: .data | length, sample: .data[0] | {symbol, position, sar}}'
```

---

## 📝 维护建议

### 日常监控

1. **每日检查采集成功率**
   ```bash
   pm2 logs sar-jsonl-collector --nostream --lines 100 | \
     grep "成功率" | tail -5
   ```
   - 期望: 100% 成功率
   - 警告阈值: < 90%

2. **检查PM2重启次数**
   ```bash
   pm2 jlist | jq '.[] | select(.name == "sar-jsonl-collector") | {name, restarts: .pm2_env.restart_time}'
   ```
   - 正常: < 5次/天
   - 警告: > 10次/天

3. **数据时效性检查**
   ```bash
   ./scripts/diagnose_system.sh "SAR斜率系统" | grep "数据时效"
   ```
   - 期望: < 10分钟
   - 警告: > 30分钟

### 常见问题处理

| 问题 | 症状 | 处理方法 |
|------|------|---------|
| 采集失败 | 成功率 < 100% | 查看错误日志，检查OKX API可用性 |
| 数据过期 | 最新数据 > 30分钟前 | 重启sar-jsonl-collector |
| PM2频繁重启 | 重启次数 > 10次/天 | 查看错误日志，修复代码bug或I/O问题 |
| 详情页undefined | 页面显示错误 | 检查数据文件是否存在且有效 |

### 优化建议

1. **日志I/O错误**
   - 当前状态: OSError: [Errno 5] Input/output error
   - 影响: 仅日志写入失败，不影响数据采集
   - 建议: 降低日志级别或减少日志输出频率

2. **PM2稳定性**
   - 考虑使用 `--max-memory-restart` 参数
   - 监控内存使用情况
   - 定期清理旧日志

3. **数据备份**
   - 定期备份 `data/sar_jsonl/` 目录
   - 保留至少30天历史数据

---

## 🎯 总结

### 问题回顾
- **现象**: XRP详情页显示undefined，数据12.5天未更新
- **根因**: OKX API方法名从 `get_candlesticks()` 改为 `get_candles()`
- **影响**: 所有27个币种的SAR数据采集失败

### 修复成果
- ✅ 修复API方法名
- ✅ 验证API可用性
- ✅ 重启采集器
- ✅ 提交代码修复
- ⏳ 等待首次数据采集（13:50）

### 预计恢复
- **首次采集**: 2026-02-01 13:50:00
- **详情页恢复**: 2026-02-01 13:51:30
- **完全稳定**: 2026-02-01 13:55:00（3次成功采集后）

### Git提交
```
commit: fix: change get_candlesticks to get_candles for new OKX API
file: source_code/sar_jsonl_collector.py
```

---

**报告完成时间**: 2026-02-01 13:45:00  
**下次检查时间**: 2026-02-01 13:51:00  
**预计完全恢复**: 2026-02-01 13:55:00  
**维护者**: GenSpark AI Developer
