# 锚点系统高盈利统计与图表优化

## 📊 更新概述

1. **高盈利卡片数据对接**：为300%、250%、200%、150%四个高盈利统计卡片对接后台数据
2. **图表数字增大**：增大逃顶信号趋势图中极端涨跌标记的数字显示大小

## ✅ 任务1: 高盈利卡片数据对接

### 卡片位置
4个高盈利卡片位于"空单盈利≥120%"卡片上方，使用独立的stats-grid展示。

### 卡片样式

#### 🏆 空单盈利≥300%
- **颜色**: 紫色系（#a855f7）
- **图标**: 🏆
- **字体大小**: 64px超大字体
- **背景**: 紫色渐变（#e9d5ff → #d8b4fe）

#### ⭐ 空单盈利≥250%
- **颜色**: 粉色系（#ec4899）
- **图标**: ⭐
- **字体大小**: 64px超大字体
- **背景**: 粉色渐变（#fce7f3 → #fbcfe8）

#### 🔥 空单盈利≥200%
- **颜色**: 橙色系（#f97316）
- **图标**: 🔥
- **字体大小**: 64px超大字体
- **背景**: 橙色渐变（#fed7aa → #fdba74）

#### ✅ 空单盈利≥150%
- **颜色**: 绿色系（#22c55e）
- **图标**: ✅
- **字体大小**: 64px超大字体
- **背景**: 绿色渐变（#d1fae5 → #a7f3d0）

### 数据源

#### API端点
```
GET /api/coin-change-tracker/latest
```

#### 数据格式
```json
{
  "success": true,
  "data": {
    "short_stats": {
      "gte_300": 0,
      "gte_300_1h": 0,
      "gte_250": 0,
      "gte_250_1h": 0,
      "gte_200": 0,
      "gte_200_1h": 0,
      "gte_150": 0,
      "gte_150_1h": 0
    }
  }
}
```

### 数据收集脚本
文件：`/home/user/webapp/source_code/coin_change_tracker.py`

```python
# 计算不同盈利级别的空单数量
gte_300 = len([p for p in short_profits if p['profit'] >= 300])
gte_250 = len([p for p in short_profits if p['profit'] >= 250])
gte_200 = len([p for p in short_profits if p['profit'] >= 200])
gte_150 = len([p for p in short_profits if p['profit'] >= 150])

# 计算1小时内的峰值
gte_300_1h = max(gte_300_1h, len([p for p in record_short_profits if p >= 300]))
gte_250_1h = max(gte_250_1h, len([p for p in record_short_profits if p >= 250]))
gte_200_1h = max(gte_200_1h, len([p for p in record_short_profits if p >= 200]))
gte_150_1h = max(gte_150_1h, len([p for p in record_short_profits if p >= 150]))

# 保存到short_stats
short_stats = {
    'gte_300': gte_300,
    'gte_250': gte_250,
    'gte_200': gte_200,
    'gte_150': gte_150,
    'gte_300_1h': gte_300_1h,
    'gte_250_1h': gte_250_1h,
    'gte_200_1h': gte_200_1h,
    'gte_150_1h': gte_150_1h
}
```

### 前端更新代码
文件：`/home/user/webapp/source_code/templates/anchor_system_real.html`

```javascript
async function loadShortProfitStats() {
    try {
        const response = await fetch('/api/coin-change-tracker/latest');
        const result = await response.json();
        
        if (result.success && result.data) {
            const shortStats = result.data.short_stats || {};
            
            // 更新空单盈利≥300%
            document.getElementById('short300').textContent = shortStats.gte_300 || 0;
            document.getElementById('short300_1h').textContent = shortStats.gte_300_1h || 0;
            
            // 更新空单盈利≥250%
            document.getElementById('short250').textContent = shortStats.gte_250 || 0;
            document.getElementById('short250_1h').textContent = shortStats.gte_250_1h || 0;
            
            // 更新空单盈利≥200%
            document.getElementById('short200').textContent = shortStats.gte_200 || 0;
            document.getElementById('short200_1h').textContent = shortStats.gte_200_1h || 0;
            
            // 更新空单盈利≥150%
            document.getElementById('short150').textContent = shortStats.gte_150 || 0;
            document.getElementById('short150_1h').textContent = shortStats.gte_150_1h || 0;
            
            console.log('✅ 空单盈利统计更新完成:', shortStats);
        }
    } catch (error) {
        console.error('❌ 更新空单盈利统计异常:', error);
    }
}
```

### HTML元素ID

| 卡片 | 主数值ID | 1小时内ID |
|------|----------|-----------|
| 300% | `short300` | `short300_1h` |
| 250% | `short250` | `short250_1h` |
| 200% | `short200` | `short200_1h` |
| 150% | `short150` | `short150_1h` |

### 数据更新频率
- **主页面加载时**：立即加载一次
- **自动刷新**：随其他数据每30秒更新一次
- **手动刷新**：点击"刷新数据"按钮时更新

## ✅ 任务2: 图表标记数字增大

### 修改内容

#### 极端上涨标记（💥 ≥100%）

##### 修改前
```javascript
symbolSize: 80,
fontSize: 12,
offset: [0, 12]
```

##### 修改后
```javascript
symbolSize: 90,     // 标记点从80增大到90
fontSize: 16,       // 字体从12增大到16
offset: [0, 15]     // 偏移量相应调整
```

#### 极端暴跌标记（💀 ≤-80%）

##### 修改前
```javascript
symbolSize: 80,
fontSize: 12,
offset: [0, 12]
```

##### 修改后
```javascript
symbolSize: 90,     // 标记点从80增大到90
fontSize: 16,       // 字体从12增大到16
offset: [0, 15]     // 偏移量相应调整
```

