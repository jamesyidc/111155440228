# 📊 27币涨跌幅条件单系统 - 功能文档

**实现时间**: 2026-03-02 22:25  
**Git提交**: `d296e36`

---

## 🎯 功能概述

基于**27币涨跌幅之和**触发开仓策略的条件单系统，支持自动开空单和开多单。

---

## ✨ 核心功能

### **1️⃣ 条件单类型**

#### **情况1：开空单条件**
- **触发条件**: 27币涨跌幅之和 **高于** 设定阈值
- **执行动作**: 触发指定的**开空单策略**
- **示例**: 当27币涨跌幅之和 > +50% 时，触发"涨幅前8名做空"策略

#### **情况2：开多单条件**
- **触发条件**: 27币涨跌幅之和 **低于** 设定阈值
- **执行动作**: 触发指定的**开多单策略**
- **示例**: 当27币涨跌幅之和 < -30% 时，触发"跌幅后8名做多"策略

---

### **2️⃣ 策略选择**

#### **开空单策略列表**
| 策略编码 | 策略名称 | 描述 |
|---------|---------|------|
| `STG_SHORT_TOP8` | 涨幅前8名做空 | 对27币中涨幅前8名开空单 |
| `STG_SHORT_BOTTOM8` | 跌幅后8名做空 | 对27币中跌幅后8名（涨幅最小）开空单 |

#### **开多单策略列表**
| 策略编码 | 策略名称 | 描述 |
|---------|---------|------|
| `STG_LONG_TOP8` | 涨幅前8名做多 | 对27币中涨幅前8名开多单 |
| `STG_LONG_BOTTOM8` | 跌幅后8名做多 | 对27币中跌幅后8名（涨幅最小）开多单 |

---

### **3️⃣ 防重复触发设计**

#### **触发权限控制**
- **初始状态**: `allow_trigger: true`（允许触发）
- **触发后**: `allow_trigger: false`（不允许触发）
- **重置**: 手动重置或定时重置触发权限

#### **工作流程**
```
1. 条件单启用 (enabled: true)
2. 监控27币涨跌幅之和
3. 满足触发条件 AND allow_trigger=true
   → 执行开仓策略
   → allow_trigger 设置为 false
   → 记录触发时间和次数
4. 不再重复触发，直到手动重置
```

---

## 🔧 API端点

### **1. 获取条件单列表**
**端点**: `GET /api/okx-trading/coin-change-conditional-orders/<account_id>`

**响应**:
```json
{
    "success": true,
    "account_id": "account_main",
    "orders": [
        {
            "id": "cond_order_001",
            "enabled": true,
            "order_type": "open_short",
            "trigger_condition": "above",
            "trigger_value": 50.0,
            "target_strategy_code": "STG_SHORT_TOP8",
            "allow_trigger": true,
            "triggered_count": 0,
            "last_triggered_at": null,
            "created_at": "2026-03-02 22:30:00",
            "updated_at": "2026-03-02 22:30:00"
        }
    ],
    "total_orders": 1
}
```

---

### **2. 保存/更新条件单**
**端点**: `POST /api/okx-trading/coin-change-conditional-orders/<account_id>`

**请求体**:
```json
{
    "id": "cond_order_001",
    "enabled": true,
    "order_type": "open_short",
    "trigger_condition": "above",
    "trigger_value": 50.0,
    "target_strategy_code": "STG_SHORT_TOP8",
    "allow_trigger": true
}
```

**字段说明**:
- `id`: 条件单ID（可选，不提供则自动生成）
- `enabled`: 是否启用
- `order_type`: `open_short` | `open_long`
- `trigger_condition`: `above`（高于阈值） | `below`（低于阈值）
- `trigger_value`: 触发阈值（27币涨跌幅之和）
- `target_strategy_code`: 目标策略唯一编码
- `allow_trigger`: 是否允许触发

---

### **3. 删除条件单**
**端点**: `DELETE /api/okx-trading/coin-change-conditional-orders/<account_id>/<order_id>`

---

### **4. 重置触发权限**
**端点**: `POST /api/okx-trading/coin-change-conditional-orders/<account_id>/<order_id>/reset-trigger`

**功能**: 将 `allow_trigger` 重置为 `true`，允许再次触发

---

### **5. 获取可用策略列表**
**端点**: `GET /api/okx-trading/available-strategies/<account_id>?order_type=open_short`

**响应**:
```json
{
    "success": true,
    "account_id": "account_main",
    "strategies": [
        {
            "code": "STG_SHORT_TOP8",
            "name": "涨幅前8名做空",
            "type": "open_short",
            "description": "对27币中涨幅前8名开空单"
        }
    ]
}
```

---

## 📁 数据存储

### **JSONL文件格式**
**路径**: `/home/user/webapp/data/coin_change_conditional_orders/<account_id>_conditional_orders.jsonl`

**每行一条条件单**:
```json
{"id": "cond_order_001", "enabled": true, "order_type": "open_short", "trigger_condition": "above", "trigger_value": 50.0, "target_strategy_code": "STG_SHORT_TOP8", "allow_trigger": true, "triggered_count": 0, "last_triggered_at": null, "created_at": "2026-03-02 22:30:00", "updated_at": "2026-03-02 22:30:00"}
{"id": "cond_order_002", "enabled": true, "order_type": "open_long", "trigger_condition": "below", "trigger_value": -30.0, "target_strategy_code": "STG_LONG_BOTTOM8", "allow_trigger": true, "triggered_count": 0, "last_triggered_at": null, "created_at": "2026-03-02 22:35:00", "updated_at": "2026-03-02 22:35:00"}
```

