# 见底信号做多策略 - 完整功能说明

## 📋 创建时间
**2026-02-21** - 所有功能已完整实现并验证

---

## 🎯 策略概述

**见底信号做多策略** 是基于市场情绪底部背离信号和RSI指标的自动做多策略，与见顶信号做空策略形成对称设计。

### ✅ 两个做多策略

#### 策略1：见底信号+涨幅前8做多 🎯
- **触发条件**：
  - 出现**"🎯见底信号"**（底部背离）
  - **RSI总和 < 800**（可配置：300-1500）
  - 自动对**涨幅前8名币种**开多单
- **杠杆**：10倍
- **仓位配置**：
  - 总投入：可用余额 × 1.5%
  - 分配方式：平均分配给8个币种
  - 单币限额：默认 5.0 USDT（可配置：1-100 USDT）
- **监控频率**：每60秒检查一次
- **冷却机制**：触发后1小时内不重复执行

#### 策略2：见底信号+涨幅后8做多 🎯
- **触发条件**：
  - 出现**"🎯见底信号"**（底部背离）
  - **RSI总和 < 800**（可配置：300-1500）
  - 自动对**涨幅后8名币种**开多单
- **杠杆**：10倍
- **仓位配置**：
  - 总投入：可用余额 × 1.5%
  - 分配方式：平均分配给8个币种
  - 单币限额：默认 5.0 USDT（可配置：1-100 USDT）
- **监控频率**：每60秒检查一次
- **冷却机制**：触发后1小时内不重复执行

---

## 🎨 前端UI设计

### 卡片位置
- 位于"RSI自动开仓策略"黄色卡片内
- 在"见顶信号做空策略"之后

### 视觉设计

#### 策略1：见底信号+涨幅前8做多
- **背景色**：浅绿色（`rgba(34, 197, 94, 0.1)`）
- **边框色**：深绿色（`#22c55e`）
- **文字色**：深绿色（`#166534`）
- **图标**：🎯

#### 策略2：见底信号+涨幅后8做多
- **背景色**：翠绿色（`rgba(16, 185, 129, 0.1)`）
- **边框色**：翠绿色（`#10b981`）
- **文字色**：深绿色（`#065f46`）
- **图标**：🎯

### UI组件

每个策略包含：
1. **开关**：启用/禁用策略
2. **触发条件说明**：清晰展示触发逻辑
3. **参数设置区域**：
   - RSI阈值输入框（300-1500，默认800）
   - 单币限额输入框（1-100 USDT，默认5）
   - 💾 保存按钮
4. **资金配置说明**：仓位计算方式
5. **监控频率说明**：检查间隔和冷却机制

---

## 🔧 技术实现细节

### 前端代码位置
**文件：** `templates/okx_trading.html`

#### 1. UI组件（第3317-3403行）

**策略1 UI（第3317-3359行）：**
```html
<!-- 见底信号做多策略 - 涨幅前8 -->
<div style="margin-top: 10px; padding: 10px; background: rgba(34, 197, 94, 0.1); border-radius: 8px; border: 1px solid #22c55e;">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
        <span style="color: #166534; font-weight: 600; font-size: 13px;">🎯 见底信号+涨幅前8做多</span>
        <label class="switch">
            <input type="checkbox" id="bottomSignalTop8LongSwitch">
            <span class="slider slider-bottom-signal-top8-long"></span>
        </label>
    </div>
    
    <!-- 触发条件 -->
    <strong>触发条件：</strong>
    <ul>
        <li>出现<strong>"🎯见底信号"</strong>（底部背离）</li>
        <li><strong>RSI总和 < <span id="bottomSignalTop8RsiThresholdDisplay">800</span></strong></li>
        <li>自动对<strong>涨幅前8名币种</strong>开多单（10倍杠杆）</li>
    </ul>
    
    <!-- 参数设置 -->
    <strong>参数设置：</strong>
    <div style="display: flex; gap: 10px;">
        <div>
            <label>RSI阈值</label>
            <input type="number" id="bottomSignalTop8RsiThreshold" value="800" 
                   step="10" min="300" max="1500"
                   onchange="updateBottomSignalTop8Display()">
        </div>
        <div>
            <label>单币限额(USDT)</label>
            <input type="number" id="bottomSignalTop8MaxOrder" value="5" 
                   step="1" min="1" max="100">
        </div>
        <button onclick="saveBottomSignalTop8Config()">💾 保存</button>
    </div>
    
    <!-- 资金配置说明 -->
    <strong>资金配置：</strong>
    <ul>
        <li>总投入：可用余额的 <strong>1.5%</strong></li>
        <li>分配方式：平均分配给8个币种</li>
        <li>单币限额：最高 <strong><span id="bottomSignalTop8MaxOrderDisplay">5.0</span> USDT</strong></li>
    </ul>
</div>
```

