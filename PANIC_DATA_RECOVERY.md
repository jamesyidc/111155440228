# 恐慌洗盘指数数据恢复说明

## 问题描述

**时间**: 2026-02-17 01:00  
**现象**: 恐慌洗盘指数页面显示 2026-02-17 只有 2 条记录，而 2026-02-16 有 390 条记录

## 根本原因

**panic-wash-collector** 采集器在 **2026-02-15 18:53:13** 后停止工作，导致：
- 2026-02-15 18:53 之后没有新数据
- 2026-02-16 全天没有数据（只有之前残留的 2 条）
- 2026-02-17 只有凌晨的 2 条数据

## 解决方案

### 1. 重启采集器
```bash
cd /home/user/webapp
pm2 restart panic-wash-collector
```

### 2. 验证采集器状态
```bash
# 查看最新日志
pm2 logs panic-wash-collector --nostream --lines 20

# 查看数据文件
tail -3 data/panic_jsonl/panic_wash_index.jsonl
```

### 3. 确认数据恢复

重启后采集器已正常工作，最新数据：
- **2026-02-17 01:03:16**: panic_index=0.14, 1h爆仓=512.05万$
- **2026-02-17 01:06:20**: panic_index=0.14, 1h爆仓=490.27万$  
- **2026-02-17 01:08:44**: panic_index=0.14, 1h爆仓=237.26万$

## 数据采集规格

- **采集频率**: 每 3 分钟一次
- **数据源**: btc126.com 真实爆仓数据
- **存储位置**: `data/panic_jsonl/panic_wash_index.jsonl`
- **每日数据量**: 约 480 条记录（24小时 × 60分钟 ÷ 3分钟）

## 预防措施

### 1. 监控采集器运行状态
```bash
# 定期检查所有采集器
pm2 status

# 检查特定采集器日志
pm2 logs panic-wash-collector --lines 50
```

### 2. 添加健康检查
建议在 `system-health-monitor-v2` 中添加：
- 检查最新数据时间戳
- 如果超过 10 分钟无新数据，自动重启采集器
- 发送告警通知

### 3. 数据完整性验证
```python
# 检查每日数据点数量
import json
from collections import defaultdict

data_by_date = defaultdict(int)
with open('data/panic_jsonl/panic_wash_index.jsonl', 'r') as f:
    for line in f:
        record = json.loads(line)
        date = record['beijing_time'][:10]
        data_by_date[date] += 1

# 正常情况下每天应该有约 480 条记录
for date, count in sorted(data_by_date.items())[-7:]:
    status = "✅" if count > 400 else "⚠️"
    print(f"{status} {date}: {count} 条记录")
```

## 影响分析

### 缺失数据时间段
- **2026-02-15**: 18:53 之后缺失（约 100 条）
- **2026-02-16**: 全天缺失（约 480 条）
- **2026-02-17**: 00:00-01:03 缺失（约 21 条）

### 业务影响
- 1小时爆仓金额曲线图出现断点
- 恐慌洗盘指数趋势图不完整
- 24小时统计数据可能不准确

### 数据恢复建议
由于历史数据无法从 btc126.com 回溯获取，建议：
1. 在图表中标注数据缺失时间段
2. 使用插值或平滑算法填补缺失点（仅用于显示）
3. 在统计分析时排除缺失时间段

## 相关文件

- **采集器脚本**: `source_code/panic_wash_collector.py`
- **数据存储**: `data/panic_jsonl/panic_wash_index.jsonl`
- **页面模板**: `templates/panic_new.html`
- **API路由**: `app.py` (line 1789, 3265, 3342, 3468, 3623)

## 恢复时间线

- **2026-02-15 18:53:13**: 采集器最后一次成功采集
- **2026-02-17 01:08:35**: 采集器重新启动
- **2026-02-17 01:08:44**: 首条新数据写入
- **采集间隔**: 每 3 分钟
- **预计恢复**: 2026-02-17 01:08 开始正常采集

---

**总结**: panic-wash-collector 已重启并恢复正常工作，从 2026-02-17 01:08 开始将每 3 分钟采集一次数据。页面将在几个小时后恢复正常的数据密度显示。
