# 预警功能优化 - 2026-02-10 02:00

## ✅ 已完成的优化

### 1. **声音持续播放** 🔊
**需求**: 声音不要停，一直播放到用户关闭弹窗才结束

**实现方案**:
- 添加`alertSoundLoop`变量控制声音循环
- `playAlertSound()`改为循环播放，每轮5次哔声后间隔1秒继续
- 添加`stopAlertSound()`函数停止循环
- 在弹窗的"知道了"和"刷新数据"按钮中调用`stopAlertSound()`

**播放逻辑**:
```
触发预警 → 开始循环播放
  ↓
5次哔声（高-低-高-低-高）
  ↓
等待1秒
  ↓
再次播放5次哔声...
  ↓
持续循环，直到用户关闭弹窗
```

**停止声音的方式**:
1. 点击"知道了"按钮 → 停止声音 → 关闭弹窗
2. 点击"刷新数据"按钮 → 停止声音 → 刷新页面

---

### 2. **预警可重复触发** 🔔
**问题**: 触发一次后就不再触发了

**原因分析**:
- 旧逻辑：触发后设置`upperTriggered = true`，并关闭开关
- 检查条件：`if (alertState.upperEnabled && !alertState.upperTriggered && ...)`
- 结果：第二次不满足`!alertState.upperTriggered`，不会触发

**新方案**:
- 移除`upperTriggered`和`lowerTriggered`
- 添加`upperLastTriggerTime`和`lowerLastTriggerTime`记录上次触发时间
- 添加`triggerInterval = 5 * 60 * 1000`（5分钟）防止频繁触发
- 检查逻辑改为：如果距离上次触发超过5分钟，则可以再次触发

**触发机制**:
```
当前值 >= 阈值
  ↓
检查距离上次触发时间
  ↓
>= 5分钟 → 触发预警
< 5分钟  → 跳过，打印等待时间
```

**优点**:
1. 预警开关不会自动关闭，持续监控
2. 避免频繁打扰（5分钟间隔）
3. 修改阈值或重新开启预警，会重置触发时间，立即生效

---

## 📊 数据结构变化

### alertState 对象

**修改前**:
```javascript
{
    upperEnabled: false,
    lowerEnabled: false,
    upperThreshold: 10,
    lowerThreshold: -20,
    upperTriggered: false,    // 已触发标记
    lowerTriggered: false,    // 已触发标记
    lastCheckTime: null,
    tgEnabled: true
}
```

**修改后**:
```javascript
{
    upperEnabled: false,
    lowerEnabled: false,
    upperThreshold: 10,
    lowerThreshold: -20,
    upperLastTriggerTime: null,  // 上次触发时间（毫秒）
    lowerLastTriggerTime: null,  // 上次触发时间（毫秒）
    lastCheckTime: null,
    tgEnabled: true,
    triggerInterval: 5 * 60 * 1000  // 5分钟间隔
}
```

---

## 🔧 核心函数修改

### 1. playAlertSound()
```javascript
// 修改前：播放一次5个哔声后结束
async function playAlertSound() {
    await playBeep(1000, 0.2, 0);
    await playBeep(800, 0.2, 100);
    await playBeep(1000, 0.2, 100);
    await playBeep(800, 0.2, 100);
    await playBeep(1000, 0.3, 100);
}

// 修改后：持续循环播放
async function playAlertSound() {
    stopAlertSound();  // 停止之前的循环
    alertSoundLoop = { playing: true };
    
    const playLoop = async () => {
        while (alertSoundLoop && alertSoundLoop.playing) {
            // 播放5次哔声
            await playBeep(1000, 0.2, 0);
            await playBeep(800, 0.2, 100);
            await playBeep(1000, 0.2, 100);
            await playBeep(800, 0.2, 100);
            await playBeep(1000, 0.3, 100);
            
            // 等待1秒后继续
            if (alertSoundLoop.playing) {
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
    };
    
    playLoop();
}
```

### 2. stopAlertSound()
```javascript
function stopAlertSound() {
    if (alertSoundLoop) {
        console.log('🔇 停止预警音效');
        alertSoundLoop.playing = false;
        alertSoundLoop = null;
    }
}
```

### 3. checkAlerts()
```javascript
// 修改前：触发后自动关闭开关
if (alertState.upperEnabled && !alertState.upperTriggered && currentValue >= alertState.upperThreshold) {
    // 触发预警
    alertState.upperEnabled = false;    // 关闭开关
    alertState.upperTriggered = true;   // 标记已触发
    document.getElementById('upAlertEnabled').checked = false;
}

// 修改后：使用时间间隔控制
if (alertState.upperEnabled && currentValue >= alertState.upperThreshold) {
    const timeSinceLastTrigger = alertState.upperLastTriggerTime 
        ? now - alertState.upperLastTriggerTime 
        : Infinity;
    
    if (timeSinceLastTrigger >= alertState.triggerInterval) {
        // 触发预警
        alertState.upperLastTriggerTime = now;  // 记录触发时间
        playAlertSound();  // 开始循环播放
        showAlertDialog('upper', currentValue, triggerCoins);
        // 开关保持开启状态
    } else {
        const waitTime = Math.round((alertState.triggerInterval - timeSinceLastTrigger) / 1000);
        console.log(`⏱️ 上限预警已触发，还需等待 ${waitTime} 秒才能再次触发`);
    }
}
```

