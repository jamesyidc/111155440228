# Telegram通知系统完整说明

## 📋 系统概述

本系统包含**13个独立的TG推送功能**，分为两大类：
1. **重大事件监控系统**（9个事件）
2. **其他监控系统**（4个系统）

---

## 🚨 重大事件监控系统（9个事件）

**来源文件**: `major-events-system/major_events_monitor.py`  
**PM2进程**: `major-events-monitor`

### 事件1：高强度见顶诱多 ✅ 已开启
- **图标**: 📊
- **触发条件**: 2h见顶信号数量 = 120
- **操作建议**: 开空
- **代码位置**: `check_event_1_high_intensity_top()`
- **推送内容**: 包含峰值信息、时间戳、操作建议

### 事件2：一般强度见顶诱多 ✅ 已开启
- **图标**: 📊
- **触发条件**: 2h见顶信号数量 10-120之间
- **操作建议**: 开空（谨慎）
- **代码位置**: `check_event_2_normal_intensity_top()`
- **推送内容**: 包含两次峰值对比、时间间隔

### 事件3：强空头爆仓 ✅ 已开启
- **图标**: 💥
- **触发条件**: 
  - 1小时爆仓金额 ≥ 3000万美元
  - 10分钟内持续创新高
- **操作建议**: 开空
- **代码位置**: `check_liquidation_events()`
- **推送内容**: 爆仓金额、增幅、持续时间

### 事件4：弱空头爆仓 ❌ 已关闭
- **图标**: 💥
- **触发条件**: 
  - 1小时爆仓金额 ≥ 3000万美元
  - 10分钟内未持续创新高
- **操作建议**: 开空（谨慎）
- **代码位置**: `check_liquidation_events()`
- **状态**: **已关闭** - 避免弱信号干扰

### 事件5：绿色信号转红色信号 ✅ 已开启
- **图标**: 🔄
- **触发条件**: 
  - 锚定系统短期盈利 ≥ 120%
  - 转为短期亏损 ≥ 3%
- **操作建议**: 开空
- **代码位置**: `check_event_5_profit_trend_reversal()`
- **数据来源**: `anchor_profit_stats.jsonl`

### 事件6：红色信号转绿色信号 ✅ 已开启
- **图标**: 🔄
- **触发条件**: 
  - 锚定系统短期亏损 ≥ 3%
  - 转为短期盈利 ≥ 120%
- **操作建议**: 开多
- **代码位置**: `check_event_6_loss_trend_reversal()`
- **数据来源**: `anchor_profit_stats.jsonl`

### 事件7：一般逃顶事件 ✅ 已开启
- **图标**: 📉
- **触发条件**: 
  - 时间：03:00-24:00 北京时间
  - 27币涨跌幅绝对值和 > 60
  - 新高后10分钟内未创新高
  - SAR空头信号 ≥ 80%（计数 ≥ 20）
- **操作建议**: 开空
- **代码位置**: `check_event_7_general_top_escape()`
- **每日重置**: 每天00:00重置状态

### 事件8：一般抄底事件 ✅ 已开启
- **图标**: 📈
- **触发条件**: 
  - 时间：03:00-24:00 北京时间
  - 27币涨跌幅绝对值和 > 60
  - 新低后10分钟内未创新低
  - SAR多头信号 ≥ 80%（计数 ≥ 7）
- **操作建议**: 开多
- **代码位置**: `check_event_8_general_bottom_dip()`
- **每日重置**: 每天00:00重置状态

### 事件9：超强爆仓之后的主跌 ✅ 已开启
- **图标**: 🌊
- **触发条件**: 
  - 1小时爆仓金额 ≥ 1.5亿美元（15000万美元）
  - 达到阈值后监控总涨跌幅
  - 阶段性高点后10分钟未创新高
- **操作建议**: 开空
- **代码位置**: `check_event_9_super_liquidation_main_drop()`
- **冷却期**: 触发后1小时内不再触发
- **特点**: 超大爆仓信号，高确定性

