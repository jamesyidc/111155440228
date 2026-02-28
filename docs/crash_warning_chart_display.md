# 趋势图暴跌预警标记显示功能

## 概述

在趋势图（27币涨跌幅之和）上添加暴跌预警标记，当检测到A点递减（A1 > A2 > A3）的暴跌预警模式时，在图表的A3点位置显示醒目的红色钻石标记。

## 实现时间

2026-02-26

## 修改内容

### 1. 数据加载（templates/coin_change_tracker.html）

**位置**: `updateHistoryData()` 函数中波峰数据加载部分

```javascript
// 将暴跌预警数据保存到全局变量，供趋势图使用
if (crashWarning) {
    window.crashWarningData = {
        has_warning: true,
        warnings: [{
            peaks: wavePeaksData,
            ...crashWarning
        }]
    };
} else {
    window.crashWarningData = { has_warning: false };
}
```

**功能**: 
- 从 `/api/coin-change-tracker/wave-peaks` API 获取暴跌预警数据
- 将数据保存到 `window.crashWarningData` 全局变量
- 确保趋势图配置可以访问这些数据

### 2. 图表标记（templates/coin_change_tracker.html）

**位置**: 趋势图 series[0].markPoint.data 配置

```javascript
// 添加暴跌预警标记
if (window.crashWarningData && window.crashWarningData.has_warning) {
    const warnings = window.crashWarningData.warnings || [];
    warnings.forEach((warning, idx) => {
        // 获取A3点（第三个A点）的时间，作为预警显示位置
        const peaks = warning.peaks || [];
        if (peaks.length >= 3) {
            // 从波峰结构中获取A3点时间
            const a3Peak = peaks[2];
            const a3TimeStr = a3Peak.a_point?.beijing_time || a3Peak.a_point_time || '';
            
            // 提取时间部分（HH:MM:SS）
            let a3Time = a3TimeStr;
            if (a3TimeStr.includes(' ')) {
                // 格式：2026-02-26 14:30:00 -> 14:30:00
                a3Time = a3TimeStr.split(' ')[1];
            }
            
            console.log('🚨 尝试在图表上标记暴跌预警，A3点时间:', a3Time);
            
            // 查找对应的时间索引
            const timeIndex = times.findIndex(t => t && t.startsWith(a3Time.substring(0, 5))); // 匹配 HH:MM
            
            if (timeIndex >= 0) {
                console.log('✅ 找到A3点在图表中的位置，索引:', timeIndex, '时间:', times[timeIndex]);
                points.push({
                    name: '🚨暴跌预警',
                    value: '暴跌预警',
                    xAxis: timeIndex,
                    yAxis: changes[timeIndex],
                    itemStyle: {
                        color: '#DC2626',  // 深红色
                        borderColor: '#fff',
                        borderWidth: 3
                    },
                    label: {
                        formatter: '🚨暴跌预警',
                        fontSize: 14,
                        fontWeight: 'bold',
                        color: '#DC2626',
                        show: true,
                        position: 'top',
                        backgroundColor: 'rgba(254, 226, 226, 0.95)',  // 红色背景
                        padding: [8, 12],
                        borderRadius: 8,
                        borderColor: '#DC2626',
                        borderWidth: 2
                    },
                    symbol: 'diamond',  // 钻石形状，更醒目
                    symbolSize: 20
                });
            } else {
                console.warn('⚠️ 未找到A3点在图表中的位置，A3时间:', a3Time, '图表时间范围:', times[0], '-', times[times.length - 1]);
            }
        }
    });
}
```

**功能**:
- 检查 `window.crashWarningData` 是否存在暴跌预警
- 提取A3点的时间信息（支持两种时间格式）
- 在趋势图时间轴上查找A3点的索引位置
- 添加红色钻石标记，显示 "🚨暴跌预警" 文字

## 标记样式

### 视觉效果

- **符号**: 钻石形状 (`diamond`)
- **符号大小**: 20px
- **符号颜色**: 深红色 (`#DC2626`)
- **边框**: 白色，3px宽

### 标签样式

- **文本**: 🚨暴跌预警
- **字体大小**: 14px
- **字体粗细**: 加粗
- **文字颜色**: 深红色 (`#DC2626`)
- **背景色**: 浅红色半透明 (`rgba(254, 226, 226, 0.95)`)
- **内边距**: 上下8px，左右12px
- **圆角**: 8px
- **边框**: 深红色，2px宽
- **位置**: 标记点上方 (`top`)

## 触发条件

当满足以下条件时，趋势图上会显示暴跌预警标记：

1. 波峰检测API返回 `crash_warning` 不为空
2. `crash_warning.peaks` 至少包含3个波峰
3. A1、A2、A3点呈递减趋势（A1 > A2 > A3）
4. A3点的时间在趋势图的时间轴范围内

