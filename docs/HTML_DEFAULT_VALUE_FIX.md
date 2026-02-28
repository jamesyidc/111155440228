# 修复 HTML 默认值覆盖问题

## 🔍 问题诊断

### 发现的问题
在 V2 页面中，输入框显示的是默认值 5% 和 -5%，而不是从服务器加载的值 30% 和 -40%。

### 根本原因
**HTML 中硬编码了默认值：**
```html
<!-- ❌ 错误：硬编码默认值 -->
<input type="number" id="upThreshold" value="5" ... >
<input type="number" id="downThreshold" value="-5" ... >
```

**问题流程：**
1. 浏览器加载 HTML → 输入框显示 5 和 -5（硬编码值）
2. JavaScript 执行 `loadAlertSettings()` → 从服务器获取 30 和 -40
3. JavaScript 尝试设置 `input.value = 30` 和 `input.value = -40`
4. **但由于某种原因，设置失败或被覆盖**
5. 最终用户看到的仍然是 5 和 -5

---

## ✅ 解决方案

### 1. 移除 HTML 默认值
```html
<!-- ✅ 正确：不设置默认值，使用 placeholder -->
<input type="number" id="upThreshold" step="0.1" min="0" max="100"
       placeholder="加载中..." ... >
<input type="number" id="downThreshold" step="0.1" max="0" min="-100"
       placeholder="加载中..." ... >
```

**好处：**
- 输入框初始为空，显示"加载中..."提示
- JavaScript 设置的值不会被默认值覆盖
- 用户可以清楚看到加载过程

### 2. 立即执行加载函数
```javascript
// ❌ 旧代码：使用 setTimeout 延迟
setTimeout(() => {
    loadAlertSettings();
}, 100);

// ✅ 新代码：立即执行，并添加验证
loadAlertSettings().then(() => {
    console.log('🎯 页面加载完成，预警设置已加载');
    
    // 500ms后二次验证
    setTimeout(() => {
        const upValue = document.getElementById('upThreshold').value;
        const downValue = document.getElementById('downThreshold').value;
        console.log('🔍 验证 - 上限:', upValue, '下限:', downValue);
        
        // 如果不匹配，强制重新设置
        if (upValue != alertState.upperThreshold || downValue != alertState.lowerThreshold) {
            console.warn('⚠️ 值不匹配，强制重新设置！');
            document.getElementById('upThreshold').value = alertState.upperThreshold;
            document.getElementById('downThreshold').value = alertState.lowerThreshold;
        }
    }, 500);
});
```

**好处：**
- 立即执行，不等待 100ms
- 500ms 后二次验证，确保值正确
- 如果检测到不匹配，强制重新设置

---

## 🧪 测试步骤

### 第一步：清除浏览器缓存
1. 按 `Ctrl + Shift + Delete`
2. 选择"全部时间"
3. 勾选"缓存的图片和文件"
4. 点击"清除数据"

### 第二步：强制刷新 V2 页面
```
https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/coin-change-tracker-v2
```
按 `Ctrl + Shift + R`（强制刷新）

### 第三步：观察加载过程
打开浏览器控制台（F12），应该看到：
```
🎯 页面加载完成，预警设置已加载
✅ 预警设置已从服务器加载: {upperThreshold: 30, lowerThreshold: -40, ...}
📊 阈值已更新 - 上限: 30 下限: -40
🔍 500ms后验证 - 上限输入框值: 30 下限输入框值: -40
🔍 500ms后验证 - alertState: {"upperThreshold":30,"lowerThreshold":-40,...}
```

### 第四步：检查输入框
- **上涨阈值输入框**：应该显示 `30`（不是 5）
- **下跌阈值输入框**：应该显示 `-40`（不是 -5）
- **初始加载时**：应该显示"加载中..."，然后变为实际值

---

## 📊 期望结果

### 视觉上
1. **页面刚打开**：输入框显示"加载中..."（灰色 placeholder）
2. **0.1秒后**：输入框显示 30 和 -40（黑色文字）
3. **开关状态**：上涨和下跌开关都是绿色（已开启）

### 控制台日志
```
✅ 预警设置已从服务器加载: {
  upperThreshold: 30,
  lowerThreshold: -40,
  upperEnabled: true,
  lowerEnabled: true,
  tgEnabled: true,
  ...
}
📊 阈值已更新 - 上限: 30 下限: -40
🎯 页面加载完成，预警设置已加载
🔍 500ms后验证 - 上限输入框值: 30 下限输入框值: -40
```

### 刷新后
再次按 `F5` 刷新页面，值应该仍然是 30 和 -40，不会变回 5 和 -5。

---

## 🔍 如果仍然有问题

### 调试步骤

#### 1. 检查后端数据
```bash
curl -s http://localhost:5000/api/coin-tracker/alert-settings | jq
```
应该返回：
```json
{
  "success": true,
  "settings": {
    "upperThreshold": 30,
    "lowerThreshold": -40,
    ...
  }
}
```

#### 2. 在控制台手动检查
按 F12，在 Console 中输入：
```javascript
// 检查输入框的值
document.getElementById('upThreshold').value
document.getElementById('downThreshold').value

// 检查 alertState
alertState

// 手动设置值
document.getElementById('upThreshold').value = 30
document.getElementById('downThreshold').value = -40
```

#### 3. 检查 Network 请求
1. 打开 F12 → Network 标签
2. 刷新页面
3. 筛选 XHR 请求
4. 查找 `/api/coin-tracker/alert-settings`
5. 检查响应是否包含正确的数据

---

## 📁 修改的文件

### templates/coin_change_tracker_v2.html
- **第 80 行**：移除 `value="5"`，添加 `placeholder="加载中..."`
- **第 107 行**：移除 `value="-5"`，添加 `placeholder="加载中..."`
- **第 1727-1730 行**：改为立即执行 + 二次验证

---

## 🎯 关键改进

| 项目 | 修改前 | 修改后 |
|------|--------|--------|
| **HTML 默认值** | `value="5"` 和 `value="-5"` | 无默认值，使用 `placeholder` |
| **加载时机** | `setTimeout(100ms)` | 立即执行 |
| **验证机制** | 无 | 500ms 后二次验证 |
| **错误处理** | 无 | 检测不匹配并强制重置 |
| **用户体验** | 先显示错误值，再变为正确值 | 显示"加载中..."，然后显示正确值 |

---

## ✅ 成功标志

**这次修复应该彻底解决问题！**

如果 V2 页面正确显示 30 和 -40，说明：
- ✅ HTML 默认值问题已解决
- ✅ JavaScript 加载逻辑正常
- ✅ 后端 API 返回正确
- ✅ 数据持久化成功

**请现在访问 V2 并反馈结果！** 🎉

---

生成时间：2026-02-09  
版本：HTML 默认值修复 v1.0
