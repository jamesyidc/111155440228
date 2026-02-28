# RSI自动开仓策略 - 执行许可重置功能

## 📋 功能概述

为"RSI自动开仓策略"添加了**重置执行许可**功能，允许用户手动重置策略的触发状态，使已执行过的策略可以再次执行。

## 🎯 功能特点

### 1. 用户界面
- **重置按钮位置**：在"🚀 RSI自动开仓策略"卡片标题栏的右侧
- **按钮样式**：橙色渐变主题，与卡片颜色协调
- **交互效果**：
  - Hover悬停：背景色变深，按钮上移1px，显示阴影
  - Active点击：恢复原位，阴影消失
  - 点击前确认：显示确认对话框，避免误操作

### 2. 重置范围
重置按钮会同时重置**两个**RSI自动开仓策略的执行许可：
1. **见顶信号 + 涨幅前8做空** (`top8_short`)
2. **见顶信号 + 涨幅后8做空** (`bottom8_short`)

### 3. 使用场景
- 策略已触发并进入1小时冷却期，但希望立即重新触发
- 测试策略执行逻辑
- 市场情况变化，需要重新评估开仓机会

## 🔧 技术实现

### 前端实现

#### HTML按钮
```html
<button onclick="resetRsiStrategyExecution()" 
        class="btn-reset-rsi"
        style="padding: 4px 12px; background: #f59e0b; color: white; ...">
    🔄 重置执行许可
</button>
```

#### JavaScript函数
```javascript
async function resetRsiStrategyExecution() {
    const account = accounts.find(acc => acc.id === currentAccount);
    if (!account) {
        alert('❌ 请先选择账户');
        return;
    }
    
    // 确认操作
    if (!confirm('确认重置执行许可吗？\n\n重置后，已触发的策略将可以再次执行。')) {
        return;
    }
    
    // 重置两个策略
    const strategies = ['top8_short', 'bottom8_short'];
    for (const strategy of strategies) {
        await fetch(`/api/okx-trading/set-allowed-top-signal/${account.id}/${strategy}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                allowed: true,
                reason: '用户手动重置执行许可'
            })
        });
    }
}
```

#### CSS样式
```css
.btn-reset-rsi:hover {
    background: #d97706 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.btn-reset-rsi:active {
    transform: translateY(0);
    box-shadow: none;
}
```

### 后端API

#### API路由
```
POST /api/okx-trading/set-allowed-top-signal/<account_id>/<strategy_type>
```

#### 请求体
```json
{
    "allowed": true,
    "reason": "用户手动重置执行许可"
}
```

#### 响应
```json
{
    "success": true,
    "message": "Top signal top8_short execution allowed status set to true",
    "record": {
        "timestamp": "2026-02-21T11:45:00",
        "account_id": "account_main",
        "strategy_type": "top8_short",
        "allowed": true,
        "reason": "用户手动重置执行许可"
    }
}
```

#### JSONL文件更新
API会更新以下JSONL文件的**第一行**（文件头）：
```
data/okx_auto_strategy/{account_id}_top_signal_{strategy_type}_execution.jsonl
```

文件头格式：
```json
{
    "allowed": true,
    "timestamp": "2026-02-21T11:45:00",
    "reason": "用户手动重置执行许可"
}
```

## 📊 执行流程

```
用户点击"🔄 重置执行许可"按钮
    ↓
显示确认对话框
    ↓
用户确认
    ↓
遍历两个策略 (top8_short, bottom8_short)
    ↓
调用后端API设置 allowed=true
    ↓
后端更新JSONL文件头
    ↓
前端显示操作结果
    ↓
后台监控脚本读取新的 allowed 状态
    ↓
满足条件时策略可再次执行
```

## 🔒 安全机制

### 1. 用户确认
```javascript
if (!confirm('确认重置执行许可吗？\n\n重置后，已触发的策略将可以再次执行。')) {
    return;
}
```

### 2. 账户验证
```javascript
const account = accounts.find(acc => acc.id === currentAccount);
if (!account) {
    alert('❌ 请先选择账户');
    return;
}
```

### 3. 错误处理
```javascript
try {
    // API调用
} catch (e) {
    alert(`❌ 重置失败: ${e.message}`);
}
```

### 4. 操作反馈
```javascript
// 成功
alert(`✅ 重置成功！\n\n账户：${account.name}\n已重置 ${successCount} 个策略的执行许可`);