## 数据流程

```
API: /api/coin-change-tracker/wave-peaks
  ↓
返回 crash_warning 数据
  ↓
保存到 window.crashWarningData
  ↓
趋势图渲染时读取数据
  ↓
在A3点位置添加标记
  ↓
显示红色钻石标记
```

## 测试用例

### 测试日期: 2026-02-26

**API返回数据**:
```json
{
  "crash_warning": {
    "pattern_name": "A点递减（A1 > A2 > A3）",
    "warning": "🚨 暴跌预警！波峰1-2-3 A点递减（A1 > A2 > A3），即将暴跌",
    "operation_tip": "逢高做空",
    "warning_level": "critical",
    "peaks": [
      {
        "a_point": {
          "beijing_time": "2026-02-26 05:37:22",
          "value": 124.25
        }
      },
      {
        "a_point": {
          "beijing_time": "2026-02-26 08:22:43",
          "value": 35.77
        }
      },
      {
        "a_point": {
          "beijing_time": "2026-02-26 12:40:48",
          "value": 29.73
        }
      }
    ],
    "comparisons": {
      "a_values": {
        "a1": 124.25,
        "a2": 35.77,
        "a3": 29.73,
        "a2_vs_a1": {
          "diff": -88.48,
          "diff_pct": -71.21
        },
        "a3_vs_a2": {
          "diff": -6.04,
          "diff_pct": -16.89
        }
      }
    }
  }
}
```

**控制台日志**:
```
🚨 检测到暴跌预警！ {pattern_name: "A点递减（A1 > A2 > A3）", ...}
🚨 尝试在图表上标记暴跌预警，A3点时间: 12:40:48
✅ 找到A3点在图表中的位置，索引: 595 时间: 12:40:48
```

**效果**:
- 在趋势图的12:40位置显示红色钻石标记
- 标记上方显示 "🚨暴跌预警" 标签
- 标签为红色背景，醒目易识别

## 调试信息

### 关键日志

1. **数据加载**:
   ```
   ✅ 波峰数据加载成功，波峰数量: 3
   🚨 检测到暴跌预警！
   ```

2. **标记添加**:
   ```
   🚨 尝试在图表上标记暴跌预警，A3点时间: 12:40:48
   ✅ 找到A3点在图表中的位置，索引: 595 时间: 12:40:48
   ```

3. **标记显示**:
   ```
   ✅ 完整波峰标记点添加完成，总标记点数: 13
   ```

### 常见问题

**Q: 标记不显示？**

A: 检查以下几点：
1. 确认API返回了 `crash_warning` 数据
2. 检查控制台是否有 "🚨 检测到暴跌预警！" 日志
3. 确认A3点时间在图表时间范围内
4. 查看是否有 "⚠️ 未找到A3点在图表中的位置" 警告

**Q: 时间匹配失败？**

A: 代码支持两种时间格式：
- 完整格式: `2026-02-26 12:40:48`
- 简短格式: `12:40:48`

如果A3点时间格式不匹配，会导致查找失败。代码会自动提取时间部分并匹配前5个字符（HH:MM）。

## Git提交

**Commit**: 9541c81

**消息**:
```
feat: 在趋势图上显示暴跌预警标记

修改内容：
1. 将crashWarning数据保存到window.crashWarningData，供趋势图使用
2. 修复A3点时间提取逻辑，支持两种时间格式
3. 在趋势图的markPoint中显示'🚨暴跌预警'标记
4. 使用钻石形状、红色背景的标记，显示在A3点位置
5. 添加详细的调试日志，便于排查问题

效果：
- 当检测到暴跌预警时，会在趋势图的A3点位置显示醒目的红色钻石标记
- 标记文字：🚨暴跌预警
- 样式：红色背景、钻石符号、加粗字体
```

## 相关文件

- `templates/coin_change_tracker.html`: 前端模板和JavaScript代码
- `app.py`: 波峰检测和暴跌预警API
- `source_code/wave_peak_detector.py`: 暴跌预警检测逻辑

## 后续优化建议

1. **点击交互**: 点击标记后显示详细的暴跌预警信息弹窗
2. **动画效果**: 添加闪烁或脉冲动画，更加醒目
3. **声音提示**: 页面首次加载时播放警报声
4. **历史记录**: 显示历史暴跌预警的触发次数和准确率
5. **自定义样式**: 允许用户自定义标记颜色和大小

## 效果演示

访问地址: `https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai/coin-change-tracker`

在2026-02-26的数据中，可以看到：
- 在12:40位置有一个红色钻石标记
- 标记上方显示 "🚨暴跌预警" 文字
- 与其他波峰标记（B点、A点、C点）区分明显
