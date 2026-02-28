# 🔔 预警功能快速测试指南

## 🎯 问题修复

**已修复：** `checkAlerts()` 函数之前从未被调用，现在已添加到数据更新流程中。

---

## 🧪 快速测试步骤

### 第1步：打开页面
```
https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/coin-change-tracker
```

### 第2步：降低阈值（临时测试）
当前总涨跌幅是 **-35.88%**，为了快速测试，我们需要设置一个容易触发的阈值：

1. 找到"下跌预警"区域
2. 将下跌阈值改为：`-36`（略高于当前值）
3. 确保下跌开关是**绿色**（已开启）
4. 点击"💾 保存预警设置"

### 第3步：等待触发（约10秒）
- 系统每10秒自动更新一次数据
- 下次更新时，会检测到 -35.88 <= -36（错误，应该是 -35.88 > -36）
  
**修正：应该设置为 `-35`** 才能触发！

让我重新说明：

### ✅ 正确的测试步骤

1. **设置阈值为 `-35`**（低于当前值 -35.88）
2. **点击保存**
3. **等待10秒**
4. **观察**：
   - 🔊 听到音效（哔哔哔，3次）
   - 📝 看到弹窗提示
   - 📱 收到 Telegram 通知（如已配置）
   - 🔴 下跌开关自动变灰（关闭）

---

## 🔍 如果没有触发，检查以下项

### 1. 打开控制台（F12）
查看是否有以下日志：
```
✅ 预警设置已保存
🟢 触发下限预警: -35.88 <= -35
```

### 2. 检查开关状态
- 下跌开关是否是**绿色**（开启）？
- 如果是灰色，说明已经触发过，需要手动重新开启

### 3. 手动测试
在控制台（F12）中输入：
```javascript
checkAlerts({
    cumulative_pct: -35.88,
    changes: window.currentCoinsData || {}
});
```

如果这个命令触发了预警，说明自动检查有问题。
如果没有触发，说明条件不满足。

---

## 📊 当前设置确认

在控制台输入以查看当前状态：
```javascript
console.log('当前涨跌幅:', document.getElementById('totalChange').textContent);
console.log('预警状态:', alertState);
```

**期望输出：**
```
当前涨跌幅: -35.88%
预警状态: {
  upperEnabled: true,
  lowerEnabled: true,
  upperThreshold: 30,
  lowerThreshold: -35,    // 测试值
  upperTriggered: false,
  lowerTriggered: false,
  lastCheckTime: null,
  tgEnabled: true
}
```

---

## 🎮 测试脚本（自动化）

直接在控制台运行这个脚本：

```javascript
// 1. 设置阈值为当前值的上方（确保触发）
const currentValue = parseFloat(document.getElementById('totalChange').textContent);
alertState.lowerThreshold = currentValue + 0.5;  // 稍微高一点
alertState.lowerEnabled = true;
alertState.lowerTriggered = false;

// 2. 保存设置
await saveAlertSettings();
console.log(`✅ 阈值已设置为 ${alertState.lowerThreshold}，当前值 ${currentValue}`);

// 3. 等待2秒后手动触发测试
setTimeout(() => {
    console.log('🧪 执行测试触发...');
    checkAlerts({
        cumulative_pct: currentValue,
        changes: window.currentCoinsData || {}
    });
}, 2000);
```

**期望结果（2秒后）：**
- 🔊 音效播放
- 📝 弹窗显示
- 📱 Telegram 通知
- 🔴 开关变灰

---

## ⚠️ 重要提示

### 阈值的比较逻辑
- **上涨预警**：当前值 **>=** 阈值时触发
  - 例如：当前 35%，阈值 30% → 触发（35 >= 30）
  
- **下跌预警**：当前值 **<=** 阈值时触发
  - 例如：当前 -35.88%，阈值 -35% → 触发（-35.88 <= -35）
  - **注意**：-35.88 比 -35 更小（更负），所以满足条件

### 为什么之前没触发？
如果您看到的是 -35.88%，而阈值是 -40%：
- -35.88 <= -40？**否**（-35.88 > -40）
- 所以不会触发

如果瞬间低于 -40（比如 -40.5），但您没有看到页面：
- 可能在那10秒内触发了
- 开关可能已经自动关闭
- 需要检查 JSONL 文件中的 `lowerTriggered` 字段

---

## 🔧 检查历史触发记录

```bash
cd /home/user/webapp
tail -5 data/coin_alert_settings/settings.jsonl | jq
```

如果之前触发过，会看到：
```json
{
  "lowerTriggered": true,    // 表示已触发
  "lowerEnabled": false,     // 自动关闭
  "timestamp": "2026-02-09T..."
}
```

---

## 📞 测试后反馈

### ✅ 如果测试成功
- 看到了弹窗 → 功能正常
- 听到了音效 → 音效正常
- 收到 Telegram → 通知正常

### ❌ 如果测试失败
请提供：
1. 控制台日志截图（F12 → Console）
2. 当前阈值设置截图
3. 手动测试的结果（运行 `checkAlerts(...)` 的输出）

---

## 🚀 测试完成后

### 恢复原阈值
```javascript
alertState.upperThreshold = 30;
alertState.lowerThreshold = -40;
alertState.upperEnabled = true;
alertState.lowerEnabled = true;
alertState.upperTriggered = false;
alertState.lowerTriggered = false;
await saveAlertSettings();
console.log('✅ 阈值已恢复为 30 和 -40');
```

或者直接点击页面上的"恢复默认"按钮，然后重新设置为 30 和 -40。

---

生成时间：2026-02-09  
状态：✅ 待测试