// 部分成功
alert(`⚠️ 部分成功\n\n成功：${successCount} 个\n失败：${errors.length} 个`);

// 全部失败
alert(`❌ 重置失败\n\n${errors.join('\n')}`);
```

## 🎨 UI效果

### 按钮状态
| 状态 | 背景色 | 效果 | 阴影 |
|------|--------|------|------|
| Normal | #f59e0b | - | 无 |
| Hover | #d97706 | translateY(-1px) | 0 4px 6px rgba(0,0,0,0.1) |
| Active | #d97706 | translateY(0) | 无 |

### 卡片布局
```
┌────────────────────────────────────────────────────────────┐
│  🚀 RSI自动开仓策略                     [🔄 重置执行许可]  │
│  ───────────────────────────────────────────────────────── │
│  💡 说明：基于市场情绪信号和RSI指标自动开仓...              │
│                                                            │
│  ⚠️ 见顶信号+涨幅前8做空                         [开关]   │
│  ⚠️ 见顶信号+涨幅后8做空                         [开关]   │
└────────────────────────────────────────────────────────────┘
```

## 📝 使用说明

### 步骤1：打开OKX交易页面
```
https://9002-iopxcqas7abbrajoi4k4x-2e77fc33.sandbox.novita.ai/okx-trading
```

### 步骤2：选择账户
在顶部选择要操作的账户（如"主账户"）

### 步骤3：找到RSI自动开仓策略卡片
向下滚动到黄色渐变的"🚀 RSI自动开仓策略"卡片

### 步骤4：点击重置按钮
点击卡片标题栏右侧的"🔄 重置执行许可"按钮

### 步骤5：确认操作
在弹出的确认对话框中点击"确定"

### 步骤6：查看结果
系统会显示操作结果：
- ✅ 重置成功：显示已重置的策略数量
- ⚠️ 部分成功：显示成功和失败的详情
- ❌ 重置失败：显示错误信息

## ⚠️ 注意事项

### 1. 重置时机
- 重置后策略会立即重新监控市场条件
- 如果当前RSI和市场情绪满足触发条件，策略可能**立即执行**
- 建议在了解当前市场状况后再重置

### 2. 冷却期绕过
- 策略默认有**1小时冷却期**
- 重置功能会**绕过**这个冷却期
- 使用时请谨慎，避免频繁触发

### 3. 账户隔离
- 每个账户的执行许可是**独立**的
- 重置只影响**当前选中的账户**
- 切换账户后需要分别重置

### 4. 策略范围
- 当前重置功能仅针对**见顶信号做空策略**
- 如需支持其他策略类型，需要修改代码

## 🔍 调试信息

### 查看JSONL文件
```bash
# 查看策略执行许可状态
cat /home/user/webapp/data/okx_auto_strategy/account_main_top_signal_top8_short_execution.jsonl | head -1 | jq

# 查看两个策略的状态
for strategy in top8_short bottom8_short; do
    echo "=== $strategy ==="
    cat /home/user/webapp/data/okx_auto_strategy/account_main_top_signal_${strategy}_execution.jsonl | head -1 | jq
done
```

### 查看后台监控日志
```bash
pm2 logs top-signal-short-monitor --lines 50
```

## 📈 未来改进

### 可能的增强功能
1. **批量重置**：同时重置多个账户的执行许可
2. **定时重置**：设置自动重置时间（如每天凌晨重置）
3. **条件重置**：只在特定条件下允许重置（如RSI < 某阈值）
4. **操作日志**：记录每次重置操作的详细信息
5. **权限控制**：限制某些账户的重置权限

## 🎉 功能亮点

✅ **简洁直观**：按钮集成在卡片标题栏，不占用额外空间  
✅ **安全可靠**：确认对话框避免误操作，详细的错误反馈  
✅ **样式统一**：按钮颜色与卡片主题一致，hover效果流畅  
✅ **批量操作**：一键重置两个策略，提高效率  
✅ **实时生效**：重置后立即生效，无需重启服务  

## 📚 相关文档

- **策略配置文档**：`RSI_STRATEGY_REFACTOR.md`
- **API文档**：`app.py` 第16986行
- **前端代码**：`templates/okx_trading.html` 第3241行（按钮）、第7919行（函数）

---

**创建时间**：2026-02-21  
**最后更新**：2026-02-21  
**Git Commit**：c98d8ae
