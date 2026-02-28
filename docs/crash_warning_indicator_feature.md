# 暴跌预警指示器功能说明

## 更新时间
2026-02-26

## 功能概述
在趋势图标题旁边添加了**暴跌预警指示器**，当系统检测到暴跌预警信号时，指示器会自动显示，提醒用户注意市场风险。

## 功能特点

### 1. 视觉设计
- **位置**：趋势图标题右侧
- **外观**：
  - 红色渐变背景（`bg-red-100`）
  - 红色边框（`border-red-500`，2px粗）
  - 红色文字（`text-red-700`）
  - 三角形警告图标（`fa-exclamation-triangle`）
  - 带动画效果（`animate-pulse`，呼吸灯效果）
- **文字内容**："触发了暴跌预警"

### 2. 显示逻辑
- **显示条件**：当后端检测到暴跌预警信号（`crashWarning !== null`）时显示
- **隐藏条件**：
  - 无暴跌预警信号时
  - 切换到没有暴跌预警的日期时
  - 数据加载失败时

### 3. 自动更新机制
- **实时响应**：随着日期切换自动更新显示状态
- **数据联动**：与波峰告警框（下方的详细告警信息）联动
- **错误处理**：数据加载异常时自动隐藏指示器

## 技术实现

### HTML 结构
```html
<div class="flex items-center gap-4">
    <h2 class="text-xl font-bold">
        <i class="fas fa-chart-area text-blue-600 mr-2"></i>
        总涨跌幅趋势
        ...
    </h2>
    <!-- 暴跌预警指示器 -->
    <div id="crashWarningIndicator" class="hidden">
        <span class="inline-flex items-center px-3 py-1 rounded-lg bg-red-100 border-2 border-red-500 text-red-700 font-semibold text-sm animate-pulse">
            <i class="fas fa-exclamation-triangle mr-2 text-red-600"></i>
            触发了暴跌预警
        </span>
    </div>
</div>
```

### JavaScript 函数
```javascript
// 更新暴跌预警指示器
function updateCrashWarningIndicator(crashWarning) {
    const indicator = document.getElementById('crashWarningIndicator');
    
    if (crashWarning) {
        // 显示暴跌预警指示器
        indicator.classList.remove('hidden');
        console.log('✅ 显示暴跌预警指示器');
    } else {
        // 隐藏暴跌预警指示器
        indicator.classList.add('hidden');
        console.log('ℹ️ 隐藏暴跌预警指示器');
    }
}
```

### 调用位置
在 `updateHistoryData()` 函数中，加载波峰数据后自动调用：

```javascript
// 更新波峰告警框
updateWavePeakAlert(wavePeaksData, falseBreakout, crashWarning);

// 更新暴跌预警指示器（新增）
updateCrashWarningIndicator(crashWarning);

// 更新B-A-C波峰详情框
updateWavePeakDetails(wavePeaksData, currentState);
```

## 数据流程

```
用户切换日期
    ↓
updateHistoryData(date)
    ↓
加载波峰数据 (API: /api/coin-change-tracker/wave-peaks)
    ↓
提取 crashWarning 字段
    ↓
保存到 window.crashWarningData
    ↓
调用 updateCrashWarningIndicator(crashWarning)
    ↓
显示/隐藏指示器
```

## 用户体验

### 优点
1. **位置醒目**：紧邻趋势图标题，用户第一眼就能看到
2. **视觉突出**：红色警告色+动画效果，吸引注意力
3. **即时反馈**：日期切换后立即更新状态
4. **一致性**：与下方详细告警框保持一致的数据源

### 使用场景
1. **实时监控**：用户查看当天趋势图时，立即知道是否有暴跌预警
2. **历史回顾**：切换历史日期时，快速了解该日期是否有预警
3. **风险提示**：作为快速的视觉提示，引导用户查看详细告警信息

## 与其他功能的关系

### 暴跌预警系统的三层展示
1. **第一层（新增）**：趋势图标题旁的指示器
   - 作用：快速提示
   - 信息：简单的"是/否"状态
   
2. **第二层（已有）**：波峰告警框
   - 作用：详细信息展示
   - 信息：A点/B点数值、递减趋势、具体比较等
   
3. **第三层（已有）**：图表上的标记点
   - 作用：在趋势图上标注预警位置
   - 信息：A3点时间位置、图标标记

## 测试验证

### 测试步骤
1. 访问页面：https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai/coin-change-tracker
2. 切换到有暴跌预警的日期（例如：2026-02-05、2026-02-06等）
3. 观察趋势图标题右侧是否显示红色预警指示器
4. 切换到无预警的日期，观察指示器是否隐藏
5. 检查浏览器控制台日志确认函数调用情况

### 预期结果
- 有暴跌预警的日期：指示器显示，并带动画效果
- 无暴跌预警的日期：指示器隐藏
- 控制台日志：显示相应的"显示/隐藏"日志

## 相关文件
- **模板文件**：`templates/coin_change_tracker.html`
  - 新增HTML元素（第3800-3820行附近）
  - 新增JavaScript函数（第8935-8952行）
  - 更新调用位置（第8039行、第8065行、第8068行）

## 后续优化建议
1. 可以考虑添加点击指示器跳转到详细告警框的功能
2. 可以显示预警的具体类型（如"A点递减"、"B点递减"等）
3. 可以添加预警触发时间的悬浮提示

## Git 提交记录
- Commit: c3d4580
- Message: "feat: 在趋势图标题旁显示暴跌预警指示器"
- Date: 2026-02-26
