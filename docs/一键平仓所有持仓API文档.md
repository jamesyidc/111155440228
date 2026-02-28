# 一键平仓所有持仓 API 文档

## API 概述

**接口名称**: 一键平仓所有持仓  
**接口路径**: `POST /api/okx-trading/close-all-positions`  
**功能说明**: 自动获取账户的所有持仓并逐个平仓，适用于止盈止损触发时需要快速清空所有仓位的场景。

---

## 请求参数

### 请求方法
```
POST /api/okx-trading/close-all-positions
```

### 请求头
```
Content-Type: application/json
```

### 请求体 (JSON)

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| apiKey | string | 是 | OKX API Key | "b0c18f2d-e014-4ae8-9c3c-cb02161de4db" |
| apiSecret | string | 是 | OKX API Secret | "92F864C599B2CE2EC5186AD14C8B4110" |
| passphrase | string | 是 | OKX API Passphrase | "Tencent@123" |
| accountId | string | 否 | 账户ID（用于日志记录） | "account_main" |

### 请求示例

```json
{
    "apiKey": "b0c18f2d-e014-4ae8-9c3c-cb02161de4db",
    "apiSecret": "92F864C599B2CE2EC5186AD14C8B4110",
    "passphrase": "Tencent@123",
    "accountId": "account_main"
}
```

---

## 响应参数

### 成功响应 (200 OK)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| success | boolean | 请求是否成功 |
| message | string | 操作结果消息 |
| totalPositions | integer | 总持仓数量 |
| closedCount | integer | 成功平仓数量 |
| failedCount | integer | 失败数量 |
| results | array | 每个持仓的平仓结果详情 |

#### results 数组元素结构

| 字段名 | 类型 | 说明 |
|--------|------|------|
| instId | string | 交易对（如 SOL-USDT-SWAP） |
| posSide | string | 持仓方向（long/short） |
| size | string | 持仓数量 |
| avgPx | string | 平均开仓价格 |
| upl | string | 未实现盈亏 |
| status | string | 平仓状态（success/failed/error） |
| message | string | 结果消息 |
| code | string | 错误代码（如果失败） |

### 响应示例

#### 全部成功
```json
{
    "success": true,
    "message": "一键平仓完成: 成功 8 个，失败 0 个",
    "totalPositions": 8,
    "closedCount": 8,
    "failedCount": 0,
    "results": [
        {
            "instId": "SOL-USDT-SWAP",
            "posSide": "long",
            "size": "10",
            "avgPx": "145.23",
            "upl": "2.50",
            "status": "success",
            "message": "平仓成功"
        },
        {
            "instId": "XRP-USDT-SWAP",
            "posSide": "long",
            "size": "50",
            "avgPx": "0.58",
            "upl": "-1.20",
            "status": "success",
            "message": "平仓成功"
        },
        ...
    ]
}
```

#### 部分成功
```json
{
    "success": true,
    "message": "一键平仓完成: 成功 6 个，失败 2 个",
    "totalPositions": 8,
    "closedCount": 6,
    "failedCount": 2,
    "results": [
        {
            "instId": "SOL-USDT-SWAP",
            "posSide": "long",
            "size": "10",
            "avgPx": "145.23",
            "upl": "2.50",
            "status": "success",
            "message": "平仓成功"
        },
        {
            "instId": "TAO-USDT-SWAP",
            "posSide": "long",
            "size": "5",
            "avgPx": "650.00",
            "upl": "-5.00",
            "status": "failed",
            "message": "余额不足",
            "code": "51008"
        },
        ...
    ]
}
```

#### 没有持仓
```json
{
    "success": true,
    "message": "当前没有持仓需要平仓",
    "closedCount": 0,
    "failedCount": 0,
    "results": []
}
```

### 错误响应

#### API凭证错误
```json
{
    "success": false,
    "error": "API凭证不完整"
}
```

#### 获取持仓失败
```json
{
    "success": false,
    "error": "获取持仓失败: Invalid API Key"
}
```

#### 网络超时
```json
{
    "success": false,
    "error": "API请求超时"
}
```

---

## 工作流程

### 1. 获取所有持仓
```
GET /api/v5/account/positions
↓
过滤出有持仓的(pos != '0')
↓
得到需要平仓的持仓列表
```

### 2. 获取账户持仓模式
```
GET /api/v5/account/config
↓
确定是双向持仓还是单向持仓
↓
决定是否需要传递 posSide 参数
```

### 3. 逐个平仓
```
对每个持仓:
  ├─ 构造平仓请求
  ├─ 调用 POST /api/v5/trade/close-position
  ├─ 记录结果（成功/失败）
  └─ 继续下一个
```

### 4. 返回汇总结果
```
汇总所有平仓结果
↓
记录到交易日志
↓
返回详细报告给前端
```

---

## 使用场景

### 场景 1：止盈触发后一键平仓
```javascript
// 用户设置止盈阈值为 +100 USDT
// 当前未实现盈亏达到 +102 USDT

// 1. 触发止盈警报
alert('🎉 止盈警报！当前盈利: +102 USDT');

// 2. 调用一键平仓API
const response = await fetch('/api/okx-trading/close-all-positions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        apiKey: account.apiKey,
        apiSecret: account.apiSecret,
        passphrase: account.passphrase,
        accountId: account.id
    })
});

const result = await response.json();
if (result.success) {
    alert(`✅ 已平仓 ${result.closedCount} 个持仓！`);
}
```

