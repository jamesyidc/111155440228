# OKX自动策略执行流程说明

## 当前执行流程（无确认弹窗）

### 1. 策略触发条件检查（每60秒）

**BTC价格触发策略：**
- BTC价格 < 触发价 → 涨幅后8名策略
- BTC价格 > 触发价 → 涨幅前8名策略

**上涨占比0触发策略：**
- 上涨占比 = 0% → 自动执行

### 2. 触发后自动执行（无需用户确认）

**代码位置：** `templates/okx_trading.html` 第6783行

```javascript
// 执行开单（直接执行，无confirm）
const result = await executeAutoTrade(account, btcPrice, settings.triggerPrice, strategyType);
```

**没有任何confirm确认对话框！**

### 3. 执行流程

1. **检查触发条件**
   - BTC价格检查
   - 上涨占比检查
   - JSONL allowed状态检查
   - 执行锁检查

2. **发送Telegram通知（触发）**
   ```
   🎯 涨幅后8名策略触发
   ⏰ 触发时间: 2026-02-18 10:00:00
   💰 BTC价格: $66969
   📉 触发价格: $67000
   👤 账户: account_poit_main
   📊 正在分析常用币(15个)涨跌幅...
   🔄 准备对涨幅后8名开多单...
   ```

3. **自动执行开单**
   - 获取常用币列表（15个）
   - 获取24h涨跌幅数据
   - 排序选取前8名/后8名
   - 计算开仓金额（总权益 × positionSize%）
   - 依次下单（8个币种）

4. **发送Telegram通知（完成）**
   ```
   ✅ 涨幅后8名策略执行完成
   ⏰ 完成时间: 2026-02-18 10:01:00
   👤 账户: account_poit_main
   💰 BTC价格: $66969
   📊 执行结果
   ✓ 成功: 8/8 个币种
   🟢 成功币种:
   TAO, APT, DOT, LDO, CRO, SUI, FIL, CFX
   ```

5. **自动关闭策略**
   - 设置 enabled = false
   - 设置 allowed = false
   - 释放执行锁

### 4. 代码验证

```bash
# 搜索confirm调用
cd /home/user/webapp
grep -n "confirm.*executeAutoTrade\|executeAutoTrade.*confirm" templates/okx_trading.html
# 结果：无匹配

# 搜索executeAutoTrade调用
grep -B5 -A5 "await executeAutoTrade" templates/okx_trading.html
# 结果：直接调用，无confirm
```

## 可能的确认对话框来源

如果用户看到确认对话框，可能来自：

### 1. 浏览器安全提示
- 某些浏览器在弹窗或通知时会要求确认
- **解决方案**：允许网站通知权限

### 2. 浏览器扩展/插件
- 广告拦截器
- 隐私保护插件
- **解决方案**：将网站添加到白名单

### 3. Telegram通知权限
- 浏览器请求通知权限时的确认
- **解决方案**：允许通知

### 4. 其他页面功能
- 止盈止损警报
- 一键平仓确认
- **解决方案**：确认是哪个功能触发的

## 验证方法

### 1. 查看Console日志
```javascript
// 触发时应该看到：
🎯 触发条件满足！BTC价格 $66969 低于触发价 $67000
📊 准备对常用币(15个)中涨幅后8名开多单...
📢 策略执行完成通知已发送到Telegram

// 不应该看到：
❓ 等待用户确认...
⏸️ 等待确认对话框...
```

### 2. 禁用所有扩展
临时禁用浏览器所有扩展，重新测试

### 3. 使用无痕模式
在无痕模式下测试，排除缓存和扩展影响

## 确认策略已自动执行

查看PM2日志：
```bash
pm2 logs flask-app --lines 50 | grep "开仓金额"

# 应该看到：
📊 每个币种开仓金额: 2.98 USDT (总权益198.64 × 1.5%, 上限5U)
```

查看Telegram消息：
- 触发通知
- 完成通知
- 成功币种列表

## 结论

**代码中没有确认对话框，策略触发后会自动执行！**

如果用户仍然看到确认对话框，请提供：
1. 对话框出现的具体时机（开启开关？策略触发？）
2. 对话框的完整截图
3. 浏览器Console的日志输出

这样我们才能定位问题来源。