**策略2 UI（第3361-3403行）：** 结构相同，ID改为 `bottomSignalBottom8*`

#### 2. JavaScript函数

**更新显示函数（第8082-8095行）：**
```javascript
// 更新见底信号Top8策略显示
function updateBottomSignalTop8Display() {
    const rsiThreshold = document.getElementById('bottomSignalTop8RsiThreshold').value;
    const maxOrder = document.getElementById('bottomSignalTop8MaxOrder').value;
    document.getElementById('bottomSignalTop8RsiThresholdDisplay').textContent = rsiThreshold;
    document.getElementById('bottomSignalTop8MaxOrderDisplay').textContent = parseFloat(maxOrder).toFixed(1);
}

// 更新见底信号Bottom8策略显示
function updateBottomSignalBottom8Display() {
    const rsiThreshold = document.getElementById('bottomSignalBottom8RsiThreshold').value;
    const maxOrder = document.getElementById('bottomSignalBottom8MaxOrder').value;
    document.getElementById('bottomSignalBottom8RsiThresholdDisplay').textContent = rsiThreshold;
    document.getElementById('bottomSignalBottom8MaxOrderDisplay').textContent = parseFloat(maxOrder).toFixed(1);
}
```

**保存配置函数（第8098-8186行）：**
```javascript
// 保存见底信号Top8策略配置
async function saveBottomSignalTop8Config() {
    const account = accounts.find(acc => acc.id === currentAccount);
    if (!account) {
        alert('❌ 请先选择账户');
        return;
    }
    
    const rsiThreshold = parseInt(document.getElementById('bottomSignalTop8RsiThreshold').value);
    const maxOrder = parseFloat(document.getElementById('bottomSignalTop8MaxOrder').value);
    
    // 验证输入
    if (rsiThreshold < 300 || rsiThreshold > 1500) {
        alert('❌ RSI阈值必须在300-1500之间');
        return;
    }
    
    if (maxOrder < 1 || maxOrder > 100) {
        alert('❌ 单币限额必须在1-100 USDT之间');
        return;
    }
    
    try {
        const response = await fetch(`/api/okx-trading/save-bottom-signal-config/${account.id}/top8_long`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                enabled: document.getElementById('bottomSignalTop8LongSwitch').checked,
                rsi_threshold: rsiThreshold,
                max_order_usdt: maxOrder,
                position_percent: 1.5,
                leverage: 10
            })
        });
        
        const result = await response.json();
        if (result.success) {
            updateBottomSignalTop8Display();
            alert(`✅ 配置保存成功！\n\n账户：${account.name}\nRSI阈值：${rsiThreshold}\n单币限额：${maxOrder} USDT`);
        } else {
            alert(`❌ 保存失败：${result.error || '未知错误'}`);
        }
    } catch (e) {
        console.error('Save bottom signal top8 config error:', e);
        alert(`❌ 保存失败: ${e.message}`);
    }
}

// 保存见底信号Bottom8策略配置（类似实现）
async function saveBottomSignalBottom8Config() {
    // ... 类似实现，调用 /api/okx-trading/save-bottom-signal-config/${account.id}/bottom8_long
}
```

