# 2月份暴跌预警统计可视化

## 🎯 功能说明

这是一个交互式的柱状图统计页面，展示2026年2月份每一天的暴跌预警状态。

### 📊 可视化效果

- **绿色柱子**: 无预警的安全日期（16天）
- **红色柱子**: 有预警的危险日期（8天）
- **柱子高度**: 表示预警级别（critical > medium）
- **悬停提示**: 显示日期、预警类型、波峰数等详情

### 📈 统计数据

#### 总体统计
- **总天数**: 24天（2月1日-24日）
- **绿色（安全）**: 16天，占比 66.7%
- **红色（预警）**: 8天，占比 33.3%

#### 预警日期明细
| 日期 | 预警类型 | 级别 |
|------|---------|------|
| 2月2日 | A点递减（A2 > A3 > A4） | Critical |
| 2月5日 | A点递减（A1 > A2 > A3） | Critical |
| 2月6日 | A点递减（A2 > A3 > A4） | Critical |
| 2月7日 | A点递减（A1 > A2 > A3） | Critical |
| 2月9日 | A点递减（A1 > A2 > A3） | Critical |

#### 预警类型分布
- **A点递减模式**: 5天（2月2,5,6,7,9日）

---

## 🚀 访问方式

### 方式1: 直接访问统计页面

**URL**: https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai/february-warning-stats

点击链接即可查看完整的可视化统计图表。

### 方式2: 命令行生成

如果统计文件不存在或需要重新生成：

```bash
cd /home/user/webapp
python3 scripts/generate_warning_chart.py
```

生成后访问: https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai/february-warning-stats

---

## 🎨 页面设计特点

### 1. 汇总统计卡片

顶部展示三个渐变色卡片：
- **紫色卡片**: 总天数（24天）
- **绿色卡片**: 无预警天数（16天，66.7%）
- **红色卡片**: 有预警天数（8天，33.3%）

### 2. 柱状图

- **24根柱子**: 每根代表一天
- **绿色柱子**: 高度固定为60px，表示安全
- **红色柱子**: 
  - Critical级别：200px高
  - Medium级别：150px高
- **交互效果**: 鼠标悬停显示详细tooltip

### 3. 图例说明

底部展示颜色对应的含义：
- 🟢 绿色 = 无预警（安全）
- 🔴 红色 = 有预警（危险）

### 4. 响应式设计

- 支持桌面和移动设备
- 在窄屏幕上自动调整布局
- 柱子宽度和间距自适应

---

## 🔧 技术实现

### 生成脚本

**文件**: `/home/user/webapp/scripts/generate_warning_chart.py`

**功能**:
1. 读取 `data/crash_warning_events/february_analysis.json`
2. 提取预警日期和类型
3. 生成完整的2月份日期列表（1-24日）
4. 为每天标记预警状态
5. 生成HTML静态页面
6. 保存到 `static/february_warning_stats.html`

### Flask路由

**文件**: `/home/user/webapp/app.py`

**路由**: `/february-warning-stats`

**功能**:
- 检查静态HTML文件是否存在
- 如果不存在，自动调用生成脚本
- 返回HTML页面给浏览器

---

## 📝 数据来源

### 原始数据

**文件**: `/home/user/webapp/data/crash_warning_events/february_analysis.json`

**生成方式**:
```bash
cd /home/user/webapp
python3 scripts/check_february_crash_warnings.py
```

**数据结构**:
```json
{
  "analysis_time": "2026-02-24 12:46:55",
  "month": "2026-02",
  "summary": {
    "total_days": 24,
    "valid_days": 23,
    "warning_days": 8,
    "warning_rate": "34.8%"
  },
  "crash_warning_days": [
    {
      "date": "2026-02-02",
      "warning": {
        "signal_type": "crash_warning_amplifying",
        "pattern_name": "情况8：暴跌幅度递增（后3波）",
        "warning_level": "critical",
        ...
      },
      "peaks_count": 6
    },
    ...
  ],
  "all_results": [...]
}
```

---

## 🎯 使用案例

### 案例1: 快速查看2月预警分布

