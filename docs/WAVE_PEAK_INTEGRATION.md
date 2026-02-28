# 波峰检测与假突破告警功能集成文档

## 功能概述

本文档记录了波峰检测与假突破告警功能在27币涨跌幅追踪系统中的完整集成过程。

## 波峰检测算法

### 核心定义

#### B-A-C 三点波峰结构
- **B点（谷底）**: 15分钟滚动窗口内的最低点
- **A点（峰顶）**: B点之后15分钟窗口内的最高点  
- **C点（反弹点）**: A点下跌超过振幅50%后止跌反弹的点

#### 波峰成立条件
1. **振幅要求**: B到A的涨幅差 > 40%
2. **回调要求**: A到C的跌幅 > (A-B) * 50%
3. **时间要求**: B、A、C均需在不同的15分钟窗口内

### 假突破判定逻辑

当满足以下条件时，系统判定为"假突破"，市场可能转跌：

```
连续3个波峰的A点（峰顶）均未突破第1个波峰的前高
```

**判定规则**:
- 检测最近的连续3个波峰
- 第2个波峰的A点 ≤ 第1个波峰的A点
- 第3个波峰的A点 ≤ 第1个波峰的A点
- 触发假突破告警

### 实现细节

#### 后端API
**接口**: `GET /api/coin-change-tracker/wave-peaks`

**参数**:
- `date` (可选): 查询日期，格式YYYY-MM-DD或YYYYMMDD，默认今天

**响应示例**:
```json
{
  "success": true,
  "date": "20260218",
  "peaks_count": 2,
  "false_breakout": {
    "consecutive_peaks": 3,
    "reference_high": 34.96,
    "peaks": [
      {
        "b_point": {"time": "2026-02-18 01:13:04", "value": -9.93},
        "a_point": {"time": "2026-02-18 03:14:41", "value": 34.96},
        "c_point": {"time": "2026-02-18 03:52:33", "value": 12.00},
        "amplitude": 44.89,
        "decline_ratio": 51.1
      },
      {
        "b_point": {"time": "2026-02-18 01:45:48", "value": -19.24},
        "a_point": {"time": "2026-02-18 03:14:41", "value": 34.96},
        "c_point": {"time": "2026-02-18 04:07:47", "value": 6.56},
        "amplitude": 54.20,
        "decline_ratio": 52.4
      },
      {
        "b_point": {"time": "2026-02-18 02:10:15", "value": -15.80},
        "a_point": {"time": "2026-02-18 03:20:10", "value": 30.15},
        "c_point": {"time": "2026-02-18 04:15:22", "value": 8.20},
        "amplitude": 45.95,
        "decline_ratio": 50.2
      }
    ]
  },
  "peaks": [...]
}
```

#### 前端可视化

##### 图表标记点
在ECharts趋势图上标记B-A-C三点：

| 点位 | 形状 | 颜色 | 标签示例 |
|-----|------|------|---------|
| B点 (谷底) | 圆形 | 青色 #06B6D4 | "波峰1-B\nB: -9.9%" |
| A点 (峰顶) | 三角形 | 橙色 #F59E0B | "波峰1-A\nA: 34.9%" |
| C点 (反弹点) | 菱形 | 紫色 #8B5CF6 | "波峰1-C\nC: 12.0%" |

**实现代码片段**:
```javascript
markPoint: {
    data: (function() {
        const points = [...]; // 最高价、最低价标记
        
        // 添加波峰标记
        if (wavePeaksData && wavePeaksData.length > 0) {
            wavePeaksData.forEach((peak, peakIdx) => {
                // B点
                points.push({
                    name: `波峰${peakIdx+1}-B`,
                    value: `B: ${peak.b_point.value.toFixed(1)}%`,
                    symbol: 'circle',
                    symbolSize: 12,
                    itemStyle: { color: '#06B6D4' }
                });
                // A点、C点类似...
            });
        }
        return points;
    })()
}
```

##### 假突破告警框

**位置**: BTC状态框与图表之间

**触发条件**: `falseBreakout !== null`

**告警内容**:
1. **标题**: "检测到假突破 - 市场可能转跌"
2. **说明**: 显示连续波峰数量和参考前高
3. **波峰详情**: 3个波峰的B、A点和振幅数据
4. **交易建议**:
   - 谨慎追高，建议观望或减仓
   - 关注是否跌破第3波峰的B点支撑位
   - 等待明确的反转信号后再考虑入场