**加载配置函数（集成在账户切换中）：**
```javascript
// 加载见底信号做多策略配置
const top8Response = await fetch(`/api/okx-trading/get-bottom-signal-config/${account.id}/top8_long`);
const top8Data = await top8Response.json();
if (top8Data.success && top8Data.config) {
    document.getElementById('bottomSignalTop8LongSwitch').checked = top8Data.config.enabled || false;
    document.getElementById('bottomSignalTop8RsiThreshold').value = top8Data.config.rsi_threshold || 800;
    document.getElementById('bottomSignalTop8MaxOrder').value = top8Data.config.max_order_usdt || 5;
    updateBottomSignalTop8Display();
}

const bottom8Response = await fetch(`/api/okx-trading/get-bottom-signal-config/${account.id}/bottom8_long`);
const bottom8Data = await bottom8Response.json();
if (bottom8Data.success && bottom8Data.config) {
    document.getElementById('bottomSignalBottom8LongSwitch').checked = bottom8Data.config.enabled || false;
    document.getElementById('bottomSignalBottom8RsiThreshold').value = bottom8Data.config.rsi_threshold || 800;
    document.getElementById('bottomSignalBottom8MaxOrder').value = bottom8Data.config.max_order_usdt || 5;
    updateBottomSignalBottom8Display();
}
```

### 后端API
**文件：** `app.py`

#### 1. 保存配置API（第17046-17112行）

**路由：** `POST /api/okx-trading/save-bottom-signal-config/<account_id>/<strategy_type>`

**参数：**
- `account_id`: 账户ID（如 `account_main`）
- `strategy_type`: 策略类型（`top8_long` 或 `bottom8_long`）

**请求体：**
```json
{
    "enabled": true,
    "rsi_threshold": 800,
    "max_order_usdt": 5.0,
    "position_percent": 1.5,
    "leverage": 10
}
```

**响应：**
```json
{
    "success": true,
    "message": "底部信号 top8_long 配置已保存",
    "config": {
        "timestamp": "2026-02-21T12:00:00",
        "account_id": "account_main",
        "strategy_type": "top8_long",
        "enabled": true,
        "rsi_threshold": 800,
        "max_order_usdt": 5.0,
        "position_percent": 1.5,
        "leverage": 10
    }
}
```

#### 2. 获取配置API（第17114行开始）

**路由：** `GET /api/okx-trading/get-bottom-signal-config/<account_id>/<strategy_type>`

**响应：**
```json
{
    "success": true,
    "config": {
        "enabled": false,
        "rsi_threshold": 800,
        "max_order_usdt": 5.0,
        "position_percent": 1.5,
        "leverage": 10
    },
    "message": "使用默认配置（文件不存在）"
}
```

### 后端监控脚本
**文件：** `source_code/bottom_signal_long_monitor.py`

#### 主要功能

1. **配置加载**：
   ```python
   def load_strategy_config(account_id, strategy_type):
       """加载策略配置
       strategy_type: 'top8_long' 或 'bottom8_long'
       """
       config_file = CONFIG_DIR / f"{account_id}_bottom_signal_{strategy_type}.jsonl"
       
       default_config = {
           'enabled': False,
           'rsi_threshold': 800,
           'max_order_usdt': 5.0,
           'position_percent': 1.5,
           'leverage': 10
       }
       
       if not config_file.exists():
           return default_config
       
       with open(config_file, 'r', encoding='utf-8') as f:
           lines = f.readlines()
           if lines:
               return json.loads(lines[-1].strip())
       
       return default_config
   ```

