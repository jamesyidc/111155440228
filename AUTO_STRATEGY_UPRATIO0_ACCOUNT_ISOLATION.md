# 上涨占比0策略账号独立控制说明

## 📋 概述

本文档说明上涨占比0自动策略的账号独立控制机制，确保每个账号的策略完全独立运行，不会相互干扰。

**实施日期**: 2026-02-17  
**版本**: v2.0 - Account Isolation  

---

## 🔐 账号独立机制

### JSONL文件结构

每个账号每个策略都有独立的JSONL执行许可文件：

```
data/okx_auto_strategy/
├── account_main_upratio0_top8_execution.jsonl       # 主账户-涨幅前8名
├── account_main_upratio0_bottom8_execution.jsonl    # 主账户-涨幅后8名
├── account_fangfang12_upratio0_top8_execution.jsonl    # fangfang12账户-涨幅前8名
├── account_fangfang12_upratio0_bottom8_execution.jsonl # fangfang12账户-涨幅后8名
├── account_poit_upratio0_top8_execution.jsonl       # poit账户-涨幅前8名
├── account_poit_upratio0_bottom8_execution.jsonl    # poit账户-涨幅后8名
├── account_marks_upratio0_top8_execution.jsonl      # marks账户-涨幅前8名
└── account_marks_upratio0_bottom8_execution.jsonl   # marks账户-涨幅后8名
```

### JSONL记录格式

```json
{
  "timestamp": "2026-02-17T11:45:30.123456",
  "time": "2026-02-17 11:45:30",
  "account_id": "account_main",
  "strategy_type": "top8",
  "allowed": true,
  "reason": "User enabled strategy",
  "up_ratio": 0
}
```

**字段说明**:
- `timestamp`: ISO格式时间戳
- `time`: 可读时间格式
- `account_id`: 账户ID
- `strategy_type`: 策略类型（top8/bottom8）
- `allowed`: 是否允许执行（true/false）
- `reason`: 原因说明
- `up_ratio`: 触发时的上涨占比（执行时记录）

---

## 🎯 工作流程

### 用户开启策略

1. **用户操作**: 点击开关启用策略
2. **前端处理**: 
   - 捕获开关change事件
   - 获取当前账户ID
   - 调用API写入JSONL
3. **API调用**: 
   ```
   POST /api/okx-trading/set-allowed-upratio0/{account_id}/top8
   Body: { "allowed": true, "reason": "User enabled strategy" }
   ```
4. **JSONL写入**: 
   - 追加新记录到对应账户的JSONL文件
   - `allowed = true`
5. **UI反馈**: 
   - 策略状态显示"监控中"
   - 控制台输出"已写入JSONL：允许执行"

### 定时检查触发（每60秒）

1. **检查开关**: 开关是否启用？
2. **检查时间**: 当前时间是否在0:00-0:30？
3. **检查上涨占比**: up_ratio是否等于0？
4. **🔒 检查JSONL**: 
   ```
   GET /api/okx-trading/check-allowed-upratio0/{account_id}/top8
   返回: { "success": true, "allowed": true/false }
   ```
5. **判断逻辑**:
   ```
   if (开关启用 && 时间允许 && up_ratio === 0 && JSONL允许) {
       执行策略
   } else {
       跳过本次检查
   }
   ```

### 策略执行

1. **设置执行锁**: `strategyExecuting = true`
2. **执行开单**: 调用`executeUpRatio0Strategy()`
3. **执行成功后**:
   - **立即写入JSONL**: `allowed = false`
   - 关闭UI开关
   - 更新状态显示
   - 通知用户
4. **释放执行锁**: `strategyExecuting = false`

### 用户关闭策略

1. **用户操作**: 点击开关关闭策略
2. **API调用**: 
   ```
   POST /api/okx-trading/set-allowed-upratio0/{account_id}/top8
   Body: { "allowed": false, "reason": "User disabled strategy" }
   ```
3. **JSONL写入**: 
   - 追加新记录
   - `allowed = false`
4. **UI反馈**: 
   - 策略状态显示"未启用"

---

## 🛡️ 防重复机制（三层防护）

### 第一层：JSONL文件锁（最重要）

**作用**: 跨设备、跨浏览器、跨会话有效

**流程**:
1. 执行前检查JSONL最后一条记录
2. 只有`allowed = true`才允许执行
3. 执行后立即写入`allowed = false`

**优势**:
- ✅ 即使多个浏览器同时打开，只有第一个触发的请求能执行
- ✅ 数据持久化，重启浏览器不影响
- ✅ 每个账号独立控制

### 第二层：全局执行锁

**作用**: 同一页面内防止并发

**流程**:
1. 执行前检查`strategyExecuting`
2. 如果为`true`，跳过本次执行
3. 设置为`true`后执行
4. 执行完成后设置为`false`

### 第三层：自动关闭开关

**作用**: 用户界面反馈

**流程**:
1. 执行成功后自动关闭UI开关
2. 需要手动重新开启才能再次触发

---

## 📊 账号隔离示例

### 场景：4个账号同时使用

| 账号 | 策略A（涨幅前8名） | 策略B（涨幅后8名） | 独立JSONL |
|------|-------------------|-------------------|----------|
| 主账户 | ✅ 已启用 | ❌ 未启用 | account_main_upratio0_top8.jsonl<br>account_main_upratio0_bottom8.jsonl |
| fangfang12 | ❌ 未启用 | ✅ 已启用 | account_fangfang12_upratio0_top8.jsonl<br>account_fangfang12_upratio0_bottom8.jsonl |
| poit | ✅ 已启用 | ✅ 已启用 | account_poit_upratio0_top8.jsonl<br>account_poit_upratio0_bottom8.jsonl |
| marks | ❌ 未启用 | ❌ 未启用 | account_marks_upratio0_top8.jsonl<br>account_marks_upratio0_bottom8.jsonl |