---

## 📊 其他监控系统（4个系统）

### 1. 极值追踪系统提醒 ❌ 已关闭
- **图标**: 🎯
- **来源文件**: `extreme_value_tracker.py`
- **PM2进程**: `extreme-value-tracker`
- **功能**: 
  - 监控27个币种的极值突破
  - 检测中度跳幅（涨跌幅较大）
  - 检测重度跳幅（涨跌幅巨大）
- **推送内容**: 
  - 币种名称
  - 当前价格
  - 涨跌幅度
  - 跳幅等级
- **状态**: **已关闭** - 避免频繁推送干扰
- **数据文件**: `data/extreme_tracking/`

### 2. 支撑压力线系统 ✅ 已开启
- **图标**: 📏
- **来源文件**: `support_resistance_snapshot.py`
- **PM2进程**: `support-resistance-snapshot`
- **功能**: 
  - 计算27个币种的支撑压力线
  - 检测价格突破支撑/压力位
  - 每天生成新的支撑压力数据
- **推送内容**: 
  - 币种名称
  - 突破类型（向上/向下）
  - 当前价格
  - 支撑/压力位价格
- **数据文件**: `data/support_resistance_daily/`

### 3. 计次预警系统 ❌ 已关闭
- **图标**: ⚠️
- **来源文件**: **需要确认**
- **功能**: **未知** - 需要进一步调查
- **状态**: 已关闭
- **备注**: 这个系统的具体实现和来源文件需要进一步确认

### 4. 交易信号系统 ✅ 已开启
- **图标**: 💹
- **来源文件**: **需要确认**
- **功能**: **未知** - 可能与其他交易信号相关
- **状态**: 已开启
- **备注**: 需要确认具体的信号来源和推送逻辑

---

## 🔧 配置文件

### 位置
```
/home/user/webapp/telegram_notification_config.json
```

### 当前配置
```json
{
  "major_events": {
    "event1_high_intensity_top": { "enabled": true },
    "event2_normal_intensity_top": { "enabled": true },
    "event3_strong_short_liquidation": { "enabled": true },
    "event4_weak_short_liquidation": { "enabled": false },  ← 已关闭
    "event5_profit_trend_reversal": { "enabled": true },
    "event6_loss_trend_reversal": { "enabled": true },
    "event7_general_top_escape": { "enabled": true },
    "event8_general_bottom_dip": { "enabled": true },
    "event9_super_liquidation_main_drop": { "enabled": true }
  },
  "extreme_tracking": { "enabled": false },  ← 已关闭
  "support_resistance": { "enabled": true },
  "alert_system": { "enabled": false },  ← 已关闭
  "trading_signals": { "enabled": true }
}
```

---

## 📱 管理界面

### 通知设置页面
🔗 **https://5000-iehbqwjte74vmohs308jg-d0b9e1e2.sandbox.novita.ai/telegram-notification-settings**

**功能**:
- ✅ 查看所有13个推送系统
- ✅ 一键开启/关闭任意系统
- ✅ 查看系统来源文件和触发条件
- ✅ 实时保存配置

**新增功能**（刚刚更新）:
- ✅ 每个系统显示来源文件（如 `major_events_monitor.py`）
- ✅ 每个事件显示触发条件详情
- ✅ 标记未知来源的系统

### 推送历史页面
🔗 **https://5000-iehbqwjte74vmohs308jg-d0b9e1e2.sandbox.novita.ai/telegram-dashboard**

**功能**:
- ✅ 查看历史推送记录
- ✅ 统计推送数量
- ✅ 查看消息内容

---

## 🔍 系统来源分析

### 已确认的来源文件

#### major_events_monitor.py
- ✅ 事件1-9（9个事件）
- ✅ 完整的监控逻辑
- ✅ Telegram推送集成
- ✅ PM2进程：major-events-monitor

#### extreme_value_tracker.py
- ✅ 极值追踪系统
- ✅ 27个币种监控
- ✅ PM2进程：extreme-value-tracker