2. **检查执行许可**：
   ```python
   def check_execution_allowed(account_id, strategy_type):
       """检查是否允许执行（1小时冷却）"""
       execution_file = EXECUTION_DIR / f"{account_id}_bottom_signal_{strategy_type}_execution.jsonl"
       
       if not execution_file.exists():
           return True, "首次执行"
       
       with open(execution_file, 'r', encoding='utf-8') as f:
           lines = f.readlines()
           if lines:
               last_record = json.loads(lines[0].strip())
               last_time = datetime.fromisoformat(last_record['timestamp'])
               
               if datetime.now() - last_time < timedelta(seconds=COOLDOWN_TIME):
                   return False, f"冷却中（距上次执行 {int((datetime.now() - last_time).total_seconds() / 60)} 分钟）"
       
       return True, "冷却结束"
   ```

3. **市场情绪检查**：
   ```python
   def get_market_sentiment():
       """获取市场情绪"""
       response = requests.get(f"{API_BASE}/api/market-sentiment/current", timeout=10)
       data = response.json()
       return {
           'sentiment': data.get('sentiment', ''),
           'rsi_sum': data.get('rsi_sum', 0),
           'is_bottom': data.get('sentiment') == '🎯见底信号'
       }
   ```

4. **执行做多策略**：
   ```python
   def execute_long_strategy(account, config, strategy_type, sentiment):
       """执行做多策略"""
       # 获取常用15币涨幅排行
       coins = get_top_15_coins()
       
       # 根据策略类型选择目标币种
       if strategy_type == 'top8_long':
           target_coins = coins[:8]  # 涨幅前8
       else:  # bottom8_long
           target_coins = coins[7:15]  # 涨幅后8
       
       # 计算仓位
       available_balance = get_available_balance(account)
       total_position = available_balance * config['position_percent'] / 100
       per_coin_amount = min(total_position / 8, config['max_order_usdt'])
       
       # 开多单
       for coin in target_coins:
           open_long_position(
               account=account,
               coin=coin,
               amount=per_coin_amount,
               leverage=config['leverage']
           )
       
       # 记录执行
       record_execution(account, strategy_type, sentiment)
       
       # 发送Telegram通知
       send_telegram_notification(account, strategy_type, target_coins, per_coin_amount)
   ```

5. **主循环**：
   ```python
   def main():
       """主循环"""
       log("🚀 见底信号做多监控器启动")
       
       while True:
           try:
               # 获取所有账户
               accounts = load_accounts()
               
               # 获取市场情绪
               sentiment = get_market_sentiment()
               
               for account in accounts:
                   # 检查两个策略
                   for strategy_type in ['top8_long', 'bottom8_long']:
                       config = load_strategy_config(account['id'], strategy_type)
                       
                       if not config['enabled']:
                           continue
                       
                       # 检查触发条件
                       if sentiment['is_bottom'] and sentiment['rsi_sum'] < config['rsi_threshold']:
                           allowed, reason = check_execution_allowed(account['id'], strategy_type)
                           
                           if allowed:
                               execute_long_strategy(account, config, strategy_type, sentiment)
                           else:
                               log(f"⏳ [{account['id']}/{strategy_type}] {reason}")
               
               time.sleep(CHECK_INTERVAL)
               
           except Exception as e:
               log(f"❌ 监控循环异常: {e}")
               time.sleep(10)
   ```

---

## 📁 数据文件结构

### JSONL配置文件
```
/home/user/webapp/data/okx_bottom_signal_strategies/
├── account_main_bottom_signal_top8_long.jsonl
├── account_main_bottom_signal_bottom8_long.jsonl
├── account_fangfang12_bottom_signal_top8_long.jsonl
├── account_fangfang12_bottom_signal_bottom8_long.jsonl
├── account_poit_main_bottom_signal_top8_long.jsonl
└── account_poit_main_bottom_signal_bottom8_long.jsonl
```

**配置文件格式：**
```jsonl
{"timestamp":"2026-02-21T12:00:00","time":"2026-02-21 12:00:00","account_id":"account_main","strategy_type":"top8_long","enabled":true,"rsi_threshold":800,"max_order_usdt":5.0,"position_percent":1.5,"leverage":10,"description":"见底信号+涨幅前8做多策略"}
```