### 触发时的行为

**假设**: 上涨占比 = 0%，当前时间 = 10:00

1. **主账户**: 
   - 策略A检查JSONL → allowed=true → ✅ 执行
   - 策略B未启用 → 跳过
   
2. **fangfang12**: 
   - 策略A未启用 → 跳过
   - 策略B检查JSONL → allowed=true → ✅ 执行
   
3. **poit**: 
   - 策略A检查JSONL → allowed=true → ✅ 执行（等待主账户完成）
   - 策略B检查JSONL → allowed=true → ✅ 执行（等待策略A完成）
   
4. **marks**: 
   - 策略A未启用 → 跳过
   - 策略B未启用 → 跳过

**结果**: 每个账号独立执行，互不干扰

---

## 🔄 与BTC价格策略对比

| 特性 | BTC价格策略 | 上涨占比0策略 |
|------|------------|--------------|
| 触发条件 | BTC价格 < 设定价格 | up_ratio = 0 |
| JSONL文件 | `{account_id}_execution.jsonl` | `{account_id}_upratio0_{top8\|bottom8}_execution.jsonl` |
| API端点 | `/api/okx-trading/check-allowed/{account_id}` | `/api/okx-trading/check-allowed-upratio0/{account_id}/{strategy_type}` |
| 账号独立 | ✅ | ✅ |
| JSONL控制 | ✅ | ✅ |
| 执行锁 | ✅ | ✅ |
| 自动关闭 | ✅ | ✅ |
| 时间排除 | ❌ | ✅ (0:00-0:30) |

---

## 📝 API接口

### 检查执行许可

**端点**: `GET /api/okx-trading/check-allowed-upratio0/<account_id>/<strategy_type>`

**参数**:
- `account_id`: 账户ID（如account_main）
- `strategy_type`: 策略类型（top8或bottom8）

**返回**:
```json
{
  "success": true,
  "allowed": true,
  "reason": "Read from JSONL",
  "lastRecord": {
    "timestamp": "2026-02-17T11:45:30.123456",
    "account_id": "account_main",
    "strategy_type": "top8",
    "allowed": true,
    "reason": "User enabled strategy"
  }
}
```

### 设置执行许可

**端点**: `POST /api/okx-trading/set-allowed-upratio0/<account_id>/<strategy_type>`

**参数**:
- `account_id`: 账户ID
- `strategy_type`: 策略类型（top8或bottom8）

**请求体**:
```json
{
  "allowed": true,
  "reason": "User enabled strategy",
  "upRatio": 0
}
```

**返回**:
```json
{
  "success": true,
  "message": "Execution allowed status set to true for top8",
  "record": {
    "timestamp": "2026-02-17T11:45:30.123456",
    "time": "2026-02-17 11:45:30",
    "account_id": "account_main",
    "strategy_type": "top8",
    "allowed": true,
    "reason": "User enabled strategy",
    "up_ratio": 0
  }
}
```

---

## 🧪 测试验证

### 测试1：账号独立性

1. 切换到账户A，启用策略A
2. 切换到账户B，启用策略A
3. 触发条件满足
4. **预期**: 两个账户分别执行，互不干扰

### 测试2：JSONL防重复

1. 账户A启用策略A
2. 打开两个浏览器窗口
3. 同时触发条件
4. **预期**: 只有一个窗口成功执行

### 测试3：自动关闭

1. 账户A启用策略A
2. 触发条件满足，执行成功
3. **预期**: 开关自动关闭，JSONL写入allowed=false

### 测试4：切换账号

1. 账户A启用策略A
2. 切换到账户B
3. 账户B的策略A开关状态
4. **预期**: 账户B的开关是独立的（未启用）

---

## 🔍 故障排查

### 策略未执行

**检查步骤**:
1. 查看控制台日志
2. 检查JSONL文件是否存在
3. 检查JSONL最后一条记录的allowed状态
4. 确认账户ID是否正确

**常见原因**:
- JSONL文件中allowed=false
- 开关未启用
- 时间在排除时段（0:00-0:30）
- 执行锁被占用

### JSONL文件位置

```bash
cd /home/user/webapp/data/okx_auto_strategy
ls -l *upratio0*
```

### 查看JSONL内容

```bash
# 查看主账户涨幅前8名策略的最后一条记录
tail -1 account_main_upratio0_top8_execution.jsonl | jq .
```

---

## ✅ 验证清单

- ✅ 每个账号有独立的JSONL文件
- ✅ 开关启用时写入allowed=true
- ✅ 开关关闭时写入allowed=false
- ✅ 执行成功后写入allowed=false
- ✅ 执行前检查JSONL状态
- ✅ 不同账号策略互不干扰
- ✅ 同一账号不同策略独立控制
- ✅ 全局执行锁防止并发
- ✅ 时间排除机制生效
- ✅ 自动关闭开关正常

---

## 📞 技术支持

如有问题，请检查：
1. 控制台日志
2. JSONL文件内容
3. 网络请求（F12 → Network）
4. API返回结果

**服务地址**: https://9002-iou7okyaq15h840cyuitp-c07dda5e.sandbox.novita.ai/okx-trading

---

## 📄 更新日志

### v2.0 (2026-02-17)
- ✅ 实现账号独立JSONL控制
- ✅ 添加策略类型区分（top8/bottom8）
- ✅ 与BTC价格策略逻辑一致
- ✅ 完整的API接口实现

### v1.0 (2026-02-17)
- ✅ 初始版本
- ✅ 基础策略实现

---

**重要提醒**: 每个账号的策略完全独立，不会相互影响。开启某个账号的策略不会影响其他账号。
