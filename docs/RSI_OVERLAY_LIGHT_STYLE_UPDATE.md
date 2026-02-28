# RSI曲线样式更新 - 浅色虚线与右侧刻度

## 📋 更新概述

根据用户需求，将RSI之和曲线样式更新为浅色虚线，并将刻度标记在图表右侧，以提供更清晰的视觉效果。

## 🎨 样式变更详情

### 1. **颜色更新**
- **原颜色**: 紫色 `#9333EA`
- **新颜色**: 浅灰色 `#D1D5DB`
- **理由**: 浅灰色作为辅助指标，不抢夺主曲线（涨跌幅）的视觉焦点

### 2. **线条样式**
- **线型**: 虚线（dashed）
- **线宽**: 2px
- **平滑**: 启用（smooth: true）
- **符号大小**: 从 4px 调整为 3px，更加精细

### 3. **Y轴配置**
```javascript
// 右侧Y轴 (yAxisIndex: 1)
{
    type: 'value',
    name: 'RSI之和',
    position: 'right',
    min: 0,
    max: 2700,
    interval: 270,
    axisLabel: {
        formatter: '{value}'
    },
    axisLine: {
        lineStyle: {
            color: '#D1D5DB'  // 轴线颜色与RSI曲线一致
        }
    },
    splitLine: {
        show: false  // 不显示网格线，避免干扰
    }
}
```

### 4. **参考线标记**
RSI曲线包含三条重要参考线（均使用右侧Y轴）：

- **超买线 (平均70)**: yAxis: 1890
  - 颜色: 红色 `#EF4444`
  - 含义: RSI总和 > 1890 表示市场整体超买

- **中性线 (平均50)**: yAxis: 1350
  - 颜色: 灰色 `#6B7280`
  - 含义: RSI总和 = 1350 表示市场中性

- **超卖线 (平均30)**: yAxis: 810
  - 颜色: 绿色 `#10B981`
  - 含义: RSI总和 < 810 表示市场整体超卖

## 📊 数据采集与存储

### **采集频率**
- **周期**: 5分钟（300秒）
- **触发条件**: 距离上次RSI采集已超过5分钟
- **质量保证**: 仅当成功获取 ≥20 个币种的RSI数据时才保存

### **数据存储**
RSI数据独立存储在单独的JSONL文件中：

**文件路径**: `data/coin_change_tracker/rsi_YYYYMMDD.jsonl`

**数据格式**:
```json
{
    "timestamp": 1771396946842,
    "beijing_time": "2026-02-18 14:42:06",
    "rsi_values": {
        "BTC": 65.53,
        "ETH": 67.24,
        "BNB": 58.18,
        ...
    },
    "total_rsi": 1703.17,
    "count": 27
}
```

### **API接口**
```
GET /api/coin-change-tracker/rsi-history?date=YYYYMMDD&limit=1440
```

**响应格式**:
```json
{
    "success": true,
    "date": "20260218",
    "count": 152,
    "data": [
        {
            "timestamp": 1771396946842,
            "beijing_time": "2026-02-18 14:42:06",
            "rsi_values": {...},
            "total_rsi": 1703.17,
            "count": 27
        },
        ...
    ]
}
```

## 💡 前端实现

### **双Y轴配置**
```javascript
yAxis: [
    {
        type: 'value',
        name: '涨跌幅 (%)',
        position: 'left',      // 左侧Y轴 - 涨跌幅
        axisLabel: {
            formatter: '{value}%'
        }
    },
    {
        type: 'value',
        name: 'RSI之和',
        position: 'right',     // 右侧Y轴 - RSI
        min: 0,
        max: 2700,
        axisLine: {
            lineStyle: {
                color: '#D1D5DB'
            }
        }
    }
]
```

### **RSI系列配置**
```javascript
{
    name: 'RSI之和',
    type: 'line',
    yAxisIndex: 1,           // 使用右侧Y轴
    smooth: true,
    data: rsiValues,
    lineStyle: {
        width: 2,
        type: 'dashed',      // 虚线样式
        color: '#D1D5DB'     // 浅灰色
    },
    itemStyle: {
        color: '#D1D5DB'
    },
    symbol: 'circle',
    symbolSize: 3,           // 小符号
    zlevel: 1                // 确保在主曲线上方
}
```

### **Tooltip增强**
鼠标悬停时同时显示涨跌幅和RSI信息：

```javascript
formatter: function(params) {
    // 显示涨跌幅
    const changeParam = params.find(p => p.seriesName === '27币涨跌幅之和');
    
    // 显示RSI及市场状态
    const rsiParam = params.find(p => p.seriesName === 'RSI之和');
    if (rsiParam) {
        const rsiValue = rsiParam.value;
        const avgRsi = (rsiValue / 27).toFixed(2);
        
        let status = '中性';
        let statusColor = '#6B7280';
        if (rsiValue > 1890) {
            status = '超买';
            statusColor = '#EF4444';
        } else if (rsiValue < 810) {
            status = '超卖';
            statusColor = '#10B981';
        }
        
        // 显示RSI信息...
    }
}
```

## ✅ 修改文件清单