**样式特征**:
- 渐变背景: 红色至橙色 (#FEF2F2 → #FFF7ED)
- 左侧红色边框 (4px)
- 警告图标: fas fa-exclamation-triangle

## 数据流程

### 1. 数据采集
- 数据源: `data/coin_change_tracker/coin_change_YYYYMMDD.jsonl`
- 采集频率: 每分钟一次
- 数据字段: `timestamp`, `beijing_time`, `total_change`, `changes`

### 2. 波峰检测
- 触发: 用户访问页面或切换日期
- 处理: Python后端 `WavePeakDetector` 类
- 输出: 波峰列表 + 假突破判定

### 3. 前端渲染
- 加载波峰数据: `updateHistoryData()` 函数中
- 标记点绘制: ECharts markPoint配置
- 告警框更新: `updateWavePeakAlert()` 函数

## 使用场景

### 场景1: 正常波峰显示
当市场出现明显的B-A-C波峰结构时：
- 图表上显示彩色标记点
- 无假突破告警
- 用户可清晰看到波峰结构

### 场景2: 假突破告警
当连续3个波峰未突破前高时：
- 图表显示3个波峰的B-A-C点
- 告警框自动展开，显示黄色警告
- 提供具体的交易建议

### 场景3: 历史回溯
用户可通过日期选择器：
- 查看历史任意日期的波峰
- 分析假突破信号的准确性
- 优化交易策略

## 技术要点

### 性能优化
1. **异步加载**: 波峰数据与历史数据、RSI数据并行加载
2. **缓存策略**: 添加 `no-cache` 头确保数据实时性
3. **按需渲染**: 只在有假突破信号时显示告警框

### 错误处理
```javascript
try {
    const wavePeaksResponse = await fetch(wavePeaksUrl, {...});
    const wavePeaksResult = await wavePeaksResponse.json();
    
    if (wavePeaksResult.success && wavePeaksResult.peaks) {
        wavePeaksData = wavePeaksResult.peaks;
        falseBreakout = wavePeaksResult.false_breakout;
    } else {
        console.log('⚠️ 波峰数据为空或检测失败');
    }
} catch (e) {
    console.warn('⚠️ 波峰数据加载失败:', e);
}
```

### 兼容性
- **浏览器要求**: 支持ES6 async/await
- **ECharts版本**: 5.x+
- **图表库**: 自动适配现有趋势图配置

## 测试验证

### API测试
```bash
# 测试今天的波峰数据
curl "http://localhost:9002/api/coin-change-tracker/wave-peaks"

# 测试指定日期
curl "http://localhost:9002/api/coin-change-tracker/wave-peaks?date=2026-02-18"
```

### 前端测试
1. 访问: https://9002-xxx.sandbox.novita.ai/coin-change-tracker
2. 检查浏览器控制台日志:
   - `✅ 波峰数据加载成功，波峰数量: X`
   - `⚠️ 检测到假突破信号！`
3. 验证图表标记点显示正确
4. 验证告警框在有假突破时自动显示

## 文件清单

### 新增文件
- `/home/user/webapp/source_code/wave_peak_detector.py` - 波峰检测算法
- `/home/user/webapp/docs/WAVE_PEAK_DETECTION.md` - 算法文档
- `/home/user/webapp/docs/WAVE_PEAK_INTEGRATION.md` - 本文档

### 修改文件
- `/home/user/webapp/app.py` - 添加 `/api/coin-change-tracker/wave-peaks` 接口
- `/home/user/webapp/templates/coin_change_tracker.html` - 集成前端可视化

## Git提交记录

```bash
# 提交1: 波峰检测算法实现
commit 0fd8f39
feat: 实现B-A-C波峰检测算法

# 提交2: 功能集成
commit c66fba8
feat: 添加波峰检测与假突破告警功能
- 新增波峰检测API接口
- 实现前端图表标记和告警框
- 动态显示波峰信息和假突破状态
```

## 后续优化建议

### 短期优化
1. **参数可配置**: 将40%振幅、50%回调阈值改为可配置参数
2. **音效告警**: 假突破信号触发时播放声音提示
3. **移动端优化**: 告警框在小屏设备上的响应式布局

### 长期优化
1. **机器学习**: 基于历史假突破信号训练预测模型
2. **多周期分析**: 支持5分钟、30分钟、1小时多周期波峰检测
3. **实时推送**: WebSocket实时推送假突破告警到移动设备

## 维护说明

### 日常监控
- 检查波峰检测API响应时间 (< 200ms)
- 验证假突破信号准确率
- 收集用户反馈优化阈值参数

### 故障排查
| 问题 | 可能原因 | 解决方案 |
|-----|---------|---------|
| API返回空数组 | 数据振幅不足40% | 正常情况，当天无波峰 |
| 告警框不显示 | falseBreakout为null | 检查是否有连续3个波峰 |
| 标记点位置错误 | 时间格式不匹配 | 确认beijing_time格式正确 |

## 联系方式

如有问题或建议，请联系：
- 开发者: GenSpark AI Assistant
- 项目: 27币涨跌幅追踪系统
- 日期: 2026-02-18
