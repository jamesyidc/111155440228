# 币种变化追踪系统 - 上涨占比功能文档

## 📊 功能概述

在币种变化追踪系统中新增**上涨占比**数据的采集、存储和展示功能。

## 🎯 实现内容

### 1. 后端数据采集 (coin_change_tracker_collector.py)

#### 新增JSONL字段
```json
{
  "timestamp": 1771231737030,
  "beijing_time": "2026-02-16 16:48:47",
  "cumulative_pct": -23.4,
  "total_change": -23.4,
  "up_ratio": 22.2,        // 🆕 上涨占比 (%)
  "up_coins": 6,           // 🆕 上涨币种数量
  "down_coins": 21,        // 🆕 下跌币种数量
  "changes": {...},
  "count": 27
}
```

#### 计算逻辑
```python
# 计算上涨占比
up_coins = sum(1 for item in changes.values() if item['change_pct'] > 0)
total_coins = len(changes)
up_ratio = (up_coins / total_coins * 100) if total_coins > 0 else 0
```

#### 采集器日志输出
```
[统计] 总涨跌幅: -23.40%, 币种数: 27, 上涨占比: 22.2% (6↑/21↓)
```

### 2. 前端展示 (coin_change_tracker.html)

#### Tooltip悬浮窗增强

**显示位置**: 趋势图鼠标悬浮tooltip

**显示格式**:
```
⏰ 时间 (HH:MM:SS)
━━━━━━━━━━━━━━━━━━
📊 27币涨跌幅之和
±XX.XX%
━━━━━━━━━━━━━━━━━━
📈 上涨占比: XX.X%
```

#### 数据读取策略
```javascript
// 优先使用JSONL中保存的up_ratio字段
if (historyData[dataIndex].up_ratio !== undefined) {
    upRatio = historyData[dataIndex].up_ratio.toFixed(1) + '%';
} 
// 如果没有up_ratio字段(旧数据)，则实时计算
else if (historyData[dataIndex].changes) {
    const changes = historyData[dataIndex].changes;
    const changesArray = Object.values(changes);
    const upCoins = changesArray.filter(coin => coin.change_pct > 0).length;
    const totalCoins = changesArray.length;
    upRatio = totalCoins > 0 ? (upCoins / totalCoins * 100).toFixed(1) + '%' : '--';
}
```

## ✅ 兼容性

### 向后兼容
- **旧JSONL数据**: 没有`up_ratio`字段时，前端自动实时计算
- **新JSONL数据**: 直接读取`up_ratio`字段，无需计算
- **性能优化**: 避免重复计算，提升tooltip渲染速度

### API响应
所有API端点(`/latest`, `/history`)都会返回新增字段：
```json
{
  "success": true,
  "data": {
    "up_ratio": 22.2,
    "up_coins": 6,
    "down_coins": 21,
    ...
  }
}
```

## 🔧 技术细节

### 数据存储
- **位置**: `/home/user/webapp/data/coin_change_tracker/coin_change_YYYYMMDD.jsonl`
- **格式**: JSONL (每行一条JSON记录)
- **频率**: 每1分钟采集一次
- **字段类型**:
  - `up_ratio`: float (保留1位小数)
  - `up_coins`: int
  - `down_coins`: int

### 进程管理
- **采集器**: `pm2 restart coin-change-tracker`
- **Flask应用**: `pm2 restart flask-app`
- **日志查看**: `pm2 logs coin-change-tracker`

## 📈 应用场景

1. **市场多空判断**
   - 上涨占比 > 50% → 市场偏多
   - 上涨占比 < 50% → 市场偏空

2. **趋势确认**
   - 总涨跌幅 > 0 且上涨占比 > 70% → 强势上涨
   - 总涨跌幅 < 0 且上涨占比 < 30% → 强势下跌

3. **分歧识别**
   - 总涨跌幅大但上涨占比接近50% → 市场分歧大

## 🚀 访问地址

**币种变化追踪系统**: https://5000-iou7okyaq15h840cyuitp-c07dda5e.sandbox.novita.ai/coin-change-tracker

## 📝 Git提交记录

```bash
Commit: aa73f55
Message: feat: 在币种变化追踪JSONL中保存上涨占比数据

Commit: ff61793
Message: feat: 在币种变化追踪图表悬浮窗添加上涨占比显示
```

## 🎉 功能验证

### 采集器日志验证
```bash
pm2 logs coin-change-tracker --lines 5 | grep "统计"
# 输出: [统计] 总涨跌幅: -23.40%, 币种数: 27, 上涨占比: 22.2% (6↑/21↓)
```

### JSONL数据验证
```bash
tail -1 data/coin_change_tracker/coin_change_20260216.jsonl | jq '.up_ratio'
# 输出: 22.2
```

### API验证
```bash
curl "http://localhost:9002/api/coin-change-tracker/latest" | jq '.data.up_ratio'
# 输出: 22.2
```

## 🔮 未来扩展

1. **历史统计分析**
   - 统计每日平均上涨占比
   - 绘制上涨占比趋势图

2. **预警功能**
   - 上涨占比 > 80% 时触发强势预警
   - 上涨占比 < 20% 时触发弱势预警

3. **策略优化**
   - 根据上涨占比调整开仓方向
   - 分析上涨占比与总涨跌幅的相关性

---

**文档版本**: v1.0  
**最后更新**: 2026-02-16  
**维护者**: GenSpark AI Developer