1. 打开浏览器访问: https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai/february-warning-stats
2. 查看顶部汇总卡片，了解总体预警率
3. 浏览柱状图，一目了然地看出哪些天有预警
4. 鼠标悬停在红色柱子上，查看具体预警类型

### 案例2: 分析预警模式

1. 观察红色柱子的分布
2. 发现预警集中在2月上旬和中旬
3. 2月6-7日连续两天预警（关键风险期）
4. 2月下旬预警减少（市场趋稳）

### 案例3: 导出统计报告

生成的HTML文件可以：
- 直接保存到本地
- 分享给其他人查看
- 嵌入到其他系统中
- 打印为PDF报告

---

## ⚙️ 自定义配置

### 修改颜色

编辑 `scripts/generate_warning_chart.py`，找到CSS样式部分：

```python
# 绿色柱子
.bar.green {
    background: linear-gradient(180deg, #48bb78 0%, #38a169 100%);
}

# 红色柱子
.bar.red.critical {
    background: linear-gradient(180deg, #f56565 0%, #e53e3e 100%);
}
```

### 修改柱子高度

```python
# 绿色柱子高度
.bar.green {
    height: 60px;  # 修改这里
}

# 红色Critical高度
.bar.red.critical {
    height: 200px;  # 修改这里
}

# 红色Medium高度
.bar.red.medium {
    height: 150px;  # 修改这里
}
```

### 修改图表高度

```css
.chart {
    height: 400px;  /* 修改这里 */
}
```

---

## 🔄 重新生成统计

### 场景1: 数据更新后

如果运行了新的预警分析，需要重新生成图表：

```bash
cd /home/user/webapp
python3 scripts/check_february_crash_warnings.py  # 更新分析数据
python3 scripts/generate_warning_chart.py         # 重新生成图表
```

### 场景2: 修改样式后

如果修改了生成脚本，需要重新生成：

```bash
cd /home/user/webapp
python3 scripts/generate_warning_chart.py
```

刷新浏览器页面即可看到更新。

---

## 📊 数据准确性

### 验证方式

1. **检查原始数据**:
   ```bash
   cat data/crash_warning_events/february_analysis.json | jq '.summary'
   ```

2. **统计预警天数**:
   ```bash
   cat data/crash_warning_events/february_analysis.json | jq '.crash_warning_days | length'
   ```

3. **查看具体日期**:
   ```bash
   cat data/crash_warning_events/february_analysis.json | jq '.crash_warning_days[].date'
   ```

### 已知限制

- 只包含2月1-24日的数据（2月25-28日未分析）
- 数据来源于波峰检测算法，依赖基线价格准确性
- 预警判断基于固定规则，可能存在误报或漏报

---

## 🆘 常见问题

### Q1: 页面显示错误？

**检查步骤**:
1. 确认Flask应用运行正常: `pm2 list | grep flask-app`
2. 查看错误日志: `pm2 logs flask-app --err --lines 20`
3. 手动生成图表: `python3 scripts/generate_warning_chart.py`

### Q2: 数据不对？

**可能原因**:
- 分析数据过时，需要重新运行 `check_february_crash_warnings.py`
- JSON文件损坏，检查文件完整性
- 波峰检测逻辑变更，需要重新分析

**解决方案**:
```bash
cd /home/user/webapp
python3 scripts/check_february_crash_warnings.py  # 重新分析
python3 scripts/generate_warning_chart.py         # 重新生成
```

### Q3: 如何添加其他月份？

**步骤**:
1. 修改 `check_february_crash_warnings.py` 分析其他月份
2. 修改 `generate_warning_chart.py` 的日期范围
3. 生成新的HTML文件
4. 在app.py中添加新路由

---

## 📞 技术支持

- **Web界面**: https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai/coin-change-tracker
- **统计页面**: https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai/february-warning-stats
- **GitHub**: https://github.com/jamesyidc/1212335551
- **PR #1**: https://github.com/jamesyidc/1212335551/pull/1

---

**最后更新**: 2026-02-24  
**版本**: v1.0  
**状态**: ✅ 生产就绪
