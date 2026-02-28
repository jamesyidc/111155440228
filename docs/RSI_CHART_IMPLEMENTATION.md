# 27币RSI之和曲线功能实现文档

**实现日期**: 2026-02-18  
**Git Commit**: fd4691f  
**功能**: 添加27个币种的5分钟周期RSI(14)指标曲线图

## 📋 功能概述

在27币涨跌幅追踪系统中添加了RSI（相对强弱指标）曲线图，用于分析市场整体的超买超卖状态。

### 核心功能
- **RSI计算**: 使用5分钟K线数据，计算14周期RSI
- **数据采集**: 每5分钟采集一次27个币种的RSI值
- **RSI求和**: 将27个币种的RSI相加，得到总RSI值
- **曲线展示**: 在前端以折线图形式展示RSI之和的变化趋势
- **参考线**: 显示超买线(1890)、中性线(1350)、超卖线(810)

## 🔧 后端实现

### 1. 修改采集器 (`source_code/coin_change_tracker_collector.py`)

#### 添加依赖
```python
import numpy as np
```

#### RSI计算函数
```python
def calculate_rsi(prices, period=14):
    """
    计算RSI指标
    :param prices: 价格列表(从旧到新)
    :param period: RSI周期，默认14
    :return: RSI值 (0-100)
    """
    if len(prices) < period + 1:
        return None
    
    # 计算价格变化
    deltas = np.diff(prices)
    
    # 分离涨跌
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    # 计算平均涨跌
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    
    # 避免除零
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)
```

#### 获取5分钟K线数据
```python
def get_5min_candles(symbol, limit=20):
    """
    获取5分钟K线数据
    :param symbol: 币种符号
    :param limit: 获取K线数量，默认20根（足够计算RSI14）
    :return: 收盘价列表(从旧到新)
    """
    try:
        # 优先使用永续合约
        url = f"https://www.okx.com/api/v5/market/candles?instId={symbol}-USDT-SWAP&bar=5m&limit={limit}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        # 如果永续合约失败，尝试现货
        if data.get('code') != '0' or not data.get('data'):
            url = f"https://www.okx.com/api/v5/market/candles?instId={symbol}-USDT&bar=5m&limit={limit}"
            response = requests.get(url, timeout=5)
            data = response.json()
        
        if data.get('code') == '0' and data.get('data'):
            # K线数据格式: [时间戳, 开盘价, 最高价, 最低价, 收盘价, ...]
            # OKX返回的数据是从新到旧，需要反转
            candles = data['data']
            close_prices = [float(candle[4]) for candle in reversed(candles)]
            return close_prices
        else:
            print(f"[警告] {symbol} 5分钟K线获取失败")
            return None
            
    except Exception as e:
        print(f"[错误] {symbol} 获取5分钟K线失败: {e}")
        return None
```

#### 批量获取RSI
```python
def get_all_rsi_values():
    """
    获取所有27个币种的RSI值
    :return: 字典 {symbol: rsi_value}
    """
    rsi_values = {}
    
    for symbol in SYMBOLS:
        try:
            # 获取5分钟K线数据
            close_prices = get_5min_candles(symbol, limit=20)
            
            if close_prices and len(close_prices) >= 15:  # 至少需要15根K线来计算RSI14
                rsi = calculate_rsi(close_prices, period=14)
                if rsi is not None:
                    rsi_values[symbol] = rsi
                    print(f"[RSI] {symbol}: {rsi}")
            else:
                print(f"[警告] {symbol} K线数据不足，无法计算RSI")
            
            time.sleep(0.1)  # 避免请求过快
            
        except Exception as e:
            print(f"[错误] {symbol} 计算RSI失败: {e}")
            continue
    
    return rsi_values
```

#### 主循环修改
```python
# 检查是否需要采集RSI（每5分钟一次）
should_collect_rsi = False
if last_rsi_collect_time is None:
    should_collect_rsi = True
else:
    minutes_since_last = (now - last_rsi_collect_time).total_seconds() / 60
    if minutes_since_last >= 5:
        should_collect_rsi = True

# 获取RSI数据
rsi_values = {}
total_rsi = None
if should_collect_rsi:
    print("[RSI] 开始采集5分钟RSI数据...")
    rsi_values = get_all_rsi_values()
    if rsi_values:
        total_rsi = round(sum(rsi_values.values()), 2)
        print(f"[RSI] 27币RSI之和: {total_rsi}")
        last_rsi_collect_time = now

# 如果有RSI数据，添加到记录中
if rsi_values:
    record['rsi_values'] = rsi_values
    record['total_rsi'] = total_rsi
```

### 2. 数据格式