### JSONL执行记录文件
```
/home/user/webapp/data/okx_bottom_signal_execution/
├── account_main_bottom_signal_top8_long_execution.jsonl
├── account_main_bottom_signal_bottom8_long_execution.jsonl
└── ...
```

**执行记录格式：**
```jsonl
{"timestamp":"2026-02-21T12:05:30","account_id":"account_main","strategy_type":"top8_long","executed":true,"rsi_value":750,"sentiment":"🎯见底信号","target_coins":["BTC-USDT-SWAP","ETH-USDT-SWAP","..."],"per_coin_amount":0.5,"total_amount":4.0,"leverage":10}
```

---

## 🎮 用户操作流程

### 1️⃣ 启用策略并配置参数

1. 访问 OKX交易页面
2. 找到黄色的"🚀 RSI自动开仓策略"卡片
3. 向下滚动找到绿色的"🎯 见底信号+涨幅前8/后8做多"策略
4. 设置参数：
   - **RSI阈值**：默认800，根据市场调整（300-1500）
   - **单币限额**：默认5 USDT，根据风险承受能力调整（1-100 USDT）
5. 点击**💾 保存**按钮保存配置
6. 打开策略开关

### 2️⃣ 策略自动运行

- 后端监控脚本每60秒检查市场条件
- 当满足条件时：
  - 出现见底信号（底部背离）
  - RSI总和 < 设定阈值（如800）
- 自动对目标币种开多单：
  - **策略1**：涨幅前8名币种
  - **策略2**：涨幅后8名币种
- **触发后1小时内不重复执行**

### 3️⃣ 查看执行结果

执行后会：
1. 记录到JSONL执行文件
2. 发送Telegram通知
3. 在1小时冷却期内不会重复触发

---

## 🔐 资金配置与风控

### 仓位计算公式

```
总投入 = 可用余额 × 1.5%
单币投入 = 总投入 ÷ 8
实际单币投入 = min(单币投入, 单币限额)
```

### 计算示例

#### 示例1：小账户（可用余额 200 USDT）
```
总投入 = 200 × 1.5% = 3.0 USDT
单币投入 = 3.0 ÷ 8 = 0.375 USDT
实际单币投入 = 0.375 USDT（未达到5 USDT限额）
8个币种总投入 = 0.375 × 8 = 3.0 USDT
```

#### 示例2：大账户（可用余额 5000 USDT）
```
总投入 = 5000 × 1.5% = 75 USDT
单币投入 = 75 ÷ 8 = 9.375 USDT
触发单币限额！实际单币投入 = 5.0 USDT
8个币种总投入 = 5.0 × 8 = 40 USDT
```

### 风控机制

- ✅ **仓位控制**：单次最多投入可用余额的1.5%
- ✅ **单币限额**：每个币种最多投入用户设定的限额（默认5 USDT）
- ✅ **杠杆固定**：10倍杠杆，平衡收益与风险
- ✅ **时间冷却**：触发后1小时内不重复，避免频繁交易
- ✅ **底部信号**：只在出现底部背离信号时触发
- ✅ **RSI确认**：只在RSI足够低时触发，避免假信号
- ✅ **多账户支持**：每个账户独立配置和执行

---

## 🆚 与见顶信号做空策略的对称设计