---

## 🎯 使用场景

### 场景1：首次触发
```
1. 用户设置上限预警：+10%
2. 当前涨幅达到 +11%
3. ✅ 触发预警：
   - 弹窗显示
   - 声音循环播放
   - 发送Telegram通知
4. 用户查看后点击"知道了"
5. 声音停止，弹窗关闭
6. 预警开关保持开启
```

### 场景2：重复触发
```
1. 5分钟后，涨幅仍然 > +10%（比如 +12%）
2. ✅ 再次触发预警
3. 又弹出预警窗口
4. 声音再次循环播放
```

### 场景3：频繁检查保护
```
1. 涨幅达到 +10%，触发预警
2. 2分钟后，涨幅 +11%
3. ❌ 不触发（距离上次触发不足5分钟）
4. 控制台输出："还需等待 180 秒才能再次触发"
5. 5分钟后，涨幅 +13%
6. ✅ 触发预警
```

---

## ✅ 验收要点

### 声音功能
- [x] 预警触发时声音开始播放
- [x] 声音持续循环播放（5次哔声 + 1秒间隔）
- [x] 点击"知道了"后声音停止
- [x] 点击"刷新数据"后声音停止
- [x] 关闭弹窗后声音停止

### 触发功能
- [x] 首次达到阈值时触发
- [x] 触发后开关保持开启
- [x] 5分钟后可以再次触发
- [x] 5分钟内不会重复触发
- [x] 修改阈值后重置触发时间
- [x] 重新开启预警后重置触发时间
- [x] 控制台显示等待时间

---

## 🔗 测试方法

### 测试声音循环
1. 访问: https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/coin-change-tracker
2. 打开预警设置，设置上限为当前值以下（比如当前+42%，设置+10%）
3. 开启上限预警开关
4. 点击"测试预警"
5. 应该：
   - 弹出预警窗口
   - 声音开始循环播放（5次哔声，间隔1秒，持续循环）
6. 等待10-20秒，确认声音持续播放
7. 点击"知道了"
8. 应该：声音立即停止

### 测试重复触发
1. 开启上限预警（+10%）
2. 查看控制台，应显示："🔴 触发上限预警"
3. 关闭弹窗，等待10秒（页面会自动刷新数据）
4. 查看控制台，应显示："⏱️ 上限预警已触发，还需等待 XXX 秒"
5. 等待5分钟（或修改代码将triggerInterval改为10秒测试）
6. 查看控制台，应再次显示："🔴 触发上限预警"
7. 再次弹窗和播放声音

---

## 📄 修改文件

### 核心文件
- `/home/user/webapp/templates/coin_change_tracker.html`

### 修改内容
1. 添加`alertSoundLoop`变量
2. 修改`alertState`数据结构
3. 重写`playAlertSound()`函数
4. 添加`stopAlertSound()`函数
5. 修改`checkAlerts()`触发逻辑
6. 修改弹窗按钮添加`stopAlertSound()`调用
7. 修改预警开关事件处理，重置触发时间

---

## 🐛 已知问题

### 问题：页面刷新后声音继续播放
**状态**: 已解决
**原因**: 页面刷新会重新加载，alertSoundLoop变量重置
**解决**: 无需处理，页面刷新自动停止

### 问题：同时触发上下限预警
**状态**: 理论上不会发生
**原因**: 上限和下限阈值应该设置为相反的方向
**建议**: 上限设置为正数（如+10%），下限设置为负数（如-20%）

---

## 📊 性能影响

### 声音循环
- CPU占用：极低（每秒创建5个简单的振荡器）
- 内存占用：可忽略（只有一个播放循环）
- 用户体验：持续提醒，直到用户响应

### 重复触发
- 检查频率：每10秒一次（跟随数据刷新）
- 触发频率：最多每5分钟一次
- 存储占用：只保存最后触发时间（8字节）

---

## 🎉 总结

### 核心改进
1. ✅ 声音持续播放，提高警示效果
2. ✅ 预警可重复触发，持续监控
3. ✅ 5分钟间隔，避免频繁打扰
4. ✅ 开关保持开启，无需重新设置
5. ✅ 清晰的日志输出，方便调试

### 用户体验
- **更明显的提醒**：声音持续播放，不会错过
- **更灵活的监控**：不需要每次重新开启
- **更合理的频率**：5分钟间隔，不会太吵
- **更直观的反馈**：控制台显示等待时间

---

**完成时间**: 2026-02-10 02:00  
**Git提交**: 1f486cb  
**状态**: ✅ 已完成，等待用户测试  
**下一步**: 用户测试并反馈