#### JSONL记录格式（包含RSI）
```json
{
    "timestamp": 1771395936298,
    "beijing_time": "2026-02-18 14:23:06",
    "cumulative_pct": 9.98,
    "total_change": 9.98,
    "up_ratio": 70.4,
    "up_coins": 19,
    "down_coins": 8,
    "changes": { ... },
    "count": 27,
    "rsi_values": {
        "BTC": 42.47,
        "ETH": 52.13,
        "BNB": 44.83,
        "XRP": 39.9,
        "DOGE": 59.31,
        "SOL": 48.65,
        ...
    },
    "total_rsi": 1260.47
}
```

## 🎨 前端实现

### 1. HTML结构

在趋势图下方添加RSI图表容器：

```html
<!-- RSI指标图表 -->
<div class="grid grid-cols-1 gap-6 mb-6">
    <div class="bg-white rounded-lg shadow-lg p-6">
        <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-bold">
                <i class="fas fa-chart-area text-purple-600 mr-2"></i>
                27币RSI之和曲线
            </h2>
            <div class="text-sm text-gray-600">
                <i class="fas fa-clock mr-1"></i>
                5分钟周期 RSI(14)
            </div>
        </div>
        <div class="mb-4 text-sm text-gray-600 bg-purple-50 p-3 rounded border border-purple-200">
            <p class="mb-2"><strong class="text-purple-700">指标说明：</strong></p>
            <ul class="list-disc list-inside space-y-1 ml-2">
                <li><strong>RSI(14)：</strong>相对强弱指标，周期为14根5分钟K线</li>
                <li><strong>取值范围：</strong>单个币种RSI为0-100，27币之和范围约为0-2700</li>
                <li><strong>超买超卖：</strong>RSI总和>1890（平均70）表示市场超买，<810（平均30）表示市场超卖</li>
                <li><strong>采集频率：</strong>每5分钟采集一次，与涨跌幅曲线（1分钟）不同步</li>
            </ul>
        </div>
        <!-- 参考线图例 -->
        <div class="flex flex-wrap gap-4 mb-3 text-sm">
            <span class="inline-flex items-center">
                <span class="inline-block w-8 h-0.5 bg-red-500 mr-1" style="border-top: 2px dashed;"></span>
                <span class="text-red-500 font-semibold">1890 (超买线)</span>
            </span>
            <span class="inline-flex items-center">
                <span class="inline-block w-8 h-0.5 bg-gray-500 mr-1" style="border-top: 2px dashed;"></span>
                <span class="text-gray-500 font-semibold">1350 (中性线)</span>
            </span>
            <span class="inline-flex items-center">
                <span class="inline-block w-8 h-0.5 bg-green-500 mr-1" style="border-top: 2px dashed;"></span>
                <span class="text-green-500 font-semibold">810 (超卖线)</span>
            </span>
        </div>
        <div id="rsiChart" style="height: 500px;"></div>
    </div>
</div>
```

### 2. JavaScript实现

#### 初始化RSI图表
```javascript
// 图表实例
let trendChart = null;
let rankChart = null;
let rsiChart = null;  // RSI图表实例

// 初始化图表
function initCharts() {
    const trendChartDom = document.getElementById('trendChart');
    const rankChartDom = document.getElementById('rankChart');
    const rsiChartDom = document.getElementById('rsiChart');
    
    trendChart = echarts.init(trendChartDom);
    rankChart = echarts.init(rankChartDom);
    rsiChart = echarts.init(rsiChartDom);
    
    // ... 其他配置
}
```

#### 更新RSI图表
```javascript
function updateRSIChart() {
    if (!rsiChart || !historyData || historyData.length === 0) {
        return;
    }
    
    // 筛选包含RSI数据的记录
    const rsiData = historyData.filter(d => d.total_rsi !== undefined && d.total_rsi !== null);
    
    if (rsiData.length === 0) {
        return;
    }
    
    // 提取时间和RSI值
    const times = rsiData.map(d => {
        const beijingTime = d.beijing_time || '';
        return beijingTime.split(' ')[1] || beijingTime;
    });
    
    const rsiValues = rsiData.map(d => d.total_rsi);
    
    // RSI图表配置
    rsiChart.setOption({
        tooltip: {
            trigger: 'axis',
            formatter: function(params) {
                const p = params[0];
                const value = p.value;
                const avgRsi = (value / 27).toFixed(2);
                
                // 判断市场状态
                let status = '中性';
                let statusColor = '#6B7280';
                if (value > 1890) {
                    status = '超买';
                    statusColor = '#EF4444';
                } else if (value < 810) {
                    status = '超卖';
                    statusColor = '#10B981';
                }
                
                return `
                    <div>
                        <div>${params[0].marker}27币RSI之和</div>
                        <div>${value.toFixed(2)}</div>
                        <div>平均RSI: ${avgRsi}</div>
                        <div>市场状态: <span style="color: ${statusColor}">${status}</span></div>
                    </div>
                `;
            }
        },
        xAxis: {
            type: 'category',
            data: times
        },
        yAxis: {
            type: 'value',
            min: 0,
            max: 2700
        },
        series: [{
            name: '27币RSI之和',
            type: 'line',
            data: rsiValues,
            smooth: true,
            lineStyle: { color: '#9333EA' },
            itemStyle: { color: '#9333EA' },
            areaStyle: {
                color: {
                    type: 'linear',
                    colorStops: [
                        { offset: 0, color: 'rgba(147, 51, 234, 0.3)' },
                        { offset: 1, color: 'rgba(147, 51, 234, 0.05)' }
                    ]
                }
            },
            markLine: {
                data: [
                    { yAxis: 1890, label: { formatter: '超买线 (1890)' }, lineStyle: { color: '#EF4444' } },
                    { yAxis: 1350, label: { formatter: '中性线 (1350)' }, lineStyle: { color: '#6B7280' } },
                    { yAxis: 810, label: { formatter: '超卖线 (810)' }, lineStyle: { color: '#10B981' } }
                ]
            }
        }]
    });
}
```