| 特性 | 见顶信号做空 ⚠️ | 见底信号做多 🎯 |
|------|----------------|----------------|
| **触发信号** | 见顶信号（顶部背离） | 见底信号（底部背离） |
| **RSI条件** | RSI > 1800（固定） | RSI < 800（可配置） |
| **交易方向** | 开空单 | 开多单 |
| **杠杆** | 10倍 | 10倍 |
| **目标币种** | 涨幅前8/后8 | 涨幅前8/后8 |
| **仓位配置** | 1.5% / 8 | 1.5% / 8 |
| **单币限额** | 5 USDT（固定） | 5 USDT（可配置） |
| **冷却时间** | 1小时 | 1小时 |
| **配置文件** | `okx_auto_strategy` | `okx_bottom_signal_strategies` |
| **执行记录** | `okx_auto_strategy` | `okx_bottom_signal_execution` |
| **监控脚本** | ❌ 未实现 | ✅ `bottom_signal_long_monitor.py` |
| **PM2服务** | ❌ 未运行 | ✅ `bottom-signal-long-monitor` |

---

## 📊 系统状态

### PM2服务状态
```bash
$ pm2 list | grep bottom
│ 28 │ bottom-signal-long-monitor │ online │ 0% │ 28.3mb │
```

### 数据文件状态
```bash
$ ls -lh data/okx_bottom_signal_strategies/
# 配置文件（每个账户每个策略一个文件）

$ ls -lh data/okx_bottom_signal_execution/
# 执行记录文件（每个账户每个策略一个文件）
```

### API状态
- ✅ `/api/okx-trading/save-bottom-signal-config/<account_id>/<strategy_type>` - 保存配置
- ✅ `/api/okx-trading/get-bottom-signal-config/<account_id>/<strategy_type>` - 获取配置
- ✅ 前端UI正常显示
- ✅ JavaScript函数正常工作
- ✅ 监控脚本正常运行

---

## 🚀 访问链接

**OKX交易系统：**
https://9002-iopxcqas7abbrajoi4k4x-2e77fc33.sandbox.novita.ai/okx-trading

**GitHub仓库：**
https://github.com/jamesyidc/25669889956

---

## ✅ 验证清单

- [x] 前端UI显示完整（两个策略卡片）
- [x] 开关按钮工作正常
- [x] RSI阈值输入框（300-1500，默认800）
- [x] 单币限额输入框（1-100 USDT，默认5）
- [x] 💾 保存按钮点击响应
- [x] 实时更新显示值（RSI阈值和单币限额）
- [x] JavaScript保存函数实现
- [x] JavaScript加载函数实现（集成在账户切换中）
- [x] 后端保存配置API实现
- [x] 后端获取配置API实现
- [x] JSONL配置文件格式正确
- [x] JSONL执行记录文件格式正确
- [x] 监控脚本完整实现
- [x] PM2服务正常运行
- [x] 多账户支持
- [x] 独立配置文件
- [x] 1小时冷却机制
- [x] Telegram通知集成
- [x] 错误处理完善
- [x] 参数验证完整

---

## 🎉 总结

**见底信号做多策略**已经完整实现并正常运行！

### 核心特点

1. 🎯 **对称设计**：与见顶信号做空策略完全对称
2. 🔧 **灵活配置**：RSI阈值和单币限额可独立设置
3. 📊 **多账户支持**：每个账户独立配置和执行
4. 🔐 **风控完善**：仓位控制、单币限额、冷却机制
5. 📝 **JSONL格式**：配置和执行记录清晰可追溯
6. 🤖 **自动执行**：后端监控脚本24/7运行
7. 📱 **Telegram通知**：实时推送执行结果
8. ✅ **完整验证**：所有组件已测试通过

### 使用建议

1. **初始配置**：
   - RSI阈值：800（可根据市场波动调整）
   - 单币限额：5 USDT（可根据风险承受能力调整）

2. **策略选择**：
   - **涨幅前8做多**：适合追涨反弹
   - **涨幅后8做多**：适合抄底补涨

3. **监控建议**：
   - 观察策略执行情况
   - 根据盈亏调整参数
   - 注意市场情绪变化

4. **风险提示**：
   - 10倍杠杆有较高风险
   - 单币限额控制单笔风险
   - 建议小额测试后再增加投入

---

**🎊 恭喜！见底信号做多策略功能已完美实现并运行正常！**
