# 🔊 音频功能修复指南

## 问题原因

浏览器的安全策略要求：**音频只能在用户交互后播放**（Autoplay Policy）。

如果页面加载后没有任何用户交互，Web Audio API 会被浏览器阻止。

## 解决方案

### 1. 自动初始化音频上下文
- 页面加载时尝试初始化音频上下文
- 监听用户第一次点击页面任意位置
- 用户交互后立即激活音频功能

### 2. 改进的音频播放
- 使用全局音频上下文（避免重复创建）
- 检测音频上下文状态（suspended → running）
- 使用 async/await 确保声音按顺序播放
- 5次哔声：1000Hz → 800Hz → 1000Hz → 800Hz → 1000Hz

### 3. 错误处理
- 如果音频上下文无法初始化，显示提示
- 控制台输出详细的调试信息
- 每次播放都检查音频状态

## 🎯 测试步骤

### 第一步：打开页面
访问：https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/coin-change-tracker

### 第二步：激活音频（重要！）
**在测试预警前，必须先与页面交互！**

方式1：点击页面任意空白位置
方式2：滚动页面
方式3：点击任意按钮

> 💡 这一步是为了让浏览器允许播放音频

### 第三步：打开浏览器控制台
按 `F12` 或 `Ctrl+Shift+I` 打开开发者工具

### 第四步：测试音频
点击紫色的"🧪 测试预警"按钮

### 第五步：检查控制台输出
应该看到以下日志：
```
🎵 playAlertSound 被调用
🔊 开始播放预警音效...
🔊 播放哔声: 1000Hz
🔊 播放哔声: 800Hz
🔊 播放哔声: 1000Hz
🔊 播放哔声: 800Hz
🔊 播放哔声: 1000Hz
✅ 预警音效播放完成
```

## 🔍 故障排查

### 问题1: 没有声音

**检查清单**：
1. ✅ **先点击页面任意位置**（这是最常见的问题！）
2. ✅ 检查系统音量是否静音
3. ✅ 检查浏览器标签页是否静音（右键点击标签页）
4. ✅ 检查控制台是否有错误信息
5. ✅ 尝试刷新页面，再次点击页面，然后测试

**控制台检查**：
```javascript
// 打开控制台（F12），输入以下命令检查音频状态
console.log('音频上下文:', audioContext);
console.log('音频状态:', audioContext ? audioContext.state : '未初始化');
console.log('音频初始化:', audioInitialized);
```

如果显示 `state: 'suspended'`，说明音频被浏览器暂停了，需要用户交互。

**手动激活音频**：
```javascript
// 在控制台执行
initAudio();
```

### 问题2: 控制台显示错误

**常见错误1**: `NotAllowedError: play() failed`
- **原因**: 浏览器阻止自动播放
- **解决**: 先点击页面任意位置

**常见错误2**: `AudioContext was not allowed to start`
- **原因**: 需要用户交互
- **解决**: 先点击页面任意位置

**常见错误3**: `音频上下文未初始化`
- **原因**: initAudio() 没有被调用
- **解决**: 刷新页面或手动执行 `initAudio()`

### 问题3: 只有部分哔声

**可能原因**：
- 网络延迟或CPU占用高
- 浏览器标签页被切换到后台

**解决方案**：
- 确保标签页在前台
- 等待页面完全加载后再测试

## 📱 不同浏览器的表现

### Chrome/Edge (推荐)
- ✅ 完美支持
- ✅ 需要用户交互后才能播放
- ✅ 控制台日志清晰

### Firefox
- ✅ 支持良好
- ✅ 需要用户交互
- ⚠️ 某些版本可能需要在设置中允许音频自动播放

### Safari
- ⚠️ 音频策略最严格
- ✅ 需要用户交互
- ⚠️ 可能需要多次交互才能激活

### 移动浏览器
- ⚠️ 音频支持可能受限
- ✅ 通常需要用户点击后才能播放
- 💡 建议使用桌面浏览器测试

## 🎵 音频技术细节

### 音频序列
```javascript
// 5次哔声，交替频率
1000Hz (200ms)  -- 高音
  ↓ 100ms 延迟
800Hz (200ms)   -- 低音
  ↓ 100ms 延迟
1000Hz (200ms)  -- 高音
  ↓ 100ms 延迟
800Hz (200ms)   -- 低音
  ↓ 100ms 延迟
1000Hz (300ms)  -- 高音（稍长）

总时长约 1.5 秒
```

### 音量设置
- 音量：0.3（30%）
- 波形：正弦波（sine wave）
- 淡入淡出：避免爆音

### Web Audio API
```javascript
// 创建音频上下文
const audioContext = new (window.AudioContext || window.webkitAudioContext)();

// 创建振荡器（生成声音）
const oscillator = audioContext.createOscillator();
oscillator.frequency.value = 1000; // 频率 1000Hz
oscillator.type = 'sine'; // 正弦波

// 创建增益节点（控制音量）
const gainNode = audioContext.createGain();
gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);

// 连接节点
oscillator.connect(gainNode);
gainNode.connect(audioContext.destination);

// 播放
oscillator.start();
oscillator.stop(audioContext.currentTime + 0.2);
```

## ✅ 验证清单

测试预警音频功能：

- [ ] 打开页面
- [ ] 点击页面任意位置（激活音频）
- [ ] 打开控制台（F12）
- [ ] 点击"测试预警"按钮
- [ ] 听到5次哔声
- [ ] 看到弹窗（不会自动消失）
- [ ] 控制台显示播放日志
- [ ] 手动关闭弹窗

## 🚀 快速测试命令

在浏览器控制台执行：

```javascript
// 1. 检查音频状态
console.log('音频上下文:', audioContext);
console.log('音频状态:', audioContext?.state);

// 2. 手动初始化音频
initAudio();

// 3. 手动播放测试音
playAlertSound();

// 4. 测试完整预警流程
showAlertDialog('upper', 35.5, []);
```

## 📋 改进内容

### v1.0（之前）
- ❌ 每次播放创建新的音频上下文
- ❌ 没有检查用户交互
- ❌ 声音可能被浏览器阻止
- ❌ 没有详细的调试日志

### v2.0（现在）
- ✅ 全局音频上下文，只创建一次
- ✅ 监听用户交互，自动激活音频
- ✅ 检查音频状态（suspended → running）
- ✅ 使用 async/await 确保顺序播放
- ✅ 详细的调试日志
- ✅ 更好的错误处理

## 🔗 相关链接

- **测试页面**: https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/coin-change-tracker
- **MDN Web Audio API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
- **Autoplay Policy**: https://developer.chrome.com/blog/autoplay/

## 💡 使用建议

1. **首次访问**：先点击页面任意位置，再测试音频
2. **定期测试**：使用测试按钮验证音频功能正常
3. **实际使用**：设置合理的阈值，避免频繁触发
4. **浏览器选择**：推荐使用 Chrome 或 Edge 浏览器

---

**最后更新**: 2026-02-10
**状态**: ✅ 音频功能已优化并测试通过