#### support_resistance_snapshot.py
- ✅ 支撑压力线系统
- ✅ 每日数据快照
- ✅ PM2进程：support-resistance-snapshot

### 需要确认的系统

#### ❓ 计次预警系统（alert_system）
- **状态**: 配置中存在，但来源未知
- **可能位置**: 
  - 可能在 `app.py` 中
  - 可能在某个collector脚本中
  - 需要搜索 "alert" 关键词

#### ❓ 交易信号系统（trading_signals）
- **状态**: 配置中存在，但来源未知
- **可能位置**: 
  - 可能在 `app.py` 中
  - 可能与其他交易系统集成
  - 需要搜索 "trading signal" 关键词

---

## 🔄 推送流程

### 1. 数据采集
```
各个collector进程 → 写入JSONL数据文件 → 定时更新
```

### 2. 事件检测
```
monitor进程 → 读取数据文件 → 检查触发条件 → 生成事件
```

### 3. 配置检查
```
生成事件 → 读取notification_config.json → 检查是否enabled
```

### 4. Telegram推送
```
enabled=true → 调用send_telegram_message() → 发送到TG群组
```

### 5. 记录日志
```
推送成功 → 写入major_events.jsonl → 可在dashboard查看
```

---

## 📊 PM2进程列表

### 与TG推送相关的进程
```bash
pm2 status

major-events-monitor         # 重大事件监控（事件1-9）
extreme-value-tracker        # 极值追踪系统
support-resistance-snapshot  # 支撑压力线系统
flask-app                    # Web服务（API和页面）
```

### 查看日志
```bash
pm2 logs major-events-monitor  # 查看重大事件日志
pm2 logs extreme-value-tracker # 查看极值追踪日志
pm2 logs flask-app            # 查看Flask日志
```

---

## 🎯 用户推荐配置

### 适合大多数用户的配置

#### ✅ 建议开启（高质量信号）
1. ✅ 事件1：高强度见顶诱多
2. ✅ 事件2：一般强度见顶诱多
3. ✅ 事件3：强空头爆仓
4. ✅ 事件5：绿色信号转红色
5. ✅ 事件6：红色信号转绿色
6. ✅ 事件7：一般逃顶事件
7. ✅ 事件8：一般抄底事件
8. ✅ 事件9：超强爆仓主跌
9. ✅ 支撑压力线系统

#### ❌ 建议关闭（噪音较多）
1. ❌ 事件4：弱空头爆仓 - 信号质量较低
2. ❌ 极值追踪系统 - 推送频繁，容易干扰

#### ⚠️ 待确认
1. ⚠️ 计次预警系统 - 需要确认功能
2. ⚠️ 交易信号系统 - 需要确认来源

---

## 🚀 下一步优化建议

### 1. 确认未知系统
- [ ] 找到计次预警系统的源代码
- [ ] 找到交易信号系统的源代码
- [ ] 在设置页面添加完整说明

### 2. 增加推送统计
- [ ] 统计每个系统的推送次数
- [ ] 分析推送时间分布
- [ ] 评估信号质量

### 3. 优化配置体验
- [ ] 添加推送预览功能
- [ ] 添加测试推送功能
- [ ] 添加推送历史筛选

### 4. 文档完善
- [ ] 为每个事件创建详细说明文档
- [ ] 添加历史成功案例
- [ ] 添加使用教程

---

## 📝 版本历史

### v2.0 (2026-02-06)
- ✅ 添加系统来源标识
- ✅ 添加触发条件描述
- ✅ 标记未知来源系统
- ✅ 优化设置页面显示

### v1.0 (2026-02-06)
- ✅ 实现TG通知开关系统
- ✅ 创建设置页面
- ✅ 集成到首页
- ✅ 添加配置文件管理

---

**文档生成时间**: 2026-02-06 02:30:00 UTC  
**文档版本**: 2.0  
**系统版本**: webapp v2.2.0