#### 调用时机
```javascript
// 在历史数据更新后调用
setTimeout(() => {
    trendChart.resize();
    updateRSIChart();  // 更新RSI图表
}, 100);

// 窗口resize时
window.addEventListener('resize', () => {
    trendChart.resize();
    rankChart.resize();
    if (rsiChart) {
        rsiChart.resize();
    }
});
```

## 📊 RSI指标说明

### RSI(14)计算公式
```
RS = 平均涨幅 / 平均跌幅
RSI = 100 - (100 / (1 + RS))
```

### 参考线说明
| 参考线 | 数值 | 说明 | 市场状态 |
|--------|------|------|----------|
| 超买线 | 1890 | 平均RSI=70 | 市场过热，可能回调 |
| 中性线 | 1350 | 平均RSI=50 | 市场平衡 |
| 超卖线 | 810 | 平均RSI=30 | 市场超卖，可能反弹 |

### 应用场景
1. **超买信号**: 当RSI之和>1890时，市场可能处于超买状态，短期内可能回调
2. **超卖信号**: 当RSI之和<810时，市场可能处于超卖状态，短期内可能反弹
3. **背离**: RSI与价格走势背离时，可能预示趋势反转

## 🧪 测试验证

### 1. 采集器日志验证
```bash
pm2 logs coin-change-tracker --nostream --lines 50 | grep RSI
```

**预期输出**:
```
23|coin-ch | [RSI] BTC: 42.47
23|coin-ch | [RSI] ETH: 52.13
23|coin-ch | [RSI] BNB: 44.83
...
23|coin-ch | [RSI] 27币RSI之和: 1260.47
23|coin-ch | [统计] 总涨跌幅: 9.98%, 币种数: 27, 上涨占比: 70.4%, RSI之和: 1260.47
```

### 2. JSONL数据验证
```bash
grep "total_rsi" data/coin_change_tracker/coin_change_20260218.jsonl | tail -1 | python3 -m json.tool
```

**预期输出**:
```json
{
    "rsi_values": {
        "BTC": 42.47,
        "ETH": 52.13,
        ...
    },
    "total_rsi": 1260.47
}
```

### 3. 前端图表验证

访问页面: `https://9002-xxx.sandbox.novita.ai/coin-change-tracker`

**检查项**:
- ✅ RSI图表容器正常显示
- ✅ 图表标题显示"27币RSI之和曲线"
- ✅ 三条参考线显示正确（1890、1350、810）
- ✅ 紫色曲线正常绘制
- ✅ Tooltip显示完整（RSI值、平均RSI、市场状态）
- ✅ 图表随窗口resize正常调整

## 🚀 部署状态

### 服务状态
```bash
pm2 status
```

- ✅ coin-change-tracker (PID 28832) - 正常运行
- ✅ flask-app (PID 29148) - 正常运行

### 文件修改
- ✅ `source_code/coin_change_tracker_collector.py` - 添加RSI采集功能
- ✅ `templates/coin_change_tracker.html` - 添加RSI图表

### Git提交
- **Commit**: fd4691f
- **Message**: feat(coin-change-tracker): 添加27币RSI之和曲线图

## 📝 注意事项

1. **采集频率**: RSI每5分钟采集一次，与价格涨跌幅（每1分钟）不同步
2. **数据完整性**: 只有包含`total_rsi`字段的记录才会显示在RSI图表中
3. **性能优化**: RSI计算使用numpy，需确保numpy已安装
4. **参考线意义**: 超买超卖线基于平均RSI=70和30，实际应用中可根据市场情况调整
5. **图表初始化**: RSI图表需要等待历史数据加载完成后才会显示

## 🔗 相关链接

- 页面URL: https://9002-xxx.sandbox.novita.ai/coin-change-tracker
- 数据目录: `/home/user/webapp/data/coin_change_tracker/`
- 采集器代码: `/home/user/webapp/source_code/coin_change_tracker_collector.py`
- 前端页面: `/home/user/webapp/templates/coin_change_tracker.html`

---

**最后更新**: 2026-02-18 14:30:00  
**更新人**: AI Assistant  
**状态**: ✅ 已实现并验证