1. **后端采集器**: `source_code/coin_change_tracker_collector.py`
   - 添加 RSI 计算函数 `calculate_rsi_for_symbol()`
   - 添加 `get_all_rsi_values()` 批量获取
   - 添加 `save_rsi_to_jsonl()` 独立存储
   - 更新主循环，每5分钟采集RSI

2. **后端API**: `app.py`
   - 添加 `/api/coin-change-tracker/rsi-history` 端点
   - 支持按日期和限制条数查询

3. **前端页面**: `templates/coin_change_tracker.html`
   - 更新 `initCharts()` 函数，配置双Y轴和RSI系列
   - 更新 `updateHistoryData()` 函数，加载RSI历史数据
   - 增强 tooltip 显示RSI信息和市场状态
   - 调整 RSI 曲线颜色为浅灰色 `#D1D5DB`
   - 调整 符号大小为 3px

## 🔍 验证方法

### 1. **检查RSI数据文件**
```bash
ls -lh data/coin_change_tracker/rsi_*.jsonl
tail -1 data/coin_change_tracker/rsi_20260218.jsonl | python3 -m json.tool
```

### 2. **测试API接口**
```bash
curl "http://127.0.0.1:9002/api/coin-change-tracker/rsi-history?date=20260218&limit=10"
```

### 3. **查看采集日志**
```bash
pm2 logs coin-change-tracker --nostream --lines 30
```

应显示：
- `[RSI] 成功采集 27/27 个币种，RSI之和: XXXX.XX`
- `[保存] RSI数据已写入 /home/user/webapp/data/coin_change_tracker/rsi_YYYYMMDD.jsonl`

### 4. **前端验证**
访问页面：https://9002-ixuizzbk8b8iyhwfxb9rl-5634da27.sandbox.novita.ai/coin-change-tracker

检查点：
- ✅ 图表右侧显示 "RSI之和" Y轴标签，颜色为浅灰色
- ✅ RSI曲线显示为浅灰色虚线
- ✅ 参考线正确显示（超买/中性/超卖）
- ✅ 鼠标悬停时tooltip显示涨跌幅和RSI信息
- ✅ 图表窗口缩放时曲线正确响应

## 📈 数据示例

### **RSI采集日志**
```
[RSI] BTC: 65.53
[RSI] ETH: 67.24
[RSI] BNB: 58.18
...
[RSI] 成功采集 27/27 个币种，RSI之和: 1703.17
[保存] RSI数据已写入 /home/user/webapp/data/coin_change_tracker/rsi_20260218.jsonl
```

### **API返回示例**
```json
{
    "success": true,
    "date": "20260218",
    "count": 152,
    "data": [
        {
            "timestamp": 1771396946842,
            "beijing_time": "2026-02-18 14:42:06",
            "rsi_values": {
                "BTC": 65.53,
                "ETH": 67.24,
                ...
            },
            "total_rsi": 1703.17,
            "count": 27
        }
    ]
}
```

## 🎯 视觉效果说明

### **主曲线（涨跌幅）**
- **颜色**: 蓝色 `#3B82F6`
- **样式**: 实线，带渐变填充
- **Y轴**: 左侧，显示百分比 (%)
- **视觉优先级**: 高（主要指标）

### **辅助曲线（RSI）**
- **颜色**: 浅灰色 `#D1D5DB`
- **样式**: 虚线
- **Y轴**: 右侧，显示数值 (0-2700)
- **视觉优先级**: 低（辅助参考）

### **配色方案**
- 超买：红色 `#EF4444` (RSI > 1890)
- 中性：灰色 `#6B7280` (810 ≤ RSI ≤ 1890)
- 超卖：绿色 `#10B981` (RSI < 810)

## 🚀 部署状态

- ✅ **代码提交**: commit `bdfee8d`
- ✅ **Flask重启**: PID 30907
- ✅ **PM2配置保存**: 已保存
- ✅ **RSI采集正常**: 27/27 币种成功
- ✅ **数据文件生成**: `rsi_20260218.jsonl`

## 📝 注意事项

1. **数据稀疏性**: RSI数据每5分钟采集一次，图表上的数据点相对稀疏，这是正常现象

2. **Y轴范围**: 
   - 左侧Y轴（涨跌幅）: 动态范围，根据数据自动调整
   - 右侧Y轴（RSI）: 固定范围 0-2700（27个币 × 100 RSI上限）

3. **失败容错**: 如果单个币种RSI获取失败，不影响整体数据采集，只要成功获取≥20个币种即可

4. **颜色对比**: 浅灰色虚线确保RSI曲线不会干扰主曲线的视觉焦点

5. **响应式设计**: 图表在窗口缩放时会自动调整大小（`window.addEventListener('resize', ...)`）

## 🔗 相关文档

- [RSI曲线叠加功能文档](./RSI_OVERLAY_FEATURE.md)
- [多策略配置支持](./MULTI_STRATEGY_CONFIG_SUPPORT.md)
- [账户切换UI同步修复](./ACCOUNT_SWITCH_UI_SYNC_FIX.md)

---

**更新时间**: 2026-02-18 14:45:00 UTC  
**状态**: ✅ 已完成并上线