### 场景 2：止损触发后一键平仓
```javascript
// 用户设置止损阈值为 -50 USDT
// 当前未实现盈亏达到 -52 USDT

// 1. 触发止损警报
alert('⚠️ 止损警报！当前亏损: -52 USDT');

// 2. 调用一键平仓API
const response = await fetch('/api/okx-trading/close-all-positions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        apiKey: account.apiKey,
        apiSecret: account.apiSecret,
        passphrase: account.passphrase,
        accountId: account.id
    })
});

const result = await response.json();
if (result.success) {
    alert(`✅ 已平仓 ${result.closedCount} 个持仓！`);
}
```

### 场景 3：手动一键平仓
```javascript
// 用户点击"一键平仓"按钮

if (confirm('确定要平仓所有持仓吗？')) {
    const response = await fetch('/api/okx-trading/close-all-positions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            apiKey: account.apiKey,
            apiSecret: account.apiSecret,
            passphrase: account.passphrase,
            accountId: account.id
        })
    });
    
    const result = await response.json();
    console.log('平仓结果:', result);
}
```

---

## 技术特点

### ✅ 安全可靠
- 每个持仓独立处理，一个失败不影响其他
- 详细的错误处理和日志记录
- 支持双向持仓和单向持仓模式

### ✅ 详细报告
- 返回每个持仓的平仓结果
- 包含持仓信息（交易对、方向、数量、盈亏）
- 清晰的成功/失败统计

### ✅ 自动化
- 自动获取所有持仓
- 自动判断持仓模式
- 自动构造平仓请求

### ✅ 日志记录
- 记录到 okx_trading_logs
- 包含详细的平仓结果
- 便于后续追踪和分析

---

## 常见问题

### Q1: 如果部分持仓平仓失败怎么办？
**A**: API会继续平仓其他持仓，最后返回详细的成功/失败列表。用户可以查看失败原因并手动处理。

### Q2: 平仓顺序是什么？
**A**: 按照 OKX API 返回的持仓顺序依次平仓，通常是按创建时间排序。

### Q3: 会触发滑点吗？
**A**: 使用市价单平仓，可能存在滑点。建议在市场流动性充足时使用。

### Q4: 支持部分平仓吗？
**A**: 这个API是全部平仓。如需部分平仓，请使用单个平仓接口 `/api/okx-trading/close-position`。

### Q5: 平仓需要多长时间？
**A**: 取决于持仓数量，每个持仓约需 0.5-1 秒。8个持仓大约需要 4-8 秒。

---

## 注意事项

1. **API凭证安全**: 
   - API Key 和 Secret 需妥善保管
   - 不要在日志中记录完整凭证
   - 建议设置IP白名单

2. **市场风险**:
   - 市价单可能存在滑点
   - 极端行情可能导致平仓失败
   - 建议设置合理的止盈止损阈值

3. **频率限制**:
   - OKX API 有频率限制
   - 建议间隔使用，避免被限流
   - 失败时不要频繁重试

4. **持仓模式**:
   - 双向持仓模式需要指定 posSide
   - 单向持仓模式会自动判断方向
   - 系统会自动检测并适配

---

## 日志记录

### 日志存储位置
```
/home/user/webapp/data/okx_trading_logs/trading_log_YYYYMMDD.jsonl
```

### 日志格式示例
```json
{
    "timestamp": "2026-02-15T09:30:00.000000+08:00",
    "account_id": "account_main",
    "action": "close_all_positions",
    "details": {
        "totalPositions": 8,
        "successCount": 8,
        "failedCount": 0
    },
    "result": {
        "status": "completed",
        "results": [
            {
                "instId": "SOL-USDT-SWAP",
                "posSide": "long",
                "size": "10",
                "avgPx": "145.23",
                "upl": "2.50",
                "status": "success",
                "message": "平仓成功"
            },
            ...
        ]
    }
}
```

---

## 相关 API

### 单个持仓平仓
- **接口**: `POST /api/okx-trading/close-position`
- **说明**: 平仓单个指定的持仓，支持全部或部分平仓

### 获取持仓列表
- **接口**: `POST /api/okx-trading/positions`
- **说明**: 获取账户的所有持仓信息

### 获取交易日志
- **接口**: `GET /api/okx-trading/logs`
- **说明**: 查询交易日志，包含平仓记录

---

## 更新日志

- **2026-02-15**: 首次发布
  - 实现一键平仓所有持仓功能
  - 支持双向/单向持仓模式
  - 详细的平仓结果报告
  - 自动记录到交易日志

---

## 访问地址

**API地址**: https://9002-iou7okyaq15h840cyuitp-c07dda5e.sandbox.novita.ai/api/okx-trading/close-all-positions

**文档位置**: `/home/user/webapp/docs/一键平仓所有持仓API文档.md`

---

**文档完成时间**: 2026-02-15 09:32:00 UTC  
**提交记录**: commit 6b5aeff
