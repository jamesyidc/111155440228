# V1 vs V2 版本对比

## 🔗 访问地址

| 版本 | URL | 说明 |
|------|-----|------|
| **V1 原版** | https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/coin-change-tracker | 原有功能，可能有缓存问题 |
| **V2 测试版** | https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/coin-change-tracker-v2 | 全新独立版本，推荐测试 |

---

## 📊 功能对比

| 功能 | V1 | V2 | 备注 |
|------|----|----|------|
| 27币涨跌幅监控 | ✅ | ✅ | 完全相同 |
| 趋势图表 | ✅ | ✅ | 完全相同 |
| 排名图表 | ✅ | ✅ | 完全相同 |
| 策略筛选器 | ✅ | ✅ | 完全相同 |
| 预警设置面板 | ✅ | ✅ | 完全相同 |
| 保存按钮 | ✅ | ✅ | 完全相同 |
| 恢复默认 | ✅ | ✅ | 完全相同 |
| JSONL 存储 | ✅ | ✅ | 共享相同后端 |
| localStorage | ✅ | ✅ | 独立存储空间 |
| Telegram 通知 | ✅ | ✅ | 完全相同 |

---

## 🎯 关键差异

### 页面标识
- **V1**：`<title>27币涨跌幅追踪系统</title>`
- **V2**：`<title>27币涨跌幅追踪系统 v3.0 - 全新测试版</title>`

### URL 路径
- **V1**：`/coin-change-tracker`
- **V2**：`/coin-change-tracker-v2`

### 浏览器缓存
- **V1**：可能有旧版本的 JavaScript 缓存
- **V2**：全新创建，无历史缓存

### localStorage 键名
- **两者共享**：`coinAlertSettings`
  - 如果在 V1 中保存，V2 也能读取
  - 如果在 V2 中保存，V1 也能读取

---

## 🧪 测试策略

### 场景1：验证缓存问题
1. 打开 V1，查看阈值显示
2. 打开 V2，查看阈值显示
3. **如果 V2 正确而 V1 错误** → 说明是缓存问题
4. **如果两者都错误** → 说明是代码逻辑问题

### 场景2：验证保存功能
1. 在 V2 中修改阈值为 50% 和 -60%
2. 点击"保存预警设置"
3. 刷新 V2 页面，检查是否保持
4. 打开 V1 页面，检查是否同步（因为共享后端数据）

### 场景3：验证恢复默认
1. 在 V2 中点击"恢复默认"
2. 阈值应该变为 5% 和 -5%
3. 刷新页面，检查是否保持

---

## 🔍 调试检查清单

### 打开 V2 页面后，按 F12，检查：

#### Console 标签
- [ ] 看到："✅ 预警设置从服务器加载"
- [ ] 看到："✅ 阈值更新为 上限: 30 下限: -40"
- [ ] **没有**红色错误信息
- [ ] **没有** `Uncaught TypeError` 或 `Cannot read property`

#### Network 标签
- [ ] 看到请求：`/api/coin-tracker/alert-settings`（GET）
- [ ] 状态码：200
- [ ] 响应包含：`{"success": true, "settings": {...}}`

#### Elements 标签
检查输入框的实际值：
```javascript
// 在 Console 中运行：
document.getElementById('upThreshold').value
document.getElementById('downThreshold').value
```
- [ ] 上限输入框值：30
- [ ] 下限输入框值：-40

---

## 📂 后端数据验证

可以通过命令行验证后端数据：

```bash
# 查看最新的设置
cd /home/user/webapp
tail -1 data/coin_alert_settings/settings.jsonl | jq

# 查看最近3条记录
tail -3 data/coin_alert_settings/settings.jsonl | jq

# 测试 API
curl -s http://localhost:5000/api/coin-tracker/alert-settings | jq
```

**期望输出：**
```json
{
  "success": true,
  "settings": {
    "upperThreshold": 30,
    "lowerThreshold": -40,
    "upperEnabled": true,
    "lowerEnabled": true,
    "tgEnabled": true,
    "timestamp": "2026-02-09T04:51:36.116879"
  }
}
```

---

## ✅ 成功标准

**V2 版本成功的标志：**

1. ✅ 页面标题显示"v3.0 - 全新测试版"
2. ✅ 上涨阈值输入框显示：30
3. ✅ 下跌阈值输入框显示：-40
4. ✅ 上涨开关：绿色（开启状态）
5. ✅ 下跌开关：绿色（开启状态）
6. ✅ 点击保存后，绿色提示出现 3 秒
7. ✅ 刷新页面后，所有设置保持不变
8. ✅ 控制台无错误信息

---

## 🚨 如果 V2 仍然有问题

如果 V2 版本打开后，阈值仍然显示为 5 和 -5（而不是 30 和 -40），请：

### 步骤1：完全清除浏览器缓存
1. 按 `Ctrl + Shift + Delete`
2. 选择"全部时间"
3. 勾选"缓存的图片和文件"
4. 勾选"Cookie 和其他网站数据"
5. 点击"清除数据"
6. 关闭浏览器，重新打开

### 步骤2：使用隐身模式
1. 按 `Ctrl + Shift + N`（Chrome）或 `Ctrl + Shift + P`（Firefox）
2. 在隐身窗口中打开 V2 地址
3. 检查阈值显示

### 步骤3：检查后端数据
```bash
# 确认后端确实保存了正确的数据
curl -s http://localhost:5000/api/coin-tracker/alert-settings
```

### 步骤4：截图提供
如果仍然有问题，请提供以下截图：
1. V2 页面的预警设置面板（显示阈值）
2. 浏览器控制台（F12 → Console 标签）
3. 网络请求（F12 → Network 标签 → 筛选 XHR）

---

## 📞 下一步

1. **立即访问 V2 版本**：
   ```
   https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/coin-change-tracker-v2
   ```

2. **检查阈值显示**：
   - 应该是 30% 和 -40%
   - 不应该是 5% 和 -5%

3. **反馈结果**：
   - ✅ 如果正确显示 → 说明 V1 有缓存问题，V2 正常
   - ❌ 如果仍然错误 → 说明代码逻辑有问题，需要深入排查

**请现在访问 V2 地址并告诉我结果！** 🎯