### 视觉效果对比

#### 修改前
- 标记点大小：80px
- 数字字体：12px
- 显示效果：较小，不够醒目

#### 修改后
- 标记点大小：90px（增大12.5%）
- 数字字体：16px（增大33%）
- 显示效果：更大更清晰，易于识别

### 标记触发条件

#### 极端上涨（红色标记 💥）
- **触发条件**: OKX 27币种总涨跌 ≥ 100%
- **颜色**: 红色（#ff0000）
- **防重复**: 同一小时内只标记一次

#### 极端暴跌（黑色标记 💀）
- **触发条件**: OKX 27币种总涨跌 ≤ -80%
- **颜色**: 黑色（#000000）
- **防重复**: 同一小时内只标记一次

### 代码位置
文件：`/home/user/webapp/source_code/templates/anchor_system_real.html`

行号：
- 极端上涨标记：2330-2354行
- 极端暴跌标记：2356-2380行

## 📊 实际数据示例

### 当前状态（2026-02-03）
```
空单盈利统计：
- ≥300%: 0 (1小时内峰值: 0)
- ≥250%: 0 (1小时内峰值: 0)
- ≥200%: 0 (1小时内峰值: 0)
- ≥150%: 0 (1小时内峰值: 0)

极端标记：
- 极端上涨标记 (≥100%): 2 个
- 极端暴跌标记 (≤-80%): 26 个
```

### 控制台日志
```
✅ 空单盈利统计更新完成: {
    gte_150: 0, 
    gte_150_1h: 0, 
    gte_200: 0, 
    gte_200_1h: 0, 
    gte_250: 0
}

💥 极端上涨标记 (>=100%): 2 个
💀 极端暴跌标记 (<=-80%): 26 个
```

## 📦 修改的文件

1. `/home/user/webapp/source_code/templates/anchor_system_real.html`
   - 增大极端涨跌标记的fontSize（12→16）
   - 增大标记点symbolSize（80→90）
   - 调整标记偏移量offset（12→15）

2. `/home/user/webapp/templates/anchor_system_real.html`
   - 同步自source_code目录

## 🧪 测试结果

### 页面访问
- **URL**: https://5000-iehbqwjte74vmohs308jg-d0b9e1e2.sandbox.novita.ai/anchor-system-real
- **加载时间**: 33.76秒 ✅
- **进度显示**: 0% → 100% ✅
- **数据加载**: 所有卡片正常显示 ✅

### 高盈利卡片测试
- **300%卡片**: ✅ 显示正常（当前值: 0）
- **250%卡片**: ✅ 显示正常（当前值: 0）
- **200%卡片**: ✅ 显示正常（当前值: 0）
- **150%卡片**: ✅ 显示正常（当前值: 0）
- **数据更新**: ✅ 实时更新

### 图表标记测试
- **极端上涨标记**: ✅ 字体增大到16px
- **极端暴跌标记**: ✅ 字体增大到16px
- **标记点大小**: ✅ 从80增大到90
- **显示清晰度**: ✅ 明显改善

## 📈 数据流程图

```
coin_change_tracker.py (数据收集)
    ↓ 计算盈利统计
    ↓ 保存到JSONL文件
/api/coin-change-tracker/latest (API)
    ↓ 读取最新记录
    ↓ 返回short_stats
loadShortProfitStats() (前端)
    ↓ 解析数据
    ↓ 更新DOM元素
卡片显示（short300, short250, short200, short150）
```

## 🎨 卡片布局

```
┌────────────────┬────────────────┬────────────────┬────────────────┐
│   🏆 300%      │   ⭐ 250%      │   🔥 200%      │   ✅ 150%      │
│   紫色系       │   粉色系       │   橙色系       │   绿色系       │
│   当前: 0      │   当前: 0      │   当前: 0      │   当前: 0      │
│   1h内: 0      │   1h内: 0      │   1h内: 0      │   1h内: 0      │
└────────────────┴────────────────┴────────────────┴────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────────┐
│                    💎 空单盈利≥120%                                 │
│                    （其他低级别卡片...）                            │
└────────────────────────────────────────────────────────────────────┘
```

## 🔧 技术要点

### 1. 数据收集
- 每分钟采集一次主账户持仓数据
- 计算空单盈利比例
- 统计不同级别的空单数量
- 记录1小时内的峰值

### 2. 数据存储
- 文件格式：JSONL（每行一条JSON记录）
- 文件路径：`/home/user/webapp/data/coin_change_tracker/coin_change_YYYYMMDD.jsonl`
- 每条记录包含：时间戳、涨跌数据、空单统计

### 3. 前端展示
- 卡片使用渐变背景
- 超大字体（64px）显示主数值
- 副标题显示1小时内峰值
- 每30秒自动更新

### 4. 图表标记
- ECharts markPoint配置
- 自定义label formatter
- 动态symbolSize和fontSize
- 防止同一小时重复标记

## 🎯 完成状态

### 任务1: 高盈利卡片数据对接
- ✅ 后端数据收集（已完成）
- ✅ API接口（已完成）
- ✅ 前端数据加载（已完成）
- ✅ DOM元素更新（已完成）
- ✅ 实时刷新（已完成）

### 任务2: 图表数字增大
- ✅ 极端上涨标记字体增大（12→16px）
- ✅ 极端暴跌标记字体增大（12→16px）
- ✅ 标记点大小增大（80→90px）
- ✅ 偏移量调整（12→15px）
- ✅ 视觉效果改善

---

**完成时间**: 2026-02-03 17:40:00  
**版本**: v1.0  
**作者**: Claude AI Assistant  
**更新**: 2026-02-03