---

## 🖥️ 前端UI设计（待实现）

### **页面位置**
https://9002-id51ob5t89zrt4phphxq8-5634da27.sandbox.novita.ai/okx-trading

### **UI布局**

#### **1. 条件单列表区域**（参考图片样式）

```
┌──────────────────────────────────────────────────────────┐
│  📊 27币涨跌幅条件单                        [➕ 新增条件单] │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  🟢 条件单 #1 [✅ 已启用]                    [编辑] [删除] │
│  ├─ 类型: 开空单                                          │
│  ├─ 触发条件: 27币涨跌幅之和 > +50.0%                     │
│  ├─ 目标策略: STG_SHORT_TOP8 (涨幅前8名做空)              │
│  ├─ 触发状态: ⭕ 允许触发                     [重置]      │
│  └─ 已触发次数: 0次                                       │
│                                                          │
│  🔴 条件单 #2 [⭕ 已禁用]                    [编辑] [删除] │
│  ├─ 类型: 开多单                                          │
│  ├─ 触发条件: 27币涨跌幅之和 < -30.0%                     │
│  ├─ 目标策略: STG_LONG_BOTTOM8 (跌幅后8名做多)            │
│  ├─ 触发状态: ❌ 禁止触发                     [重置]      │
│  └─ 已触发次数: 5次 | 上次触发: 2026-03-02 18:30:15      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

#### **2. 新增/编辑条件单表单**

```
┌──────────────────────────────────────────────┐
│  ➕ 新增条件单                                │
├──────────────────────────────────────────────┤
│  是否启用: [✓] 启用                           │
│                                              │
│  条件单类型:                                  │
│    ( ) 开空单  (●) 开多单                     │
│                                              │
│  触发条件:                                    │
│    27币涨跌幅之和  [▼ 高于 ▼]  [___50.0___] % │
│                                              │
│  目标策略:                                    │
│    [▼ STG_SHORT_TOP8 - 涨幅前8名做空 ▼]      │
│                                              │
│  [💾 保存]  [❌ 取消]                        │
└──────────────────────────────────────────────┘
```

---

## 🔄 监控脚本（待实现）

### **脚本功能**
- 定时检查27币涨跌幅之和
- 读取条件单配置
- 判断是否满足触发条件
- 检查 `allow_trigger` 权限
- 执行目标策略
- 更新触发状态

### **脚本文件**
`source_code/coin_change_conditional_order_monitor.py`

### **核心逻辑**
```python
# 1. 获取27币涨跌幅之和
total_change = get_27_coin_total_change()

# 2. 读取条件单
orders = load_conditional_orders(account_id)

# 3. 检查每个条件单
for order in orders:
    if not order['enabled'] or not order['allow_trigger']:
        continue
    
    # 判断是否触发
    triggered = False
    if order['trigger_condition'] == 'above' and total_change > order['trigger_value']:
        triggered = True
    elif order['trigger_condition'] == 'below' and total_change < order['trigger_value']:
        triggered = True
    
    if triggered:
        # 执行策略
        execute_strategy(order['target_strategy_code'])
        
        # 更新状态
        order['allow_trigger'] = False
        order['triggered_count'] += 1
        order['last_triggered_at'] = now()
        save_order(order)
```

---

## 🎨 UI样式参考

### **颜色主题**
- **开空单**: 橙红色渐变 `linear-gradient(135deg, #ff6b6b, #ee5a24)`
- **开多单**: 绿色渐变 `linear-gradient(135deg, #0be881, #05c46b)`
- **已启用**: 绿色边框 `#10b981`
- **已禁用**: 灰色边框 `#6b7280`

### **状态图标**
- ✅ 已启用
- ⭕ 已禁用
- ⭕ 允许触发（绿色）
- ❌ 禁止触发（红色）

---

## ✅ 验证步骤

### **1. API测试**
```bash
# 获取条件单列表
curl http://localhost:9002/api/okx-trading/coin-change-conditional-orders/account_main

# 获取可用策略（开空单）
curl http://localhost:9002/api/okx-trading/available-strategies/account_main?order_type=open_short

# 获取可用策略（开多单）
curl http://localhost:9002/api/okx-trading/available-strategies/account_main?order_type=open_long
```

### **2. 创建测试条件单**
```bash
curl -X POST http://localhost:9002/api/okx-trading/coin-change-conditional-orders/account_main \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "order_type": "open_short",
    "trigger_condition": "above",
    "trigger_value": 50.0,
    "target_strategy_code": "STG_SHORT_TOP8",
    "allow_trigger": true
  }'
```

---

## 📝 后续任务

### **待实现功能**
1. ⏳ 前端UI页面集成到 `/okx-trading`
2. ⏳ 条件单监控脚本
3. ⏳ PM2配置自动启动
4. ⏳ 触发日志记录
5. ⏳ 策略执行记录
6. ⏳ Telegram通知

---

## 🎉 总结

✅ **API端点已完成**
- 条件单CRUD操作
- 触发权限管理
- 策略列表查询
- JSONL持久化存储

⏳ **待完成**
- 前端UI集成
- 监控脚本
- 自动触发机制

---

**实现时间**: 2026-03-02 22:25  
**状态**: API已完成，前端UI和监控脚本待实现
