# 预警功能测试指南

## 🎯 快速测试步骤

### 1. 访问页面
打开浏览器访问：
```
https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/coin-change-tracker
```

### 2. 找到预警设置面板
在页面顶部导航栏下方，您会看到：
```
⚡ 预警设置
├─ 上限预警（涨幅）：[300] % [开关]
└─ 下限预警（跌幅）：[-300] % [开关]
```

### 3. 配置预警

#### 方式A：快速测试（低阈值）
```
1. 将上限阈值改为：50
2. 将下限阈值改为：-50
3. 打开两个开关（变为绿色）
4. 等待几分钟，观察是否触发
```

#### 方式B：正常使用（默认阈值）
```
1. 保持上限：300
2. 保持下限：-300
3. 打开需要的开关
4. 等待市场大幅波动
```

### 4. 验证功能

当预警触发时，您应该看到：

✅ **音效播放**
- 听到3次警报音（哔哔哔）
- 每次约0.5秒

✅ **弹窗显示**
- 页面中央出现预警对话框
- 显示详细数据和触发币种
- 5秒后自动消失

✅ **开关自动关闭**
- 触发的开关变回灰色
- 需要手动重新开启

✅ **Telegram通知**（如已配置）
- 手机收到Bot消息
- 包含预警详情

### 5. 浏览器控制台检查

按 F12 打开控制台，应该看到类似日志：
```
✅ 预警设置已加载: {upperThreshold: 300, lowerThreshold: -300, ...}
上限预警 已开启
🔴 触发上限预警: 320 >= 300
🔊 预警音效已播放
✅ Telegram通知已发送: {...}
```

## 🧪 测试案例

### 案例1：测试上限预警
```javascript
// 在控制台执行（模拟触发）
alertState.upperThreshold = 50
alertState.upperEnabled = true
updateSwitchStyles()
saveAlertSettings()
```

### 案例2：测试下限预警
```javascript
// 在控制台执行（模拟触发）
alertState.lowerThreshold = -50
alertState.lowerEnabled = true
updateSwitchStyles()
saveAlertSettings()
```

### 案例3：手动触发音效
```javascript
// 在控制台执行
playAlertSound()
```

### 案例4：测试弹窗
```javascript
// 在控制台执行
showAlertDialog('upper', 320, [
  {symbol: 'BTC', change: '15.50'},
  {symbol: 'ETH', change: '12.30'}
])
```

## 📱 Telegram配置测试

### 1. 配置Bot Token和Chat ID
访问：`https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/system-config`

### 2. 测试API
```bash
curl -X POST http://localhost:5000/api/telegram/send-alert \
  -H "Content-Type: application/json" \
  -d '{
    "message": "测试预警消息",
    "type": "test"
  }'
```

### 3. 验证响应
应该返回：
```json
{
  "success": true,
  "message": "通知已发送",
  "type": "test"
}
```

## 🔍 故障排查

### 问题1：看不到预警设置面板
**解决方案**：
- 强制刷新页面（Ctrl + Shift + R）
- 清除浏览器缓存
- 检查是否在正确的URL

### 问题2：开关点击无反应
**解决方案**：
- F12 查看控制台错误
- 检查JavaScript是否被禁用
- 刷新页面重试

### 问题3：没有音效播放
**解决方案**：
- 检查浏览器是否静音
- 确认浏览器支持Web Audio API
- 检查用户手势要求（有些浏览器需要用户交互后才能播放音频）

### 问题4：Telegram通知未收到
**解决方案**：
1. 检查Bot Token是否正确
2. 检查Chat ID是否正确
3. 确认Bot已经启动（向Bot发送/start）
4. 查看控制台错误信息

### 问题5：预警一直不触发
**解决方案**：
- 检查开关是否开启（绿色）
- 检查阈值设置是否合理
- 查看当前累计涨跌幅是否接近阈值
- 查看控制台是否有检查日志

## 📊 实时监控

### 查看当前状态
在控制台执行：
```javascript
console.log('预警状态:', alertState)
```

### 强制检查预警
在控制台执行：
```javascript
fetch('/api/coin-change-tracker/latest')
  .then(r => r.json())
  .then(data => {
    console.log('当前数据:', data)
    checkAlerts(data)
  })
```

### 查看localStorage设置
在控制台执行：
```javascript
const settings = localStorage.getItem('coinAlertSettings')
console.log('保存的设置:', JSON.parse(settings))
```

## 🎬 演示视频脚本

1. **打开页面**
   - 展示页面整体布局
   - 指出预警设置面板位置

2. **配置预警**
   - 输入阈值
   - 开启开关
   - 展示开关变绿

3. **等待触发**
   - 展示实时数据更新
   - 观察累计涨跌幅变化

4. **预警触发**
   - 音效播放
   - 弹窗显示
   - 开关自动关闭

5. **查看通知**
   - 手机Telegram收到消息
   - 展示消息内容

6. **重新启用**
   - 点击开关重新开启
   - 展示可以再次预警

## ✅ 验收检查清单

- [ ] 预警设置面板正常显示
- [ ] 可以输入和修改阈值
- [ ] 开关可以点击并切换状态
- [ ] 开关状态有颜色变化（绿/灰）
- [ ] 设置会保存到localStorage
- [ ] 页面刷新后设置保持
- [ ] 音效可以正常播放
- [ ] 弹窗可以正常显示
- [ ] 弹窗内容正确完整
- [ ] 弹窗可以手动关闭
- [ ] 弹窗5秒后自动关闭
- [ ] Telegram通知可以发送
- [ ] Telegram消息内容正确
- [ ] 触发后开关自动关闭
- [ ] 可以手动重新开启
- [ ] 控制台日志正常输出
- [ ] 没有JavaScript错误

## 📈 性能监控

### 检查项
1. **内存使用**
   - 长时间运行不应泄漏
   - 控制台 Memory 标签查看

2. **CPU占用**
   - 预警检查不应占用过多CPU
   - 任务管理器查看浏览器进程

3. **网络请求**
   - 每次检查只发送1个API请求
   - Network 标签查看请求频率

4. **响应速度**
   - 开关点击立即响应
   - 音效播放无延迟
   - 弹窗显示流畅

## 🔄 更新日志

### v2.1.0 (2026-02-09)
- ✅ 新增预警设置面板
- ✅ 实现音效播放功能
- ✅ 实现Telegram通知功能
- ✅ 实现弹窗提示功能
- ✅ 实现自动关闭开关机制
- ✅ 实现设置持久化
- ✅ 添加防重复触发逻辑
- ✅ 添加详细日志输出

---

**测试建议**：建议先用低阈值（±50%）快速测试功能是否正常，确认无误后再调整到实际使用的阈值（±300%）。
